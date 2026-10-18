"use client";

import { useState } from "react";
import { ArrowsClockwise, Sparkle } from "@phosphor-icons/react";
import { Button, Modal } from "@/components/ui";
import {
  CoverLetterLength,
  CoverLetterResponse,
  CoverLetterTone,
  RegenerateCoverLetterRequest,
} from "@/types/cover-letter";

interface CoverLetterRegenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
  letter: CoverLetterResponse;
  onRegenerate: (payload: RegenerateCoverLetterRequest) => Promise<void>;
  isLoading: boolean;
}

const TONES: { id: CoverLetterTone; label: string; desc: string }[] = [
  { id: "professional", label: "Professional", desc: "Balanced, confident, industry-standard tone" },
  { id: "concise", label: "Concise", desc: "High-impact, direct, efficient communication" },
  { id: "technical", label: "Technical", desc: "Architecture, engineering, and methodology focus" },
  { id: "formal", label: "Formal", desc: "Traditional, executive, reverent phrasing" },
];

const LENGTHS: { id: CoverLetterLength; label: string; desc: string }[] = [
  { id: "short", label: "Short", desc: "Around 200 words, quick read" },
  { id: "standard", label: "Standard", desc: "Around 350 words, well-balanced" },
  { id: "detailed", label: "Detailed", desc: "Around 500 words, deep evidence depth" },
];

export function CoverLetterRegenerateModal({
  isOpen,
  onClose,
  letter,
  onRegenerate,
  isLoading,
}: CoverLetterRegenerateModalProps) {
  const [tone, setTone] = useState<CoverLetterTone>(letter.tone || "professional");
  const [lengthOption, setLengthOption] = useState<CoverLetterLength>(
    letter.length_option || "standard"
  );
  const [instructions, setInstructions] = useState("");
  const [preserveVersion, setPreserveVersion] = useState(true);
  const [newName, setNewName] = useState(`${letter.name} (Regenerated)`);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onRegenerate({
      tone,
      length_option: lengthOption,
      additional_instructions: instructions.trim() || null,
      preserve_as_new_version: preserveVersion,
      new_name: preserveVersion ? newName.trim() || undefined : undefined,
    });
  };

  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      title="Regenerate Cover Letter"
    >
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--muted)" }}>
          Re-craft this letter with updated writing parameters while strictly maintaining zero-hallucination grounding against your verified Candidate Profile facts.
        </p>

        {/* Tone Selector */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Writing Tone
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
            Target Length
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

        {/* Additional Instructions */}
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.5rem" }}>
            Additional Focus or Guidance
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="e.g. Emphasize experience with distributed Kubernetes clusters and cross-functional leadership..."
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

        {/* Version Preservation Option */}
        <div style={{
          padding: "0.875rem 1rem",
          borderRadius: "var(--radius)",
          background: "rgba(37, 99, 235, 0.04)",
          border: "1px solid rgba(37, 99, 235, 0.15)",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.625rem", cursor: "pointer", fontWeight: 500, fontSize: "0.875rem" }}>
            <input
              type="checkbox"
              checked={preserveVersion}
              onChange={(e) => setPreserveVersion(e.target.checked)}
              style={{ width: "16px", height: "16px", accentColor: "var(--accent)" }}
            />
            <span>Preserve current version as a new independent draft</span>
          </label>
          <p style={{ margin: 0, fontSize: "0.75rem", color: "var(--muted)", paddingLeft: "1.625rem" }}>
            {preserveVersion
              ? "Creates a new copy so you can revisit the previous draft at any time."
              : "Overwrites the current draft in-place and provides an explainable AI change summary."}
          </p>

          {preserveVersion && (
            <div style={{ paddingLeft: "1.625rem", marginTop: "0.25rem" }}>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="New letter version name"
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
          )}
        </div>

        {/* Modal Actions */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "0.5rem" }}>
          <Button variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            type="submit"
            loading={isLoading}
            icon={<ArrowsClockwise size={16} weight="bold" />}
          >
            Regenerate Letter
          </Button>
        </div>
      </form>
    </Modal>
  );
}
