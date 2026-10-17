"use client";

import { useEffect, useState } from "react";
import { Button, Field, Modal, SelectField, TextareaField } from "@/components/ui";
import { JobTarget, JobTargetCreate, JobTargetStatus, JobTargetUpdate } from "@/types/job";
import { useCreateJob, useUpdateJob } from "@/hooks/use-jobs";
import { Sparkle } from "@phosphor-icons/react";

interface JobTargetModalProps {
  open: boolean;
  onClose: () => void;
  jobToEdit?: JobTarget | null;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function JobTargetModal({ open, onClose, jobToEdit, onToast }: JobTargetModalProps) {
  const isEditing = Boolean(jobToEdit);
  const createMutation = useCreateJob();
  const updateMutation = useUpdateJob();

  const [title, setTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [status, setStatus] = useState<JobTargetStatus>("saved");
  const [jobDescription, setJobDescription] = useState("");
  const [userNotes, setUserNotes] = useState("");

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (jobToEdit) {
      setTitle(jobToEdit.title || "");
      setCompanyName(jobToEdit.company_name || "");
      setLocation(jobToEdit.location || "");
      setEmploymentType(jobToEdit.employment_type || "");
      setSourceUrl(jobToEdit.source_url || "");
      setStatus(jobToEdit.status || "saved");
      setJobDescription(jobToEdit.job_description || "");
      setUserNotes(jobToEdit.user_notes || "");
    } else {
      setTitle("");
      setCompanyName("");
      setLocation("");
      setEmploymentType("");
      setSourceUrl("");
      setStatus("saved");
      setJobDescription("");
      setUserNotes("");
    }
    setErrors({});
  }, [jobToEdit, open]);

  const validate = (): boolean => {
    const nextErrors: Record<string, string> = {};

    if (!title.trim()) {
      nextErrors.title = "Job title is required.";
    } else if (title.trim().length > 200) {
      nextErrors.title = "Job title cannot exceed 200 characters.";
    }

    if (!companyName.trim()) {
      nextErrors.companyName = "Company name is required.";
    } else if (companyName.trim().length > 200) {
      nextErrors.companyName = "Company name cannot exceed 200 characters.";
    }

    if (location.trim().length > 200) {
      nextErrors.location = "Location cannot exceed 200 characters.";
    }

    if (!jobDescription.trim()) {
      nextErrors.jobDescription = "Job description is required.";
    } else if (jobDescription.trim().length > 50000) {
      nextErrors.jobDescription = "Job description is too long (max 50,000 characters).";
    }

    if (sourceUrl.trim()) {
      const url = sourceUrl.trim();
      if (!url.startsWith("http://") && !url.startsWith("https://")) {
        nextErrors.sourceUrl = "URL must start with http:// or https://";
      } else if (url.length > 500) {
        nextErrors.sourceUrl = "URL cannot exceed 500 characters.";
      }
    }

    if (userNotes.trim().length > 10000) {
      nextErrors.userNotes = "Notes cannot exceed 10,000 characters.";
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      if (isEditing && jobToEdit) {
        const payload: JobTargetUpdate = {
          title: title.trim(),
          company_name: companyName.trim(),
          location: location.trim() || null,
          employment_type: employmentType.trim() || null,
          source_url: sourceUrl.trim() || null,
          status,
          job_description: jobDescription.trim(),
          user_notes: userNotes.trim() || null,
        };
        await updateMutation.mutateAsync({ id: jobToEdit.id, payload });
        onToast("Job Target Updated", `${title.trim()} at ${companyName.trim()} was updated.`, "success");
      } else {
        const payload: JobTargetCreate = {
          title: title.trim(),
          company_name: companyName.trim(),
          location: location.trim() || undefined,
          employment_type: employmentType.trim() || undefined,
          source_url: sourceUrl.trim() || undefined,
          status,
          job_description: jobDescription.trim(),
          user_notes: userNotes.trim() || undefined,
        };
        await createMutation.mutateAsync(payload);
        onToast("Job Target Created", `${title.trim()} at ${companyName.trim()} is now saved.`, "success");
      }
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save job target. Please check your inputs.";
      onToast("Save Failed", msg, "error");
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEditing ? "Edit Job Target" : "Add Target Job Opportunity"}
      description={
        isEditing
          ? "Update details, status, or personal notes for this opportunity."
          : "Save a job opening into your workspace for evidence matching and tailored applications."
      }
      footer={
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", width: "100%" }}>
          <Button variant="ghost" type="button" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant="primary"
            type="submit"
            form="job-target-form"
            loading={isSubmitting}
            icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
          >
            {isEditing ? "Save Changes" : "Save Job Target"}
          </Button>
        </div>
      }
    >
      <form id="job-target-form" onSubmit={handleSubmit} className="profile-form-grid" noValidate>
        <Field
          label="Job Title *"
          name="job-title"
          placeholder="e.g. Senior Frontend Engineer"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          error={errors.title}
          autoFocus
          required
        />

        <Field
          label="Company Name *"
          name="job-company"
          placeholder="e.g. Stripe, Lattice, Vercel"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          error={errors.companyName}
          required
        />

        <Field
          label="Location"
          name="job-location"
          placeholder="e.g. San Francisco, CA (Hybrid) or Remote"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          error={errors.location}
          hint="City, state, country or remote classification"
        />

        <SelectField
          label="Employment Type"
          name="job-employment-type"
          value={employmentType}
          onChange={(e) => setEmploymentType(e.target.value)}
          hint="Full-time, contract, part-time, remote, etc."
        >
          <option value="">Unspecified</option>
          <option value="Full-time">Full-time</option>
          <option value="Contract">Contract</option>
          <option value="Part-time">Part-time</option>
          <option value="Internship">Internship</option>
          <option value="Remote">Remote</option>
          <option value="Hybrid">Hybrid</option>
        </SelectField>

        <Field
          label="Job Listing URL"
          name="job-source-url"
          type="url"
          placeholder="https://company.com/careers/job-id"
          value={sourceUrl}
          onChange={(e) => setSourceUrl(e.target.value)}
          error={errors.sourceUrl}
          hint="Link to the original public listing"
        />

        {isEditing ? (
          <SelectField
            label="Lifecycle Status"
            name="job-status"
            value={status}
            onChange={(e) => setStatus(e.target.value as JobTargetStatus)}
          >
            <option value="saved">Active / Saved</option>
            <option value="archived">Archived</option>
          </SelectField>
        ) : null}

        <div style={{ gridColumn: "1 / -1" }}>
          <TextareaField
            label="Job Description *"
            name="job-description-text"
            rows={10}
            placeholder="Paste the full job description text including responsibilities, requirements, and qualifications..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            error={errors.jobDescription}
            hint="The complete description used for evidence comparison and tailoring"
            required
          />
        </div>

        <div style={{ gridColumn: "1 / -1" }}>
          <TextareaField
            label="Private Notes"
            name="job-user-notes"
            rows={3}
            placeholder="Referral contacts, salary expectations, application deadlines, interview reminders..."
            value={userNotes}
            onChange={(e) => setUserNotes(e.target.value)}
            error={errors.userNotes}
            hint="Private notes only visible to you"
          />
        </div>
      </form>
    </Modal>
  );
}
