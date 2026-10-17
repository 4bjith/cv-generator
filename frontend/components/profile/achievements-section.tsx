"use client";

import { useState } from "react";
import { Plus, Trash, PencilSimple, Trophy, ArrowUpRight, ShieldCheck } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal, SelectField, TextareaField } from "@/components/ui";
import {
  useAddAchievement,
  useDeleteAchievement,
  useUpdateAchievement,
} from "@/hooks/use-profile";
import { AchievementCategory, AchievementRecord, CandidateProfileData, ProvenanceType } from "@/types/profile";

interface AchievementsSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const CATEGORY_LABELS: Record<string, string> = {
  hackathon: "Hackathon",
  award: "Award & Honor",
  competition: "Competition",
  scholarship: "Scholarship",
  open_source: "Open Source Milestone",
  publication: "Publication",
  conference: "Conference Speaker",
  leadership: "Leadership Initiative",
  community: "Community Contribution",
  other: "Achievement",
};

const PROVENANCE_TONES: Record<ProvenanceType, "neutral" | "blue" | "purple" | "amber"> = {
  user_provided: "neutral",
  imported: "blue",
  ai_enhanced: "purple",
  ai_generated: "amber",
};

export function AchievementsSection({ profile, onToast }: AchievementsSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<AchievementRecord | null>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState("");
  const [issuer, setIssuer] = useState("");
  const [category, setCategory] = useState<AchievementCategory>("hackathon");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [provenance, setProvenance] = useState<ProvenanceType>("user_provided");

  const addAchievementMutation = useAddAchievement();
  const updateAchievementMutation = useUpdateAchievement();
  const deleteAchievementMutation = useDeleteAchievement();

  const handleOpenAdd = () => {
    setEditingItem(null);
    setTitle("");
    setDescription("");
    setDate("");
    setIssuer("");
    setCategory("hackathon");
    setEvidenceUrl("");
    setProvenance("user_provided");
    setModalOpen(true);
  };

  const handleOpenEdit = (ach: AchievementRecord) => {
    setEditingItem(ach);
    setTitle(ach.title);
    setDescription(ach.description || "");
    setDate(ach.date || "");
    setIssuer(ach.issuer || "");
    setCategory((ach.category as AchievementCategory) || "award");
    setEvidenceUrl(ach.evidence_url || "");
    setProvenance(ach.provenance || "user_provided");
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      onToast("Achievement title required", "Please enter an achievement title.", "error");
      return;
    }

    try {
      if (editingItem) {
        await updateAchievementMutation.mutateAsync({
          id: editingItem.id,
          payload: {
            title: title.trim(),
            description: description.trim() || undefined,
            date: date.trim() || undefined,
            issuer: issuer.trim() || undefined,
            category,
            evidence_url: evidenceUrl.trim() || undefined,
            provenance,
          },
        });
        onToast("Achievement updated", `Saved ${title}.`, "success");
      } else {
        await addAchievementMutation.mutateAsync({
          title: title.trim(),
          description: description.trim() || undefined,
          date: date.trim() || undefined,
          issuer: issuer.trim() || undefined,
          category,
          evidence_url: evidenceUrl.trim() || undefined,
          provenance,
          order_index: (profile.achievements?.length || 0),
        });
        onToast("Achievement added", `Added ${title}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save achievement.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, achTitle: string) => {
    try {
      await deleteAchievementMutation.mutateAsync(id);
      onToast("Achievement deleted", `Removed ${achTitle}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete achievement.";
      onToast("Delete failed", msg, "error");
    }
  };

  const achievements = profile.achievements || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Honors, Awards & Achievements
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Independent accomplishments and verified milestone achievements backed by evidence.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Achievement
        </Button>
      </div>

      {achievements.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 18.5rem), 1fr))", gap: "1.25rem" }}>
          {achievements.map((ach) => {
            const evidenceCount = (ach.evidence_ids || []).length;
            return (
              <Card key={ach.id} style={{ padding: "1.5rem", display: "flex", flexDirection: "column", justifyContent: "space-between", gap: "1rem" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
                      <div className="source-icon" style={{ backgroundColor: "#fef3c7", color: "#d97706" }}>
                        <Trophy size={20} aria-hidden="true" />
                      </div>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", flexWrap: "wrap" }}>
                          <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#09090b" }}>
                            {ach.title}
                          </h3>
                          {ach.provenance && (
                            <Badge tone={PROVENANCE_TONES[ach.provenance] || "neutral"}>
                              {ach.provenance.replace(/_/g, " ")}
                            </Badge>
                          )}
                        </div>
                        <p style={{ fontSize: "0.8125rem", color: "#64748b", marginTop: "0.15rem" }}>
                          {ach.issuer ? `${ach.issuer} · ` : ""}
                          <Badge tone="amber">{CATEGORY_LABELS[ach.category || "other"] || ach.category}</Badge>
                        </p>
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: "0.25rem" }}>
                      <IconButton label={`Edit ${ach.title}`} onClick={() => handleOpenEdit(ach)}>
                        <PencilSimple size={15} aria-hidden="true" />
                      </IconButton>
                      <IconButton label={`Delete ${ach.title}`} onClick={() => handleDelete(ach.id, ach.title)}>
                        <Trash size={15} aria-hidden="true" />
                      </IconButton>
                    </div>
                  </div>

                  {ach.date && (
                    <p style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.5rem" }}>
                      Date: <strong>{ach.date}</strong>
                    </p>
                  )}

                  {ach.description && (
                    <p style={{ fontSize: "0.875rem", color: "#334155", marginTop: "0.5rem", lineHeight: 1.5 }}>
                      {ach.description}
                    </p>
                  )}
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #f1f5f9", paddingTop: "0.5rem", flexWrap: "wrap", gap: "0.5rem" }}>
                  {ach.evidence_url ? (
                    <a
                      href={ach.evidence_url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: "0.75rem", color: "#2563eb", display: "inline-flex", alignItems: "center", gap: "0.25rem" }}
                    >
                      View Citation <ArrowUpRight size={13} aria-hidden="true" />
                    </a>
                  ) : <span />}

                  {evidenceCount > 0 && (
                    <Badge tone="green">
                      <ShieldCheck size={12} style={{ display: "inline", marginRight: "0.25rem" }} />
                      {evidenceCount} Evidence Link{evidenceCount > 1 ? "s" : ""}
                    </Badge>
                  )}
                </div>
              </Card>
            );
          })}
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
          <Trophy size={32} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No achievements recorded
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add hackathon wins, awards, publications, or open source contributions.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Achievement
          </Button>
        </Card>
      )}

      {/* Modal */}
      <Modal
        open={modalOpen}
        title={editingItem ? "Edit Achievement" : "Add Achievement"}
        description="Add a notable milestone, award, or competition victory."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addAchievementMutation.isPending || updateAchievementMutation.isPending}
            >
              {editingItem ? "Save Changes" : "Save Achievement"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Field
            label="Achievement Title *"
            name="ach_title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. 1st Place Winner - Global AI Hackathon"
            required
          />
          <div className="profile-form-grid">
            <SelectField
              label="Category"
              name="ach_category"
              value={category}
              onChange={(e) => setCategory(e.target.value as AchievementCategory)}
            >
              <option value="hackathon">Hackathon</option>
              <option value="award">Award</option>
              <option value="competition">Competition</option>
              <option value="scholarship">Scholarship</option>
              <option value="open_source">Open Source</option>
              <option value="publication">Publication</option>
              <option value="conference">Conference</option>
              <option value="leadership">Leadership</option>
              <option value="community">Community</option>
              <option value="other">Other</option>
            </SelectField>
            <Field
              label="Issuing Organization"
              name="ach_issuer"
              value={issuer}
              onChange={(e) => setIssuer(e.target.value)}
              placeholder="e.g. MIT, IEEE, Company X"
            />
            <Field
              label="Date / Year"
              name="ach_date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              placeholder="YYYY-MM (e.g. 2023-09)"
            />
            <Field
              label="Evidence URL (Optional)"
              name="ach_url"
              type="url"
              value={evidenceUrl}
              onChange={(e) => setEvidenceUrl(e.target.value)}
              placeholder="https://news.mit.edu/winners..."
            />
            <SelectField
              label="Provenance (Origin)"
              name="ach_provenance"
              value={provenance}
              onChange={(e) => setProvenance(e.target.value as ProvenanceType)}
            >
              <option value="user_provided">User Provided</option>
              <option value="imported">Imported</option>
              <option value="ai_enhanced">AI Enhanced</option>
              <option value="ai_generated">AI Generated</option>
            </SelectField>
          </div>

          <TextareaField
            label="Description & Context"
            name="ach_description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the achievement, competition scope, or publication details..."
            rows={3}
          />
        </form>
      </Modal>
    </div>
  );
}
