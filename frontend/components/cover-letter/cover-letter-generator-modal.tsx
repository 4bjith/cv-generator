"use client";

import { useEffect, useState } from "react";
import { Briefcase, FileText, Info, ShieldCheck, Sparkle, Target, WarningCircle } from "@phosphor-icons/react";
import { Badge, Button, Modal } from "@/components/ui";
import { useCvList } from "@/hooks/use-cv";
import { useJobList } from "@/hooks/use-jobs";
import {
  CoverLetterLength,
  CoverLetterTone,
  GenerateCoverLetterRequest,
} from "@/types/cover-letter";

interface CoverLetterGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (payload: GenerateCoverLetterRequest) => Promise<void>;
  isLoading: boolean;
  initialJobId?: string;
  initialCvVersionId?: string;
}

const TONES: { id: CoverLetterTone; label: string; desc: string }[] = [
  { id: "professional", label: "Professional", desc: "Balanced, confident, industry-standard tone" },
  { id: "concise", label: "Concise", desc: "High-impact, direct, efficient communication" },
  { id: "technical", label: "Technical", desc: "Architecture, engineering, and methodology focus" },
  { id: "formal", label: "Formal", desc: "Traditional, executive, reverent phrasing" },
];

const LENGTHS: { id: CoverLetterLength; label: string; desc: string }[] = [
  { id: "short", label: "Short", desc: "~200 words, high impact" },
  { id: "standard", label: "Standard", desc: "~350 words, balanced" },
  { id: "detailed", label: "Detailed", desc: "~500 words, rich context" },
];

export function CoverLetterGeneratorModal({
  isOpen,
  onClose,
  onGenerate,
  isLoading,
  initialJobId,
  initialCvVersionId,
}: CoverLetterGeneratorModalProps) {
  // Fetch available jobs and CV versions
  const { data: jobsData, isLoading: isJobsLoading } = useJobList();
  const { data: cvData, isLoading: isCvLoading } = useCvList();

  const jobs = jobsData?.items || [];
  const cvVersions = cvData?.items || [];

  const [jobId, setJobId] = useState<string>(initialJobId || "");
  const [cvVersionId, setCvVersionId] = useState<string>(initialCvVersionId || "");
  const [letterName, setLetterName] = useState<string>("");
  const [tone, setTone] = useState<CoverLetterTone>("professional");
  const [lengthOption, setLengthOption] = useState<CoverLetterLength>("standard");
  const [instructions, setInstructions] = useState<string>("");

  // Recipient details
  const [recipientName, setRecipientName] = useState<string>("");
  const [recipientTitle, setRecipientTitle] = useState<string>("");
  const [recipientCompany, setRecipientCompany] = useState<string>("");
  const [recipientAddress, setRecipientAddress] = useState<string>("");
  const [showRecipientDetails, setShowRecipientDetails] = useState<boolean>(false);

  // Set default job if available
  useEffect(() => {
    if (!jobId && jobs.length > 0) {
      setJobId(jobs[0].id);
    }
  }, [jobs, jobId]);

  // Auto-fill company and suggested letter name when job changes
  useEffect(() => {
    if (jobId) {
      const selectedJob = jobs.find((j) => j.id === jobId);
      if (selectedJob) {
        if (!recipientCompany) {
          setRecipientCompany(selectedJob.company_name || "");
        }
        if (!letterName) {
          setLetterName(`Cover Letter - ${selectedJob.title || "Target Role"} at ${selectedJob.company_name || "Company"}`);
        }
      }
    }
  }, [jobId, jobs]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId) return;

    await onGenerate({
      job_id: jobId,
      cv_version_id: cvVersionId || null,
      name: letterName.trim() || null,
      tone,
      length_option: lengthOption,
      additional_instructions: instructions.trim() || null,
      recipient_name: recipientName.trim() || null,
      recipient_title: recipientTitle.trim() || null,
      recipient_company: recipientCompany.trim() || null,
      recipient_address: recipientAddress.trim() || null,
    });
  };

  const selectedJob = jobs.find((j) => j.id === jobId);

  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      title="Generate Evidence-Grounded Cover Letter"
    >
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Grounding banner */}
        <div style={{
          padding: "0.875rem 1rem",
          borderRadius: "var(--radius)",
          background: "rgba(16, 185, 129, 0.08)",
          border: "1px solid rgba(16, 185, 129, 0.25)",
          display: "flex",
          gap: "0.75rem",
          alignItems: "flex-start",
        }}>
          <ShieldCheck size={20} weight="fill" style={{ color: "#059669", flexShrink: 0, marginTop: "2px" }} />
          <div>
            <div style={{ fontWeight: 600, fontSize: "0.875rem", color: "#065f46" }}>
              Zero-Hallucination Policy
            </div>
            <div style={{ fontSize: "0.775rem", color: "#047857", marginTop: "2px", lineHeight: 1.4 }}>
              Every qualification, date, employer, and metric is verified against your master Candidate Profile and confirmed clarifications. Any job requirement lacking evidence will be flagged in the truth audit rather than fabricated.
            </div>
          </div>
        </div>

        {/* Saved Job Target Selector */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Target Job <span style={{ color: "var(--accent)" }}>*</span>
          </label>
          {isJobsLoading ? (
            <div style={{ padding: "0.5rem", fontSize: "0.875rem", color: "var(--muted)" }}>Loading saved jobs...</div>
          ) : jobs.length === 0 ? (
            <div style={{
              padding: "0.75rem",
              borderRadius: "var(--radius)",
              background: "rgba(239, 68, 68, 0.06)",
              border: "1px solid rgba(239, 68, 68, 0.2)",
              fontSize: "0.875rem",
              color: "#991b1b",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}>
              <WarningCircle size={18} />
              <span>No saved jobs found. Please create or save a job target first to ground your cover letter.</span>
            </div>
          ) : (
            <select
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.625rem 0.75rem",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
                background: "var(--card)",
                fontSize: "0.875rem",
                fontFamily: "inherit",
              }}
            >
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} {j.company_name ? `at ${j.company_name}` : ""}
                </option>
              ))}
            </select>
          )}

          {selectedJob && (
            <div style={{ marginTop: "0.35rem", display: "flex", gap: "0.5rem", alignItems: "center", fontSize: "0.75rem", color: "var(--muted)" }}>
              <span>Target: <strong>{selectedJob.title}</strong></span>
              {selectedJob.company_name && <span>• <strong>{selectedJob.company_name}</strong></span>}
            </div>
          )}
        </div>

        {/* Optional CV Version Snapshot */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Contextual CV Version (Optional)
          </label>
          <select
            value={cvVersionId}
            onChange={(e) => setCvVersionId(e.target.value)}
            style={{
              width: "100%",
              padding: "0.625rem 0.75rem",
              borderRadius: "var(--radius)",
              border: "1px solid var(--border)",
              background: "var(--card)",
              fontSize: "0.875rem",
              fontFamily: "inherit",
            }}
          >
            <option value="">No CV Snapshot (Use Master Candidate Profile)</option>
            {cvVersions.map((cv) => (
              <option key={cv.id} value={cv.id}>
                {cv.name} ({cv.status})
              </option>
            ))}
          </select>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.25rem" }}>
            If selected, the generator aligns your narrative with this tailored snapshot while keeping the letter completely independent.
          </div>
        </div>

        {/* Tone Selector */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Tone & Style
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.5rem" }}>
            {TONES.map((t) => (
              <button
                type="button"
                key={t.id}
                onClick={() => setTone(t.id)}
                style={{
                  padding: "0.625rem 0.75rem",
                  borderRadius: "var(--radius)",
                  border: tone === t.id ? "2px solid var(--accent)" : "1px solid var(--border)",
                  background: tone === t.id ? "rgba(37, 99, 235, 0.05)" : "var(--card)",
                  textAlign: "left",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontWeight: 600, fontSize: "0.875rem", color: tone === t.id ? "var(--accent)" : "inherit" }}>
                  {t.label}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.15rem" }}>
                  {t.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Length Selector */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Length
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.5rem" }}>
            {LENGTHS.map((l) => (
              <button
                type="button"
                key={l.id}
                onClick={() => setLengthOption(l.id)}
                style={{
                  padding: "0.625rem 0.75rem",
                  borderRadius: "var(--radius)",
                  border: lengthOption === l.id ? "2px solid var(--accent)" : "1px solid var(--border)",
                  background: lengthOption === l.id ? "rgba(37, 99, 235, 0.05)" : "var(--card)",
                  textAlign: "left",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontWeight: 600, fontSize: "0.875rem", color: lengthOption === l.id ? "var(--accent)" : "inherit" }}>
                  {l.label}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.15rem" }}>
                  {l.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Recipient Details Toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowRecipientDetails(!showRecipientDetails)}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent)",
              fontSize: "0.875rem",
              fontWeight: 500,
              cursor: "pointer",
              padding: 0,
              display: "flex",
              alignItems: "center",
              gap: "0.25rem",
            }}
          >
            <span>{showRecipientDetails ? "▼ Hide recipient details" : "▶ Customize recipient details"}</span>
          </button>

          {showRecipientDetails && (
            <div style={{
              marginTop: "0.75rem",
              padding: "0.875rem",
              borderRadius: "var(--radius)",
              background: "var(--background)",
              border: "1px solid var(--border)",
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: "0.75rem",
            }}>
              <div>
                <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                  Recipient Name
                </label>
                <input
                  type="text"
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                  placeholder="e.g. Jane Doe or Hiring Committee"
                  style={{
                    width: "100%",
                    padding: "0.45rem 0.65rem",
                    fontSize: "0.825rem",
                    borderRadius: "var(--radius)",
                    border: "1px solid var(--border)",
                    background: "var(--card)",
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                  Recipient Title
                </label>
                <input
                  type="text"
                  value={recipientTitle}
                  onChange={(e) => setRecipientTitle(e.target.value)}
                  placeholder="e.g. VP of Engineering"
                  style={{
                    width: "100%",
                    padding: "0.45rem 0.65rem",
                    fontSize: "0.825rem",
                    borderRadius: "var(--radius)",
                    border: "1px solid var(--border)",
                    background: "var(--card)",
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                  Company Name
                </label>
                <input
                  type="text"
                  value={recipientCompany}
                  onChange={(e) => setRecipientCompany(e.target.value)}
                  placeholder="Company Name"
                  style={{
                    width: "100%",
                    padding: "0.45rem 0.65rem",
                    fontSize: "0.825rem",
                    borderRadius: "var(--radius)",
                    border: "1px solid var(--border)",
                    background: "var(--card)",
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                  Company Address
                </label>
                <input
                  type="text"
                  value={recipientAddress}
                  onChange={(e) => setRecipientAddress(e.target.value)}
                  placeholder="e.g. 100 Tech Way, San Francisco, CA"
                  style={{
                    width: "100%",
                    padding: "0.45rem 0.65rem",
                    fontSize: "0.825rem",
                    borderRadius: "var(--radius)",
                    border: "1px solid var(--border)",
                    background: "var(--card)",
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Custom Instructions */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Candidate Instructions (Optional)
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="e.g. Emphasize backend scalability, distributed systems leadership, and direct experience with Python/FastAPI..."
            rows={3}
            style={{
              width: "100%",
              padding: "0.625rem 0.75rem",
              borderRadius: "var(--radius)",
              border: "1px solid var(--border)",
              background: "var(--card)",
              fontSize: "0.875rem",
              fontFamily: "inherit",
              resize: "vertical",
            }}
          />
        </div>

        {/* Modal Actions */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "0.5rem" }}>
          <Button variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            type="submit"
            disabled={!jobId || jobs.length === 0}
            loading={isLoading}
            icon={<Sparkle size={16} weight="fill" />}
          >
            Generate Cover Letter
          </Button>
        </div>
      </form>
    </Modal>
  );
}
