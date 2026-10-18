import asyncio
import json
from typing import Any, Dict, List, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel

from app.ai.interface import AIProviderInterface
from app.core.config import get_settings
from app.core.exceptions import InternalServerError
from app.core.logging import get_logger

logger = get_logger("app.ai.gemini_provider")

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(AIProviderInterface):
    """
    Google Gemini provider implementing text generation, structured JSON generation, and embeddings.
    Uses direct HTTPS calls via httpx with header-based authentication and transient failure retries.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or getattr(settings, "gemini_api_key", None)
        self.model_name = model_name or getattr(settings, "gemini_model", "gemini-flash-latest")
        self.embedding_model = embedding_model or getattr(settings, "gemini_embedding_model", "gemini-embedding-001")
        self.timeout = timeout
        self.max_retries = max_retries

    def _get_headers(self) -> Dict[str, str]:
        """
        Build headers with authentication.
        Uses x-goog-api-key header to prevent credentials from leaking into URLs or proxy logs.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-goog-api-key"] = self.api_key
        return headers

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate unstructured plain text via Gemini API."""
        if not self.api_key:
            raise InternalServerError("Gemini API key is not configured in settings or environment.")

        # Clean URL without API key in query string
        url = f"{self.BASE_URL}/models/{self.model_name}:generateContent"

        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        response_json = await self._send_request(url, payload)

        try:
            candidates = response_json.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini generation.")
            parts = candidates[0].get("content", {}).get("parts", [])
            text_result = "".join(p.get("text", "") for p in parts)
            return text_result.strip()
        except Exception as e:
            logger.error(f"Failed to parse Gemini text response: {e}")
            raise InternalServerError(f"Gemini response parsing error: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured JSON response adhering strictly to the provided Pydantic schema."""
        if not self.api_key:
            raise InternalServerError("Gemini API key is not configured in settings or environment.")

        # Clean URL without API key in query string
        url = f"{self.BASE_URL}/models/{self.model_name}:generateContent"

        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        if hasattr(schema, "model_json_schema"):
            payload["generationConfig"]["responseSchema"] = schema.model_json_schema()

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        response_json = await self._send_request(url, payload)

        try:
            candidates = response_json.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini structured generation.")
            parts = candidates[0].get("content", {}).get("parts", [])
            raw_text = "".join(p.get("text", "") for p in parts).strip()
            parsed_data = json.loads(raw_text)
            return schema.model_validate(parsed_data)
        except Exception as e:
            logger.error(f"Failed to validate Gemini structured output against {schema.__name__}: {e}")
            raise InternalServerError(f"Failed to validate Gemini structured output against {schema.__name__}: {e}")

    async def compute_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """Compute vector embeddings via Gemini batchEmbedContents API."""
        if not self.api_key:
            raise InternalServerError("Gemini API key is not configured in settings or environment.")

        # Clean URL without API key in query string
        url = f"{self.BASE_URL}/models/{self.embedding_model}:batchEmbedContents"

        requests = [
            {
                "model": f"models/{self.embedding_model}",
                "content": {"parts": [{"text": t}]},
            }
            for t in texts
        ]

        payload = {"requests": requests}
        response_json = await self._send_request(url, payload)

        try:
            embeddings_data = response_json.get("embeddings", [])
            return [e.get("values", []) for e in embeddings_data]
        except Exception as e:
            logger.error(f"Failed to parse Gemini embeddings response: {e}")
            raise InternalServerError(f"Failed to parse embeddings: {e}")

    async def _send_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send HTTP POST request with bounded retries for transient errors.
        - Retries on HTTP 429 (rate limits) and HTTP 5xx (server errors).
        - Retries on network timeouts and disconnects.
        - Never retries non-transient HTTP 400, 401, 403, or 404 client errors.
        - Never logs API keys or sensitive payload fragments.
        """
        headers = self._get_headers()
        last_network_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, headers=headers, json=payload)

                    if resp.status_code == 200:
                        return resp.json()

                    elif resp.status_code == 429:
                        wait_time = min(2.0 ** attempt, 10.0)
                        logger.warning(
                            f"Gemini rate limit reached (429), retrying in {wait_time:.1f}s "
                            f"(attempt {attempt}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    elif resp.status_code >= 500:
                        wait_time = min(1.5 ** attempt, 8.0)
                        logger.warning(
                            f"Gemini server error ({resp.status_code}), retrying in {wait_time:.1f}s "
                            f"(attempt {attempt}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    else:
                        # Non-retryable client errors (400, 401, 403, 404, etc.)
                        resp_text = resp.text
                        err_msg = resp_text
                        try:
                            err_json = resp.json()
                            if "error" in err_json and "message" in err_json["error"]:
                                err_msg = err_json["error"]["message"]
                        except Exception:
                            pass

                        logger.error(f"Gemini request failed with status {resp.status_code}: {err_msg}")
                        raise InternalServerError(f"Gemini API returned status {resp.status_code}: {err_msg}")

            except (httpx.TimeoutException, httpx.NetworkError) as net_err:
                last_network_error = net_err
                wait_time = 1.0 * attempt
                logger.warning(
                    f"Gemini network {type(net_err).__name__}, retrying in {wait_time:.1f}s "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                if attempt == self.max_retries:
                    raise InternalServerError(
                        f"Failed to communicate with Gemini API after {self.max_retries} attempts: {net_err}"
                    )
                await asyncio.sleep(wait_time)

        raise InternalServerError(f"Gemini API failed after {self.max_retries} attempts: {last_network_error}")
