import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cvKeys } from "@/lib/query-keys";
import { cvApi } from "@/services/cv/cv.api";
import {
  CVVersion,
  CVVersionCreate,
  CVVersionDuplicate,
  CVVersionFilters,
  CVVersionListResponse,
  CVVersionUpdate,
} from "@/types/cv";
import { ApiClientError } from "@/lib/api/errors";

export function useCvList(filters?: CVVersionFilters) {
  return useQuery<CVVersionListResponse, ApiClientError>({
    queryKey: cvKeys.list(filters),
    queryFn: () => cvApi.listVersions(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useCvDetail(id?: string) {
  return useQuery<CVVersion, ApiClientError>({
    queryKey: cvKeys.detail(id || ""),
    queryFn: () => cvApi.getVersion(id!),
    enabled: Boolean(id),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateCvVersion() {
  const queryClient = useQueryClient();

  return useMutation<CVVersion, ApiClientError, CVVersionCreate>({
    mutationFn: (payload) => cvApi.createVersion(payload),
    onSuccess: (newVersion) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.setQueryData(cvKeys.detail(newVersion.id), newVersion);
    },
  });
}

export function useUpdateCvVersion() {
  const queryClient = useQueryClient();

  return useMutation<CVVersion, ApiClientError, { id: string; payload: CVVersionUpdate }>({
    mutationFn: ({ id, payload }) => cvApi.updateVersion(id, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.setQueryData(cvKeys.detail(updated.id), updated);
    },
  });
}

export function useDuplicateCvVersion() {
  const queryClient = useQueryClient();

  return useMutation<CVVersion, ApiClientError, { id: string; payload?: CVVersionDuplicate }>({
    mutationFn: ({ id, payload }) => cvApi.duplicateVersion(id, payload),
    onSuccess: (newVersion) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.setQueryData(cvKeys.detail(newVersion.id), newVersion);
    },
  });
}

export function useArchiveCvVersion() {
  const queryClient = useQueryClient();

  return useMutation<CVVersion, ApiClientError, string>({
    mutationFn: (id) => cvApi.archiveVersion(id),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.setQueryData(cvKeys.detail(updated.id), updated);
    },
  });
}

export function useRestoreCvVersion() {
  const queryClient = useQueryClient();

  return useMutation<CVVersion, ApiClientError, string>({
    mutationFn: (id) => cvApi.restoreVersion(id),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.setQueryData(cvKeys.detail(updated.id), updated);
    },
  });
}

export function useDeleteCvVersion() {
  const queryClient = useQueryClient();

  return useMutation<void, ApiClientError, string>({
    mutationFn: (id) => cvApi.deleteVersion(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: cvKeys.all });
      queryClient.removeQueries({ queryKey: cvKeys.detail(id) });
    },
  });
}

export function useExportJsonResume(id?: string, applyVisibility = false) {
  return useQuery<Record<string, any>, ApiClientError>({
    queryKey: [...cvKeys.detail(id || ""), "json-resume", applyVisibility],
    queryFn: () => cvApi.exportJsonResume(id!, applyVisibility),
    enabled: Boolean(id),
  });
}

export function useExportPdf() {
  return useMutation<{ blob: Blob; filename: string }, ApiClientError, { id: string; overrides?: Record<string, string> }>({
    mutationFn: ({ id, overrides }) => cvApi.exportPdf(id, overrides),
    onSuccess: ({ blob, filename }) => {
      if (typeof window !== "undefined") {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    },
  });
}

export function useExportDocx() {
  return useMutation<{ blob: Blob; filename: string }, ApiClientError, { id: string; overrides?: Record<string, string> }>({
    mutationFn: ({ id, overrides }) => cvApi.exportDocx(id, overrides),
    onSuccess: ({ blob, filename }) => {
      if (typeof window !== "undefined") {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    },
  });
}
