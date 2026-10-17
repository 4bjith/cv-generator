"use client";

import { useState } from "react";
import { Plus, Trash, PencilSimple, GraduationCap } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal, TextareaField } from "@/components/ui";
import {
  useAddEducation,
  useDeleteEducation,
  useUpdateEducation,
} from "@/hooks/use-profile";
import { CandidateProfileData, EducationRecord } from "@/types/profile";

interface EducationSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function EducationSection({ profile, onToast }: EducationSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<EducationRecord | null>(null);

  const [institution, setInstitution] = useState("");
  const [degree, setDegree] = useState("");
  const [fieldOfStudy, setFieldOfStudy] = useState("");
  const [location, setLocation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [grade, setGrade] = useState("");
  const [description, setDescription] = useState("");
  const [achievementsText, setAchievementsText] = useState("");

  const addEducationMutation = useAddEducation();
  const updateEducationMutation = useUpdateEducation();
  const deleteEducationMutation = useDeleteEducation();

  const handleOpenAdd = () => {
    setEditingItem(null);
    setInstitution("");
    setDegree("");
    setFieldOfStudy("");
    setLocation("");
    setStartDate("");
    setEndDate("");
    setGrade("");
    setDescription("");
    setAchievementsText("");
    setModalOpen(true);
  };

  const handleOpenEdit = (item: EducationRecord) => {
    setEditingItem(item);
    setInstitution(item.institution);
    setDegree(item.degree);
    setFieldOfStudy(item.field_of_study || "");
    setLocation(item.location || "");
    setStartDate(item.start_date || "");
    setEndDate(item.end_date || "");
    setGrade(item.grade || "");
    setDescription(item.description || "");
    setAchievementsText((item.achievements || []).join("\n"));
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!institution.trim() || !degree.trim()) {
      onToast("Required fields missing", "Institution and Degree are required.", "error");
      return;
    }

    if (startDate.trim() && endDate.trim() && endDate.trim() < startDate.trim()) {
      onToast("Invalid date range", "End date cannot precede start date.", "error");
      return;
    }

    const achievements = achievementsText
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);

    try {
      if (editingItem) {
        await updateEducationMutation.mutateAsync({
          id: editingItem.id,
          payload: {
            institution: institution.trim(),
            degree: degree.trim(),
            field_of_study: fieldOfStudy.trim() || undefined,
            location: location.trim() || undefined,
            start_date: startDate.trim() || undefined,
            end_date: endDate.trim() || undefined,
            grade: grade.trim() || undefined,
            description: description.trim() || undefined,
            achievements,
          },
        });
        onToast("Education updated", `Saved ${institution}.`, "success");
      } else {
        await addEducationMutation.mutateAsync({
          institution: institution.trim(),
          degree: degree.trim(),
          field_of_study: fieldOfStudy.trim() || undefined,
          location: location.trim() || undefined,
          start_date: startDate.trim() || undefined,
          end_date: endDate.trim() || undefined,
          grade: grade.trim() || undefined,
          description: description.trim() || undefined,
          achievements,
          order_index: (profile.education?.length || 0),
        });
        onToast("Education added", `Added ${degree} from ${institution}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save education.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, inst: string) => {
    try {
      await deleteEducationMutation.mutateAsync(id);
      onToast("Education deleted", `Removed education at ${inst}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete education record.";
      onToast("Delete failed", msg, "error");
    }
  };

  const educationList = profile.education || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Formal Education & Degrees
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Academic credentials, fields of study, graduation dates, honors, and notable coursework.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Education
        </Button>
      </div>

      {educationList.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.25rem" }}>
          {educationList.map((item) => (
            <Card key={item.id} style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <div className="source-icon">
                    <GraduationCap size={20} aria-hidden="true" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: "1.125rem", fontWeight: 700, color: "#09090b" }}>
                      {item.degree}
                    </h3>
                    <p style={{ fontSize: "0.8125rem", color: "#64748b" }}>
                      <strong>{item.institution}</strong>
                      {item.field_of_study ? ` · ${item.field_of_study}` : ""}
                      {item.location ? ` · ${item.location}` : ""}
                    </p>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  {(item.start_date || item.end_date) && (
                    <span className="experience-date">
                      {item.start_date || "—"} to {item.end_date || "Present"}
                    </span>
                  )}
                  <IconButton label={`Edit ${item.institution}`} onClick={() => handleOpenEdit(item)}>
                    <PencilSimple size={16} aria-hidden="true" />
                  </IconButton>
                  <IconButton label={`Delete ${item.institution}`} onClick={() => handleDelete(item.id, item.institution)}>
                    <Trash size={16} aria-hidden="true" />
                  </IconButton>
                </div>
              </div>

              {item.grade && (
                <div style={{ fontSize: "0.8125rem", color: "#475569" }}>
                  <strong>Grade / GPA:</strong> <Badge tone="neutral">{item.grade}</Badge>
                </div>
              )}

              {item.description && (
                <p style={{ fontSize: "0.875rem", color: "#334155", lineHeight: 1.5 }}>
                  {item.description}
                </p>
              )}

              {item.achievements && item.achievements.length > 0 && (
                <div>
                  <p style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "0.25rem" }}>
                    Honors & Activities
                  </p>
                  <ul className="bullet-list">
                    {item.achievements.map((ach, i) => (
                      <li key={i}>{ach}</li>
                    ))}
                  </ul>
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
          <GraduationCap size={32} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No education records added
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add university, college, or boot camp education to your master career profile.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Education Record
          </Button>
        </Card>
      )}

      {/* Modal */}
      <Modal
        open={modalOpen}
        title={editingItem ? "Edit Education" : "Add Education Record"}
        description="Add details of academic and formal educational programs."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addEducationMutation.isPending || updateEducationMutation.isPending}
            >
              {editingItem ? "Save Changes" : "Save Record"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div className="profile-form-grid">
            <Field
              label="Institution / University *"
              name="institution"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="e.g. Stanford University"
              required
            />
            <Field
              label="Degree *"
              name="degree"
              value={degree}
              onChange={(e) => setDegree(e.target.value)}
              placeholder="e.g. B.S. Computer Science"
              required
            />
            <Field
              label="Field of Study"
              name="field_of_study"
              value={fieldOfStudy}
              onChange={(e) => setFieldOfStudy(e.target.value)}
              placeholder="e.g. Software Engineering & AI"
            />
            <Field
              label="Location"
              name="edu_location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Stanford, CA"
            />
            <Field
              label="Start Year / Date"
              name="edu_start"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder="YYYY (e.g. 2018)"
            />
            <Field
              label="Graduation Year / Date"
              name="edu_end"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder="YYYY (e.g. 2022)"
            />
            <Field
              label="Grade / GPA (Optional)"
              name="grade"
              value={grade}
              onChange={(e) => setGrade(e.target.value)}
              placeholder="e.g. 3.9 GPA, First Class Honours"
            />
          </div>

          <TextareaField
            label="Program Description"
            name="edu_desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Key coursework, thesis topic, or focus areas..."
            rows={3}
          />

          <TextareaField
            label="Honors & Achievements (one per line)"
            name="edu_achievements"
            value={achievementsText}
            onChange={(e) => setAchievementsText(e.target.value)}
            placeholder="Dean's Honor List 2020-2022&#10;ACM Student Chapter President"
            rows={3}
          />
        </form>
      </Modal>
    </div>
  );
}
