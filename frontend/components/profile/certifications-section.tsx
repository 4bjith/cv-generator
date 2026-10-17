"use client";

import { useState } from "react";
import { Plus, Trash, PencilSimple, SealCheck, ArrowUpRight } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal } from "@/components/ui";
import {
  useAddCertification,
  useDeleteCertification,
  useUpdateCertification,
} from "@/hooks/use-profile";
import { CandidateProfileData, Certification } from "@/types/profile";

interface CertificationsSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function CertificationsSection({ profile, onToast }: CertificationsSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Certification | null>(null);

  const [name, setName] = useState("");
  const [issuer, setIssuer] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [expirationDate, setExpirationDate] = useState("");
  const [credentialId, setCredentialId] = useState("");
  const [credentialUrl, setCredentialUrl] = useState("");
  const [skillsText, setSkillsText] = useState("");

  const addCertMutation = useAddCertification();
  const updateCertMutation = useUpdateCertification();
  const deleteCertMutation = useDeleteCertification();

  const handleOpenAdd = () => {
    setEditingItem(null);
    setName("");
    setIssuer("");
    setIssueDate("");
    setExpirationDate("");
    setCredentialId("");
    setCredentialUrl("");
    setSkillsText("");
    setModalOpen(true);
  };

  const handleOpenEdit = (cert: Certification) => {
    setEditingItem(cert);
    setName(cert.name);
    setIssuer(cert.issuer);
    setIssueDate(cert.issue_date || "");
    setExpirationDate(cert.expiration_date || "");
    setCredentialId(cert.credential_id || "");
    setCredentialUrl(cert.credential_url || "");
    setSkillsText((cert.skills || []).join(", "));
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !issuer.trim()) {
      onToast("Required fields missing", "Certification name and Issuer are required.", "error");
      return;
    }

    const skills = skillsText
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      if (editingItem) {
        await updateCertMutation.mutateAsync({
          id: editingItem.id,
          payload: {
            name: name.trim(),
            issuer: issuer.trim(),
            issue_date: issueDate.trim() || undefined,
            expiration_date: expirationDate.trim() || undefined,
            credential_id: credentialId.trim() || undefined,
            credential_url: credentialUrl.trim() || undefined,
            skills,
          },
        });
        onToast("Certification updated", `Saved ${name}.`, "success");
      } else {
        await addCertMutation.mutateAsync({
          name: name.trim(),
          issuer: issuer.trim(),
          issue_date: issueDate.trim() || undefined,
          expiration_date: expirationDate.trim() || undefined,
          credential_id: credentialId.trim() || undefined,
          credential_url: credentialUrl.trim() || undefined,
          skills,
          order_index: (profile.certifications?.length || 0),
        });
        onToast("Certification added", `Added ${name}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save certification.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, certName: string) => {
    try {
      await deleteCertMutation.mutateAsync(id);
      onToast("Certification deleted", `Removed ${certName}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete certification.";
      onToast("Delete failed", msg, "error");
    }
  };

  const certifications = profile.certifications || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Professional Certifications & Licenses
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Industry credentials, professional licenses, and accredited technical certificates.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Certification
        </Button>
      </div>

      {certifications.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 18.5rem), 1fr))", gap: "1.25rem" }}>
          {certifications.map((cert) => (
            <Card key={cert.id} style={{ padding: "1.5rem", display: "flex", flexDirection: "column", justifyContent: "space-between", gap: "1rem" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
                    <SealCheck size={22} weight="fill" className="text-blue-600 flex-shrink-0" aria-hidden="true" />
                    <div>
                      <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#09090b" }}>
                        {cert.name}
                      </h3>
                      <p style={{ fontSize: "0.8125rem", color: "#64748b", fontWeight: 500 }}>
                        {cert.issuer}
                      </p>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "0.25rem" }}>
                    <IconButton label={`Edit ${cert.name}`} onClick={() => handleOpenEdit(cert)}>
                      <PencilSimple size={15} aria-hidden="true" />
                    </IconButton>
                    <IconButton label={`Delete ${cert.name}`} onClick={() => handleDelete(cert.id, cert.name)}>
                      <Trash size={15} aria-hidden="true" />
                    </IconButton>
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem", fontSize: "0.75rem", color: "#475569", marginTop: "0.75rem" }}>
                  {cert.issue_date && (
                    <span>
                      Issued: <strong>{cert.issue_date}</strong>
                      {cert.expiration_date ? ` · Expires: ${cert.expiration_date}` : " · Does not expire"}
                    </span>
                  )}
                  {cert.credential_id && (
                    <span>
                      Credential ID: <code>{cert.credential_id}</code>
                    </span>
                  )}
                </div>

                {cert.skills && cert.skills.length > 0 && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem", marginTop: "0.75rem" }}>
                    {cert.skills.map((skill) => (
                      <Badge key={skill} tone="neutral">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              {cert.credential_url && (
                <div style={{ borderTop: "1px solid #f1f5f9", paddingTop: "0.5rem" }}>
                  <a
                    href={cert.credential_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ fontSize: "0.75rem", color: "#2563eb", display: "inline-flex", alignItems: "center", gap: "0.25rem" }}
                  >
                    Verify Credential <ArrowUpRight size={13} aria-hidden="true" />
                  </a>
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <Card
          style={{
            padding: "3rem 1.5rem",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "0.75rem",
          }}
        >
          <SealCheck size={32} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No certifications added
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add cloud, architecture, cybersecurity, or professional certifications to strengthen your profile evidence.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Certification
          </Button>
        </Card>
      )}

      {/* Modal */}
      <Modal
        open={modalOpen}
        title={editingItem ? "Edit Certification" : "Add Certification"}
        description="Add a verified professional certification or credential."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addCertMutation.isPending || updateCertMutation.isPending}
            >
              {editingItem ? "Save Changes" : "Save Certification"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div className="profile-form-grid">
            <Field
              label="Certification Name *"
              name="cert_name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. AWS Certified Solutions Architect"
              required
            />
            <Field
              label="Issuing Organization *"
              name="cert_issuer"
              value={issuer}
              onChange={(e) => setIssuer(e.target.value)}
              placeholder="e.g. Amazon Web Services, Google Cloud"
              required
            />
            <Field
              label="Issue Date"
              name="cert_issue_date"
              value={issueDate}
              onChange={(e) => setIssueDate(e.target.value)}
              placeholder="YYYY-MM (e.g. 2023-05)"
            />
            <Field
              label="Expiration Date (Optional)"
              name="cert_exp_date"
              value={expirationDate}
              onChange={(e) => setExpirationDate(e.target.value)}
              placeholder="Leave blank if no expiration"
            />
            <Field
              label="Credential ID"
              name="cert_id"
              value={credentialId}
              onChange={(e) => setCredentialId(e.target.value)}
              placeholder="e.g. AWS-PSA-12345"
            />
            <Field
              label="Verification URL"
              name="cert_url"
              type="url"
              value={credentialUrl}
              onChange={(e) => setCredentialUrl(e.target.value)}
              placeholder="https://aws.amazon.com/verify/..."
            />
          </div>

          <Field
            label="Associated Skills (comma-separated)"
            name="cert_skills"
            value={skillsText}
            onChange={(e) => setSkillsText(e.target.value)}
            placeholder="AWS, Cloud Architecture, Distributed Systems"
          />
        </form>
      </Modal>
    </div>
  );
}
