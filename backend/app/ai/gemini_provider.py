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
    Uses direct HTTPS calls via httpx with exponential backoff and retry handling.
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
        self.model_name = model_name or getattr(settings, "gemini_model", "gemini-1.5-flash")
        self.embedding_model = embedding_model or getattr(settings, "gemini_embedding_model", "text-embedding-004")
        self.timeout = timeout
        self.max_retries = max_retries

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
        }

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

        url = f"{self.BASE_URL}/models/{self.model_name}:generateContent?key={self.api_key}"

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
            logger.error("Failed to parse Gemini text response", error=str(e), response=response_json)
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

        url = f"{self.BASE_URL}/models/{self.model_name}:generateContent?key={self.api_key}"

        # Request application/json mime type
        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        # If schema has model_json_schema, pass it
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
            logger.error("Failed to validate Gemini structured output", error=str(e), response=response_json)
            raise InternalServerError(f"Failed to validate Gemini structured output against {schema.__name__}: {e}")

    async def compute_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """Compute vector embeddings via Gemini batchEmbedContents API."""
        if not self.api_key:
            raise InternalServerError("Gemini API key is not configured in settings or environment.")

        url = f"{self.BASE_URL}/models/{self.embedding_model}:batchEmbedContents?key={self.api_key}"

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
            logger.error("Failed to parse Gemini embeddings response", error=str(e))
            raise InternalServerError(f"Failed to parse embeddings: {e}")

    async def _send_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send HTTP POST request with retry and backoff."""
        headers = self._get_headers()
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 429:
                        wait_time = 2.0 ** attempt
                        logger.warning("Gemini rate limit reached (429), retrying", attempt=attempt, wait_time=wait_time)
                        await asyncio.sleep(wait_time)
                        continue
                    elif resp.status_code >= 500:
                        wait_time = 1.5 ** attempt
                        logger.warning("Gemini server error, retrying", status_code=resp.status_code, attempt=attempt)
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        resp_text = resp.text
                        logger.error("Gemini request failed", status_code=resp.status_code, body=resp_text)
                        raise InternalServerError(f"Gemini API returned status {resp.status_code}: {resp_text}")
            except httpx.TimeoutException as te:
                last_error = te
                logger.warning("Gemini request timed out, retrying", attempt=attempt)
                await asyncio.sleep(1.0 * attempt)
            except Exception as exc:
                last_error = exc
                if attempt == self.max_retries:
                    raise InternalServerError(f"Failed to communicate with Gemini API: {exc}")
                await asyncio.sleep(1.0 * attempt)

        raise InternalServerError(f"Gemini API failed after {self.max_retries} attempts: {last_error}")
