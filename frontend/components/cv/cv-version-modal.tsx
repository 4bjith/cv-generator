"use client";

import { useEffect, useState } from "react";
import { Button, Field, Modal, SelectField } from "@/components/ui";
import { CVVersion, CVVersionCreate, CVVersionStatus, CVVersionUpdate } from "@/types/cv";
import { useCreateCvVersion, useUpdateCvVersion } from "@/hooks/use-cv";
import { useJobList } from "@/hooks/use-jobs";
import { Sparkle } from "@phosphor-icons/react";

interface CVVersionModalProps {
  open: boolean;
  onClose: () => void;
  versionToEdit?: CVVersion | null;
  initialJobTargetId?: string;
  initialName?: string;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  onSuccess?: (created: CVVersion) => void;
}

export function CVVersionModal({
  open,
  onClose,
  versionToEdit,
  initialJobTargetId,
  initialName,
  onToast,
  onSuccess,
}: CVVersionModalProps) {
  const isEditing = Boolean(versionToEdit);
  const createMutation = useCreateCvVersion();
  const updateMutation = useUpdateCvVersion();

  // Load saved job targets to offer linking
  const { data: jobData } = useJobList({ limit: 100 });

  const [name, setName] = useState("");
  const [jobTargetId, setJobTargetId] = useState<string>("");
  const [status, setStatus] = useState<CVVersionStatus>("draft");
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (versionToEdit) {
      setName(versionToEdit.name || "");
      setJobTargetId(versionToEdit.job_target_id || "");
      setStatus(versionToEdit.status || "draft");
    } else {
      setName(initialName || "");
      setJobTargetId(initialJobTargetId || "");
      setStatus("draft");
    }
    setErrors({});
  }, [versionToEdit, initialName, initialJobTargetId, open]);

  const validate = (): boolean => {
    const nextErrors: Record<string, string> = {};

    if (!name.trim()) {
      nextErrors.name = "CV version name is required.";
    } else if (name.trim().length > 200) {
      nextErrors.name = "Version name cannot exceed 200 characters.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      if (isEditing && versionToEdit) {
        const payload: CVVersionUpdate = {
          name: name.trim(),
          job_target_id: jobTargetId ? jobTargetId : null,
          status,
        };
        await updateMutation.mutateAsync({ id: versionToEdit.id, payload });
        onToast("CV Version Updated", `"${name.trim()}" has been updated successfully.`, "success");
      } else {
        const payload: CVVersionCreate = {
          name: name.trim(),
          job_target_id: jobTargetId ? jobTargetId : null,
        };
        const created = await createMutation.mutateAsync(payload);
        onToast("CV Version Created", `Created snapshot for "${name.trim()}".`, "success");
        if (onSuccess) {
          onSuccess(created);
        }
      }
      onClose();
    } catch (err: any) {
      const errMsg = err?.message || "Failed to save CV version.";
      onToast("Operation Failed", errMsg, "error");
    }
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEditing ? "Edit CV Version Metadata" : "Create New CV Version"}
      description={
        isEditing
          ? "Update the version title, lifecycle status, or linked job opportunity."
          : "Create an independently persisted CV snapshot derived from your current Candidate Profile."
      }
    >
      <form onSubmit={handleSubmit} className="job-form" noValidate>
        <Field
          label="CV Version Name"
          required
          placeholder="e.g. Senior Full-Stack Engineer - Stripe"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            if (errors.name) setErrors((prev) => ({ ...prev, name: "" }));
          }}
          error={errors.name}
          autoFocus
        />

        <SelectField
          label="Link Target Job Opportunity (Optional)"
          value={jobTargetId}
          onChange={(e) => setJobTargetId(e.target.value)}
        >
          <option value="">None (General Profile Version)</option>
          {(jobData?.items || []).map((j) => (
            <option key={j.id} value={j.id}>
              {j.company_name} — {j.title}
            </option>
          ))}
        </SelectField>

        {isEditing && (
          <SelectField
            label="Version Status"
            value={status}
            onChange={(e) => setStatus(e.target.value as CVVersionStatus)}
          >
            <option value="draft">Draft (In Progress)</option>
            <option value="ready">Ready (Finalized Snapshot)</option>
            <option value="archived">Archived (Historical)</option>
          </SelectField>
        )}

        {!isEditing && (
          <div
            style={{
              padding: "0.85rem 1rem",
              background: "rgba(99, 102, 241, 0.08)",
              border: "1px solid rgba(99, 102, 241, 0.2)",
              borderRadius: "8px",
              fontSize: "0.82rem",
              color: "var(--color-text-secondary)",
              display: "flex",
              alignItems: "flex-start",
              gap: "0.6rem",
              marginTop: "0.25rem",
            }}
          >
            <Sparkle size={18} weight="fill" style={{ color: "var(--color-primary-500)", flexShrink: 0, marginTop: "2px" }} />
            <div>
              <strong style={{ color: "var(--color-text-primary)", display: "block" }}>Point-in-Time Snapshot Isolation</strong>
              Creating a version takes a snapshot of your Master Profile. Modifying your master profile in the future will not overwrite this version.
            </div>
          </div>
        )}

        <div className="modal-actions" style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "1.25rem" }}>
          <Button variant="ghost" type="button" onClick={onClose} disabled={isSaving}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" disabled={isSaving}>
            {isSaving ? "Saving..." : isEditing ? "Save Changes" : "Create Version Snapshot"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
