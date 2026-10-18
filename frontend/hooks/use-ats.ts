import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { atsKeys, cvKeys } from "@/lib/query-keys";
import { atsApi } from "@/services/ats/ats.api";
import {
  ApplyATSSuggestionsRequest,
  ApplyATSSuggestionsResponse,
  ATSAnalysisRequest,
  ATSAnalysisResponse,
} from "@/types/ats";
import { ApiClientError } from "@/lib/api/errors";

export function useAtsAnalysis(
  versionId?: string,
  jobId?: string,
  options?: { enabled?: boolean }
) {
  return useQuery<ATSAnalysisResponse, ApiClientError>({
    queryKey: atsKeys.analysis(versionId, jobId),
    queryFn: () => atsApi.getCvAtsAnalysis(versionId!, jobId),
    enabled: Boolean(versionId) && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 3, // 3 minutes
  });
}

export function useRunAtsAnalysis() {
  const queryClient = useQueryClient();

  return useMutation<ATSAnalysisResponse, ApiClientError, ATSAnalysisRequest>({
    mutationFn: (payload) => atsApi.analyzeCvAts(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(
        atsKeys.analysis(data.cv_version_id, data.job_id || undefined),
        data
      );
    },
  });
}

export function useApplyAtsSuggestions() {
  const queryClient = useQueryClient();

  return useMutation<
    ApplyATSSuggestionsResponse,
    ApiClientError,
    ApplyATSSuggestionsRequest
  >({
    mutationFn: (payload) => atsApi.applyAtsSuggestions(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.invalidateQueries({ queryKey: atsKeys.all });
    },
  });
}
