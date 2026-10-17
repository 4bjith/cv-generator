"use client";

import { useState } from "react";
import { Check, PencilSimple, X } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, SelectField, TextareaField } from "@/components/ui";
import { useUpdateCandidateProfile } from "@/hooks/use-profile";
import { CandidateProfileData, CareerLevel } from "@/types/profile";

interface ProfessionalIdentitySectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function ProfessionalIdentitySection({
  profile,
  onToast,
}: ProfessionalIdentitySectionProps) {
  const [editing, setEditing] = useState(false);
  const [primaryTitle, setPrimaryTitle] = useState(profile.primary_title || "");
  const [secondaryTitles, setSecondaryTitles] = useState<string[]>(profile.secondary_titles || []);
  const [newSecondaryTitle, setNewSecondaryTitle] = useState("");
  const [careerLevel, setCareerLevel] = useState<CareerLevel>((profile.career_level as CareerLevel) || "mid");
  const [industry, setIndustry] = useState(profile.industry || "");
  const [yearsExperience, setYearsExperience] = useState(profile.years_of_experience?.toString() || "");
  const [specializations, setSpecializations] = useState<string[]>(profile.specializations || []);
  const [newSpec, setNewSpec] = useState("");
  const [baseSummary, setBaseSummary] = useState(profile.base_summary || "");

  const updateProfileMutation = useUpdateCandidateProfile();

  const handleAddSecondaryTitle = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSecondaryTitle.trim()) return;
    if (!secondaryTitles.includes(newSecondaryTitle.trim())) {
      setSecondaryTitles([...secondaryTitles, newSecondaryTitle.trim()]);
    }
    setNewSecondaryTitle("");
  };

  const handleRemoveSecondaryTitle = (title: string) => {
    setSecondaryTitles(secondaryTitles.filter((t) => t !== title));
  };

  const handleAddSpec = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSpec.trim()) return;
    if (!specializations.includes(newSpec.trim())) {
      setSpecializations([...specializations, newSpec.trim()]);
    }
    setNewSpec("");
  };

  const handleRemoveSpec = (spec: string) => {
    setSpecializations(specializations.filter((s) => s !== spec));
  };

  const handleSave = async () => {
    try {
      const parsedYears = yearsExperience.trim() ? parseFloat(yearsExperience) : undefined;
      await updateProfileMutation.mutateAsync({
        primary_title: primaryTitle.trim() || undefined,
        secondary_titles: secondaryTitles,
        career_level: careerLevel,
        industry: industry.trim() || undefined,
        years_of_experience: parsedYears,
        specializations: specializations,
        base_summary: baseSummary.trim() || undefined,
      });
      setEditing(false);
      onToast("Identity & Summary Saved", "Your professional identity details were updated.", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update professional identity.";
      onToast("Save failed", msg, "error");
    }
  };

  return (
    <div className="profile-grid">
      {/* Professional Identity Card */}
      <Card>
        <div className="card-heading">
          <div>
            <p className="eyebrow">Professional Archetype</p>
            <h2>Role & Specializations</h2>
          </div>
          <Button
            variant={editing ? "primary" : "secondary"}
            size="sm"
            onClick={editing ? handleSave : () => setEditing(true)}
            loading={updateProfileMutation.isPending}
            icon={editing ? <Check size={16} aria-hidden="true" /> : <PencilSimple size={16} aria-hidden="true" />}
          >
            {editing ? "Save Changes" : "Edit Details"}
          </Button>
        </div>

        <div className="profile-form-grid">
          <Field
            label="Primary Job Title"
            name="primary_title"
            value={primaryTitle}
            readOnly={!editing}
            onChange={(e) => setPrimaryTitle(e.target.value)}
            placeholder="e.g. Lead Frontend Architect"
          />
          <SelectField
            label="Career Level"
            name="career_level"
            value={careerLevel}
            disabled={!editing}
            onChange={(e) => setCareerLevel(e.target.value as CareerLevel)}
          >
            <option value="student">Student</option>
            <option value="entry">Entry Level</option>
            <option value="junior">Junior</option>
            <option value="mid">Mid Level</option>
            <option value="senior">Senior</option>
            <option value="lead">Lead</option>
            <option value="manager">Manager</option>
            <option value="director">Director</option>
            <option value="executive">Executive</option>
          </SelectField>
          <Field
            label="Industry / Domain"
            name="industry"
            value={industry}
            readOnly={!editing}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g. B2B SaaS, FinTech, AI Tools"
          />
          <Field
            label="Total Years of Experience"
            name="years_experience"
            type="number"
            step="0.5"
            min="0"
            value={yearsExperience}
            readOnly={!editing}
            onChange={(e) => setYearsExperience(e.target.value)}
            placeholder="e.g. 5.5"
          />
        </div>

        {/* Secondary Titles */}
        <div style={{ marginTop: "1rem" }}>
          <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
            Secondary / Alternative Titles
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: editing ? "0.5rem" : 0 }}>
            {secondaryTitles.map((title) => (
              <Badge key={title} tone="blue">
                {title}
                {editing && (
                  <button
                    type="button"
                    onClick={() => handleRemoveSecondaryTitle(title)}
                    style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                    aria-label={`Remove ${title}`}
                  >
                    <X size={12} aria-hidden="true" />
                  </button>
                )}
              </Badge>
            ))}
            {secondaryTitles.length === 0 && !editing && (
              <span style={{ fontSize: "0.8125rem", color: "#94a3b8", fontStyle: "italic" }}>
                No secondary titles specified.
              </span>
            )}
          </div>
          {editing && (
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
              <input
                className="input"
                placeholder="Add alternative title e.g. Full Stack Engineer"
                value={newSecondaryTitle}
                onChange={(e) => setNewSecondaryTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddSecondaryTitle(e);
                  }
                }}
              />
              <Button size="sm" variant="secondary" onClick={handleAddSecondaryTitle}>
                Add
              </Button>
            </div>
          )}
        </div>

        {/* Specializations */}
        <div style={{ marginTop: "1rem" }}>
          <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
            Core Specializations & Subject Matter Areas
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: editing ? "0.5rem" : 0 }}>
            {specializations.map((spec) => (
              <Badge key={spec} tone="purple">
                {spec}
                {editing && (
                  <button
                    type="button"
                    onClick={() => handleRemoveSpec(spec)}
                    style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                    aria-label={`Remove ${spec}`}
                  >
                    <X size={12} aria-hidden="true" />
                  </button>
                )}
              </Badge>
            ))}
            {specializations.length === 0 && !editing && (
              <span style={{ fontSize: "0.8125rem", color: "#94a3b8", fontStyle: "italic" }}>
                No specializations added yet.
              </span>
            )}
          </div>
          {editing && (
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
              <input
                className="input"
                placeholder="Add specialization e.g. Design Systems, High-Concurrency APIs"
                value={newSpec}
                onChange={(e) => setNewSpec(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddSpec(e);
                  }
                }}
              />
              <Button size="sm" variant="secondary" onClick={handleAddSpec}>
                Add
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Base Professional Summary Card */}
      <Card>
        <div className="card-heading">
          <div>
            <p className="eyebrow">Canonical Story</p>
            <h2>Base Professional Summary</h2>
          </div>
        </div>
        <p style={{ fontSize: "0.8125rem", color: "#64748b", marginBottom: "0.75rem" }}>
          This is your master professional narrative. Tailored summaries for job applications will be derived
          from this baseline without altering your permanent facts.
        </p>
        <TextareaField
          label="Master Summary"
          name="base_summary"
          value={baseSummary}
          readOnly={!editing}
          onChange={(e) => setBaseSummary(e.target.value)}
          placeholder="Craft a detailed summary outlining your career focus, technical leadership, and core accomplishments..."
          rows={10}
          hint={editing ? "Aim for at least 30 characters for high profile readiness." : undefined}
        />
      </Card>
    </div>
  );
}
