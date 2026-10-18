import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { coverLetterKeys } from "@/lib/query-keys";
import { coverLetterApi, CoverLetterFilters } from "@/services/cover-letter";
import {
  CoverLetterListResponse,
  CoverLetterResponse,
  GenerateCoverLetterRequest,
  RegenerateCoverLetterRequest,
  UpdateCoverLetterRequest,
} from "@/types/cover-letter";
import { ApiClientError } from "@/lib/api/errors";

export function useCoverLetterList(filters?: CoverLetterFilters) {
  return useQuery<CoverLetterListResponse, ApiClientError>({
    queryKey: coverLetterKeys.list(filters),
    queryFn: () => coverLetterApi.listCoverLetters(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useCoverLetterDetail(id?: string) {
  return useQuery<CoverLetterResponse, ApiClientError>({
    queryKey: coverLetterKeys.detail(id || ""),
    queryFn: () => coverLetterApi.getCoverLetter(id!),
    enabled: Boolean(id),
    staleTime: 1000 * 60 * 5,
  });
}

export function useGenerateCoverLetter() {
  const queryClient = useQueryClient();

  return useMutation<CoverLetterResponse, ApiClientError, GenerateCoverLetterRequest>({
    mutationFn: (payload) => coverLetterApi.generateCoverLetter(payload),
    onSuccess: (newLetter) => {
      queryClient.invalidateQueries({ queryKey: coverLetterKeys.all });
      queryClient.setQueryData(coverLetterKeys.detail(newLetter.id), newLetter);
    },
  });
}

export function useUpdateCoverLetter() {
  const queryClient = useQueryClient();

  return useMutation<
    CoverLetterResponse,
    ApiClientError,
    { id: string; payload: UpdateCoverLetterRequest }
  >({
    mutationFn: ({ id, payload }) => coverLetterApi.updateCoverLetter(id, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: coverLetterKeys.all });
      queryClient.setQueryData(coverLetterKeys.detail(updated.id), updated);
    },
  });
}

export function useRegenerateCoverLetter() {
  const queryClient = useQueryClient();

  return useMutation<
    CoverLetterResponse,
    ApiClientError,
    { id: string; payload: RegenerateCoverLetterRequest }
  >({
    mutationFn: ({ id, payload }) => coverLetterApi.regenerateCoverLetter(id, payload),
    onSuccess: (updatedOrNew) => {
      queryClient.invalidateQueries({ queryKey: coverLetterKeys.all });
      queryClient.setQueryData(coverLetterKeys.detail(updatedOrNew.id), updatedOrNew);
    },
  });
}

export function useDuplicateCoverLetter() {
  const queryClient = useQueryClient();

  return useMutation<
    CoverLetterResponse,
    ApiClientError,
    { id: string; payload?: { new_name?: string } }
  >({
    mutationFn: ({ id, payload }) => coverLetterApi.duplicateCoverLetter(id, payload),
    onSuccess: (duplicated) => {
      queryClient.invalidateQueries({ queryKey: coverLetterKeys.all });
      queryClient.setQueryData(coverLetterKeys.detail(duplicated.id), duplicated);
    },
  });
}

export function useDeleteCoverLetter() {
  const queryClient = useQueryClient();

  return useMutation<void, ApiClientError, string>({
    mutationFn: (id) => coverLetterApi.deleteCoverLetter(id),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: coverLetterKeys.all });
      queryClient.removeQueries({ queryKey: coverLetterKeys.detail(deletedId) });
    },
  });
}

export function useExportCoverLetterPdf() {
  return useMutation<{ blob: Blob; filename: string }, ApiClientError, string>({
    mutationFn: (id) => coverLetterApi.exportPdf(id),
    onSuccess: ({ blob, filename }) => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    },
  });
}

export function useExportCoverLetterDocx() {
  return useMutation<{ blob: Blob; filename: string }, ApiClientError, string>({
    mutationFn: (id) => coverLetterApi.exportDocx(id),
    onSuccess: ({ blob, filename }) => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    },
  });
}
