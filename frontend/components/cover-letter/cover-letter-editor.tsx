"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowsClockwise,
  CheckCircle,
  Copy,
  DownloadSimple,
  FileDoc,
  FilePdf,
  FloppyDisk,
  Info,
  Plus,
  ShieldCheck,
  Sparkle,
  Trash,
  WarningCircle,
} from "@phosphor-icons/react";
import { Badge, Button, Modal } from "@/components/ui";
import {
  useCoverLetterDetail,
  useExportCoverLetterDocx,
  useExportCoverLetterPdf,
  useRegenerateCoverLetter,
  useUpdateCoverLetter,
} from "@/hooks/use-cover-letter";
import {
  CoverLetterResponse,
  CoverLetterStatus,
  RegenerateCoverLetterRequest,
  UpdateCoverLetterRequest,
} from "@/types/cover-letter";
import { CoverLetterRegenerateModal } from "./cover-letter-regenerate-modal";

interface CoverLetterEditorProps {
  letterId: string;
  onClose: () => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  onNavigateToLetter?: (id: string) => void;
}

export function CoverLetterEditor({
  letterId,
  onClose,
  onToast,
  onNavigateToLetter,
}: CoverLetterEditorProps) {
  const { data: letter, isLoading, isError, error, refetch } = useCoverLetterDetail(letterId);
  const updateMutation = useUpdateCoverLetter();
  const regenerateMutation = useRegenerateCoverLetter();
  const exportPdfMutation = useExportCoverLetterPdf();
  const exportDocxMutation = useExportCoverLetterDocx();

  // Local form state
  const [name, setName] = useState("");
  const [status, setStatus] = useState<CoverLetterStatus>("draft");
  const [recipientName, setRecipientName] = useState("");
  const [recipientTitle, setRecipientTitle] = useState("");
  const [recipientCompany, setRecipientCompany] = useState("");
  const [recipientAddress, setRecipientAddress] = useState("");
  const [salutation, setSalutation] = useState("");
  const [opening, setOpening] = useState("");
  const [bodyParagraphs, setBodyParagraphs] = useState<string[]>([]);
  const [closing, setClosing] = useState("");
  const [signOff, setSignOff] = useState("");
  const [senderName, setSenderName] = useState("");
  const [senderContact, setSenderContact] = useState("");

  const [initialJson, setInitialJson] = useState("");
  const [isRegenerateModalOpen, setIsRegenerateModalOpen] = useState(false);
  const [showDiscardModal, setShowDiscardModal] = useState(false);
  const [activeTab, setActiveTab] = useState<"edit" | "provenance">("edit");

  // Sync initial state from loaded letter
  useEffect(() => {
    if (letter) {
      setName(letter.name || "");
      setStatus(letter.status || "draft");
      setRecipientName(letter.recipient_name || "");
      setRecipientTitle(letter.recipient_title || "");
      setRecipientCompany(letter.recipient_company || "");
      setRecipientAddress(letter.recipient_address || "");
      setSalutation(letter.salutation || "Dear Hiring Team,");
      setOpening(letter.opening || "");
      setBodyParagraphs(letter.body_paragraphs || []);
      setClosing(letter.closing || "");
      setSignOff(letter.sign_off || "Sincerely,");
      setSenderName(letter.sender_name || "");
      setSenderContact(letter.sender_contact || "");

      const snapshot = JSON.stringify({
        name: letter.name,
        status: letter.status,
        recipient_name: letter.recipient_name,
        recipient_title: letter.recipient_title,
        recipient_company: letter.recipient_company,
        recipient_address: letter.recipient_address,
        salutation: letter.salutation,
        opening: letter.opening,
        body_paragraphs: letter.body_paragraphs,
        closing: letter.closing,
        sign_off: letter.sign_off,
        sender_name: letter.sender_name,
        sender_contact: letter.sender_contact,
      });
      setInitialJson(snapshot);
    }
  }, [letter]);

  // Compute dirty state
  const isDirty = useMemo(() => {
    if (!initialJson) return false;
    const current = JSON.stringify({
      name,
      status,
      recipient_name: recipientName || null,
      recipient_title: recipientTitle || null,
      recipient_company: recipientCompany || null,
      recipient_address: recipientAddress || null,
      salutation,
      opening,
      body_paragraphs: bodyParagraphs,
      closing,
      sign_off: signOff,
      sender_name: senderName,
      sender_contact: senderContact || null,
    });
    return current !== initialJson;
  }, [
    name,
    status,
    recipientName,
    recipientTitle,
    recipientCompany,
    recipientAddress,
    salutation,
    opening,
    bodyParagraphs,
    closing,
    signOff,
    senderName,
    senderContact,
    initialJson,
  ]);

  // Word count calculation
  const totalWordCount = useMemo(() => {
    const full = [opening, ...bodyParagraphs, closing].join(" ");
    return full.split(/\s+/).filter(Boolean).length;
  }, [opening, bodyParagraphs, closing]);

  const handleSave = async () => {
    try {
      const payload: UpdateCoverLetterRequest = {
        name: name.trim() || undefined,
        status,
        recipient_name: recipientName.trim() || null,
        recipient_title: recipientTitle.trim() || null,
        recipient_company: recipientCompany.trim() || null,
        recipient_address: recipientAddress.trim() || null,
        salutation: salutation.trim(),
        opening: opening.trim(),
        body_paragraphs: bodyParagraphs.map((p) => p.trim()).filter(Boolean),
        closing: closing.trim(),
        sign_off: signOff.trim(),
        sender_name: senderName.trim(),
        sender_contact: senderContact.trim() || null,
      };

      const updated = await updateMutation.mutateAsync({ id: letterId, payload });
      setInitialJson(
        JSON.stringify({
          name: updated.name,
          status: updated.status,
          recipient_name: updated.recipient_name,
          recipient_title: updated.recipient_title,
          recipient_company: updated.recipient_company,
          recipient_address: updated.recipient_address,
          salutation: updated.salutation,
          opening: updated.opening,
          body_paragraphs: updated.body_paragraphs,
          closing: updated.closing,
          sign_off: updated.sign_off,
          sender_name: updated.sender_name,
          sender_contact: updated.sender_contact,
        })
      );
      onToast("Cover Letter Saved", "Your edits have been successfully persisted.", "success");
    } catch (err: any) {
      onToast("Save Failed", err?.message || "Failed to save cover letter.", "error");
    }
  };

  const handleRegenerate = async (payload: RegenerateCoverLetterRequest) => {
    try {
      const result = await regenerateMutation.mutateAsync({ id: letterId, payload });
      setIsRegenerateModalOpen(false);

      if (payload.preserve_as_new_version && result.id !== letterId) {
        onToast("New Version Created", `Created "${result.name}" with preserved history.`, "success");
        if (onNavigateToLetter) {
          onNavigateToLetter(result.id);
        } else {
          onClose();
        }
      } else {
        onToast("Letter Regenerated", "Cover letter re-crafted with updated parameters.", "success");
      }
    } catch (err: any) {
      onToast("Regeneration Failed", err?.message || "Failed to regenerate cover letter.", "error");
    }
  };

  const handleExportPdf = async () => {
    try {
      await exportPdfMutation.mutateAsync(letterId);
      onToast("PDF Exported", "Your cover letter was downloaded as a professional PDF.", "success");
    } catch (err: any) {
      onToast("Export Failed", err?.message || "Failed to export PDF.", "error");
    }
  };

  const handleExportDocx = async () => {
    try {
      await exportDocxMutation.mutateAsync(letterId);
      onToast("DOCX Exported", "Your cover letter was downloaded as an editable Word document.", "success");
    } catch (err: any) {
      onToast("Export Failed", err?.message || "Failed to export DOCX.", "error");
    }
  };

  const handleBack = () => {
    if (isDirty) {
      setShowDiscardModal(true);
    } else {
      onClose();
    }
  };

  const addBodyParagraph = () => {
    setBodyParagraphs([...bodyParagraphs, ""]);
  };

  const updateBodyParagraph = (index: number, value: string) => {
    const updated = [...bodyParagraphs];
    updated[index] = value;
    setBodyParagraphs(updated);
  };

  const removeBodyParagraph = (index: number) => {
    setBodyParagraphs(bodyParagraphs.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return (
      <div className="workspace-container" style={{ textAlign: "center", padding: "4rem 1rem" }}>
        <p style={{ color: "var(--muted)" }}>Loading cover letter draft...</p>
      </div>
    );
  }

  if (isError || !letter) {
    return (
      <div className="workspace-container" style={{ textAlign: "center", padding: "4rem 1rem" }}>
        <p style={{ color: "#ef4444" }}>Failed to load cover letter.</p>
        <Button variant="ghost" onClick={onClose} style={{ marginTop: "1rem" }}>
          Back to Cover Letters
        </Button>
      </div>
    );
  }

  return (
    <div className="workspace-container" style={{ maxWidth: "1500px", margin: "0 auto", paddingBottom: "4rem" }}>
      {/* Top Header Bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
          paddingBottom: "1.25rem",
          borderBottom: "1px solid var(--border)",
          marginBottom: "1.5rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          <Button
            variant="ghost"
            size="sm"
            icon={<ArrowLeft size={16} />}
            onClick={handleBack}
          >
            Back
          </Button>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{
              fontSize: "1.25rem",
              fontWeight: 700,
              padding: "0.25rem 0.5rem",
              borderRadius: "var(--radius)",
              border: "1px solid transparent",
              background: "transparent",
              color: "inherit",
              outline: "none",
            }}
            onFocus={(e) => (e.target.style.border = "1px solid var(--border)")}
            onBlur={(e) => (e.target.style.border = "1px solid transparent")}
          />
          <Badge tone={status === "ready" ? "green" : status === "draft" ? "blue" : "neutral"}>
            {status.toUpperCase()}
          </Badge>
          {isDirty && (
            <Badge tone="amber">Unsaved Changes</Badge>
          )}
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as CoverLetterStatus)}
            style={{
              padding: "0.45rem 0.65rem",
              borderRadius: "var(--radius)",
              border: "1px solid var(--border)",
              background: "var(--card)",
              fontSize: "0.825rem",
              cursor: "pointer",
            }}
          >
            <option value="draft">Draft</option>
            <option value="ready">Ready</option>
            <option value="archived">Archived</option>
          </select>

          <Button
            variant="ghost"
            size="sm"
            icon={<ArrowsClockwise size={16} />}
            onClick={() => setIsRegenerateModalOpen(true)}
          >
            Regenerate
          </Button>

          <Button
            variant="ghost"
            size="sm"
            icon={<FilePdf size={16} />}
            onClick={handleExportPdf}
            loading={exportPdfMutation.isPending}
          >
            Export PDF
          </Button>

          <Button
            variant="ghost"
            size="sm"
            icon={<FileDoc size={16} />}
            onClick={handleExportDocx}
            loading={exportDocxMutation.isPending}
          >
            Export DOCX
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={<FloppyDisk size={16} />}
            onClick={handleSave}
            loading={updateMutation.isPending}
            disabled={!isDirty}
          >
            Save Changes
          </Button>
        </div>
      </div>

      {/* Editor Main Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", alignItems: "start" }}>
        {/* Left Column: Form Controls & Grounding Panels */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Tabs for Form vs Provenance */}
          <div style={{ display: "flex", gap: "0.5rem", borderBottom: "1px solid var(--border)", paddingBottom: "0.5rem" }}>
            <button
              type="button"
              onClick={() => setActiveTab("edit")}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "var(--radius)",
                border: "none",
                background: activeTab === "edit" ? "rgba(37, 99, 235, 0.1)" : "transparent",
                color: activeTab === "edit" ? "var(--accent)" : "var(--muted)",
                fontWeight: activeTab === "edit" ? 600 : 500,
                fontSize: "0.875rem",
                cursor: "pointer",
              }}
            >
              Draft Content & Sections
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("provenance")}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "var(--radius)",
                border: "none",
                background: activeTab === "provenance" ? "rgba(37, 99, 235, 0.1)" : "transparent",
                color: activeTab === "provenance" ? "var(--accent)" : "var(--muted)",
                fontWeight: activeTab === "provenance" ? 600 : 500,
                fontSize: "0.875rem",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
              }}
            >
              <ShieldCheck size={16} />
              <span>Evidence & Grounding Audit</span>
              {letter.unresolved_gaps && letter.unresolved_gaps.length > 0 && (
                <Badge tone="amber">{letter.unresolved_gaps.length}</Badge>
              )}
            </button>
          </div>

          {activeTab === "edit" ? (
            <>
              {/* Recipient Information Card */}
              <div style={{
                padding: "1.25rem",
                borderRadius: "var(--radius)",
                background: "var(--card)",
                border: "1px solid var(--border)",
              }}>
                <div style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.75rem" }}>
                  Recipient & Employer Details
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
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
                      placeholder="e.g. Head of Engineering"
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
                      placeholder="Company"
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
                      placeholder="e.g. 100 Main St, City, ST"
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
              </div>

              {/* Salutation & Opening */}
              <div style={{
                padding: "1.25rem",
                borderRadius: "var(--radius)",
                background: "var(--card)",
                border: "1px solid var(--border)",
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
              }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                    Salutation
                  </label>
                  <input
                    type="text"
                    value={salutation}
                    onChange={(e) => setSalutation(e.target.value)}
                    placeholder="Dear Hiring Team,"
                    style={{
                      width: "100%",
                      padding: "0.45rem 0.65rem",
                      fontSize: "0.85rem",
                      borderRadius: "var(--radius)",
                      border: "1px solid var(--border)",
                      background: "var(--card)",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                    Opening Paragraph
                  </label>
                  <textarea
                    value={opening}
                    onChange={(e) => setOpening(e.target.value)}
                    rows={3}
                    style={{
                      width: "100%",
                      padding: "0.625rem 0.75rem",
                      fontSize: "0.85rem",
                      borderRadius: "var(--radius)",
                      border: "1px solid var(--border)",
                      background: "var(--card)",
                      fontFamily: "inherit",
                      lineHeight: 1.5,
                      resize: "vertical",
                    }}
                  />
                </div>
              </div>

              {/* Body Paragraphs */}
              <div style={{
                padding: "1.25rem",
                borderRadius: "var(--radius)",
                background: "var(--card)",
                border: "1px solid var(--border)",
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>
                    Body Paragraphs ({bodyParagraphs.length})
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={<Plus size={14} />}
                    onClick={addBodyParagraph}
                  >
                    Add Paragraph
                  </Button>
                </div>

                {bodyParagraphs.map((para, index) => (
                  <div key={index} style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)" }}>
                        Paragraph {index + 1}
                      </span>
                      {bodyParagraphs.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeBodyParagraph(index)}
                          style={{
                            background: "none",
                            border: "none",
                            color: "#ef4444",
                            cursor: "pointer",
                            fontSize: "0.75rem",
                            display: "flex",
                            alignItems: "center",
                            gap: "0.25rem",
                          }}
                        >
                          <Trash size={14} /> Remove
                        </button>
                      )}
                    </div>
                    <textarea
                      value={para}
                      onChange={(e) => updateBodyParagraph(index, e.target.value)}
                      rows={4}
                      style={{
                        width: "100%",
                        padding: "0.625rem 0.75rem",
                        fontSize: "0.85rem",
                        borderRadius: "var(--radius)",
                        border: "1px solid var(--border)",
                        background: "var(--card)",
                        fontFamily: "inherit",
                        lineHeight: 1.5,
                        resize: "vertical",
                      }}
                    />
                  </div>
                ))}
              </div>

              {/* Closing & Sign-off */}
              <div style={{
                padding: "1.25rem",
                borderRadius: "var(--radius)",
                background: "var(--card)",
                border: "1px solid var(--border)",
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
              }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                    Closing Paragraph
                  </label>
                  <textarea
                    value={closing}
                    onChange={(e) => setClosing(e.target.value)}
                    rows={3}
                    style={{
                      width: "100%",
                      padding: "0.625rem 0.75rem",
                      fontSize: "0.85rem",
                      borderRadius: "var(--radius)",
                      border: "1px solid var(--border)",
                      background: "var(--card)",
                      fontFamily: "inherit",
                      lineHeight: 1.5,
                      resize: "vertical",
                    }}
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                  <div>
                    <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                      Sign-off
                    </label>
                    <input
                      type="text"
                      value={signOff}
                      onChange={(e) => setSignOff(e.target.value)}
                      placeholder="Sincerely,"
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
                      Sender Name
                    </label>
                    <input
                      type="text"
                      value={senderName}
                      onChange={(e) => setSenderName(e.target.value)}
                      placeholder="Your Full Name"
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

                <div>
                  <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, marginBottom: "0.25rem" }}>
                    Sender Contact Line
                  </label>
                  <input
                    type="text"
                    value={senderContact}
                    onChange={(e) => setSenderContact(e.target.value)}
                    placeholder="email@example.com | (555) 012-3456"
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
            </>
          ) : (
            /* Provenance & Truth Audit Tab */
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {/* Zero Hallucination Guarantee */}
              <div style={{
                padding: "1rem",
                borderRadius: "var(--radius)",
                background: "rgba(16, 185, 129, 0.08)",
                border: "1px solid rgba(16, 185, 129, 0.2)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 600, color: "#065f46", fontSize: "0.9rem" }}>
                  <ShieldCheck size={18} weight="fill" />
                  <span>Evidence-Grounded Guarantee</span>
                </div>
                <p style={{ margin: "0.35rem 0 0 0", fontSize: "0.8rem", color: "#047857", lineHeight: 1.4 }}>
                  All qualifications, dates, achievements, and metrics in this letter were strictly verified against your Candidate Profile facts and confirmed clarification responses.
                </p>
              </div>

              {/* Unresolved Gaps & Missing Info */}
              {letter.unresolved_gaps && letter.unresolved_gaps.length > 0 && (
                <div style={{
                  padding: "1rem",
                  borderRadius: "var(--radius)",
                  background: "rgba(245, 158, 11, 0.08)",
                  border: "1px solid rgba(245, 158, 11, 0.25)",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 600, color: "#92400e", fontSize: "0.875rem" }}>
                    <WarningCircle size={18} weight="fill" />
                    <span>Missing Information / Unresolved Requirements ({letter.unresolved_gaps.length})</span>
                  </div>
                  <p style={{ margin: "0.25rem 0 0.75rem 0", fontSize: "0.775rem", color: "#b45309" }}>
                    The target job description requested the following competencies where no verified candidate evidence was found. The generator used neutral phrasing instead of fabricating experience:
                  </p>
                  <ul style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.8rem", color: "#78350f", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                    {letter.unresolved_gaps.map((gap, i) => (
                      <li key={i}>{gap}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Verified Factual Claims */}
              <div style={{
                padding: "1.25rem",
                borderRadius: "var(--radius)",
                background: "var(--card)",
                border: "1px solid var(--border)",
              }}>
                <div style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.75rem" }}>
                  Verified Claims & Evidence Provenance ({letter.factual_claims?.length || 0})
                </div>
                {letter.factual_claims && letter.factual_claims.length > 0 ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    {letter.factual_claims.map((claim, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: "0.625rem 0.75rem",
                          borderRadius: "var(--radius)",
                          background: "var(--background)",
                          border: "1px solid var(--border)",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "flex-start",
                          gap: "0.75rem",
                        }}
                      >
                        <div style={{ fontSize: "0.825rem", lineHeight: 1.4 }}>
                          {claim.claim_text}
                        </div>
                        <Badge tone="green" style={{ flexShrink: 0 }}>
                          {claim.entity_type}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ fontSize: "0.8rem", color: "var(--muted)", margin: 0 }}>
                    No isolated factual claims recorded for this draft.
                  </p>
                )}
              </div>

              {/* Change Summary if regenerated */}
              {letter.change_summary && (
                <div style={{
                  padding: "1.25rem",
                  borderRadius: "var(--radius)",
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                }}>
                  <div style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.5rem" }}>
                    AI Regeneration Summary
                  </div>
                  <p style={{ margin: 0, fontSize: "0.825rem", color: "var(--muted)", lineHeight: 1.5 }}>
                    {letter.change_summary}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Live Formal Letterhead Document Preview */}
        <div style={{ position: "sticky", top: "1rem" }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "0.75rem",
          }}>
            <div style={{ fontWeight: 600, fontSize: "0.875rem", color: "var(--muted)" }}>
              Document Preview ({totalWordCount} words)
            </div>
            <div style={{ display: "flex", gap: "0.35rem" }}>
              <Badge tone="neutral">{letter.tone.toUpperCase()}</Badge>
              <Badge tone="neutral">{letter.length_option.toUpperCase()}</Badge>
            </div>
          </div>

          {/* Paper Canvas */}
          <div
            style={{
              background: "#ffffff",
              color: "#0f172a",
              boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05)",
              border: "1px solid #e2e8f0",
              borderRadius: "4px",
              padding: "2.75rem 2.5rem",
              fontFamily: 'Charter, "Bitstream Charter", "Sitka Text", Cambria, Georgia, serif',
              fontSize: "0.95rem",
              lineHeight: 1.65,
              minHeight: "750px",
            }}
          >
            {/* Sender Header */}
            <div style={{ borderBottom: "1.5px solid #0f172a", paddingBottom: "1rem", marginBottom: "1.5rem" }}>
              <div style={{ fontSize: "1.35rem", fontWeight: 700, letterSpacing: "-0.01em", color: "#0f172a" }}>
                {senderName || "Candidate Name"}
              </div>
              <div style={{ fontSize: "0.85rem", color: "#475569", marginTop: "0.25rem", fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                {senderContact || "candidate@email.com | (555) 012-3456"}
              </div>
            </div>

            {/* Date */}
            <div style={{ fontSize: "0.9rem", color: "#334155", marginBottom: "1.5rem" }}>
              {new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
            </div>

            {/* Recipient Block */}
            <div style={{ marginBottom: "1.5rem", fontSize: "0.9rem", color: "#1e293b", lineHeight: 1.45 }}>
              {recipientName && <div style={{ fontWeight: 600 }}>{recipientName}</div>}
              {recipientTitle && <div>{recipientTitle}</div>}
              {recipientCompany && <div style={{ fontWeight: 600 }}>{recipientCompany}</div>}
              {recipientAddress && <div>{recipientAddress}</div>}
            </div>

            {/* Salutation */}
            <div style={{ marginBottom: "1.25rem", fontWeight: 600, color: "#0f172a" }}>
              {salutation || "Dear Hiring Team,"}
            </div>

            {/* Opening Paragraph */}
            {opening && (
              <p style={{ margin: "0 0 1.25rem 0", textAlign: "justify" }}>
                {opening}
              </p>
            )}

            {/* Body Paragraphs */}
            {bodyParagraphs.map((para, i) => (
              <p key={i} style={{ margin: "0 0 1.25rem 0", textAlign: "justify" }}>
                {para}
              </p>
            ))}

            {/* Closing Paragraph */}
            {closing && (
              <p style={{ margin: "0 0 1.75rem 0", textAlign: "justify" }}>
                {closing}
              </p>
            )}

            {/* Sign-off & Signature */}
            <div style={{ marginTop: "1.5rem" }}>
              <div style={{ marginBottom: "2.5rem", color: "#1e293b" }}>
                {signOff || "Sincerely,"}
              </div>
              <div style={{ fontWeight: 700, color: "#0f172a" }}>
                {senderName || "Candidate Name"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Discard confirmation modal */}
      {showDiscardModal && (
        <Modal
          open={showDiscardModal}
          onClose={() => setShowDiscardModal(false)}
          title="Unsaved Changes"
        >
          <p style={{ fontSize: "0.875rem", color: "var(--muted)", margin: 0 }}>
            You have unsaved changes to this cover letter draft. Are you sure you want to exit without saving?
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "1.25rem" }}>
            <Button variant="ghost" onClick={() => setShowDiscardModal(false)}>
              Keep Editing
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                setShowDiscardModal(false);
                onClose();
              }}
            >
              Discard Changes
            </Button>
          </div>
        </Modal>
      )}

      {/* Regenerate Modal */}
      {isRegenerateModalOpen && (
        <CoverLetterRegenerateModal
          isOpen={isRegenerateModalOpen}
          onClose={() => setIsRegenerateModalOpen(false)}
          letter={letter}
          onRegenerate={handleRegenerate}
          isLoading={regenerateMutation.isPending}
        />
      )}
    </div>
  );
}
