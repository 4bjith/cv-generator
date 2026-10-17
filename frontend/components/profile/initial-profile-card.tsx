"use client";

import { useState } from "react";
import { Sparkle, ArrowRight } from "@phosphor-icons/react";
import { Button, Card, Field, SelectField, TextareaField } from "@/components/ui";
import { useCreateCandidateProfile } from "@/hooks/use-profile";
import { CareerLevel } from "@/types/profile";

interface InitialProfileCardProps {
  initialName?: string;
  initialEmail?: string;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function InitialProfileCard({
  initialName = "",
  initialEmail = "",
  onToast,
}: InitialProfileCardProps) {
  const nameParts = initialName.trim().split(" ");
  const defaultFirstName = nameParts[0] || "";
  const defaultLastName = nameParts.slice(1).join(" ") || "";

  const [firstName, setFirstName] = useState(defaultFirstName);
  const [lastName, setLastName] = useState(defaultLastName);
  const [headline, setHeadline] = useState("");
  const [primaryTitle, setPrimaryTitle] = useState("");
  const [careerLevel, setCareerLevel] = useState<CareerLevel>("mid");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [summary, setSummary] = useState("");

  const createProfileMutation = useCreateCandidateProfile();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstName.trim()) {
      onToast("First name required", "Please enter your first name to create your profile.", "error");
      return;
    }

    try {
      await createProfileMutation.mutateAsync({
        first_name: firstName.trim(),
        last_name: lastName.trim() || undefined,
        professional_headline: headline.trim() || undefined,
        primary_title: primaryTitle.trim() || undefined,
        career_level: careerLevel,
        email: initialEmail || undefined,
        city: city.trim() || undefined,
        country: country.trim() || undefined,
        base_summary: summary.trim() || undefined,
      });
      onToast("Profile initialized", "Your master career knowledge base is ready to customize.", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create profile.";
      onToast("Creation failed", msg, "error");
    }
  };

  return (
    <Card className="onboarding-card">
      <div className="card-heading">
        <div>
          <p className="eyebrow">Master Career Knowledge Base</p>
          <h2>Initialize Candidate Profile</h2>
        </div>
        <span className="panel-kicker-icon">
          <Sparkle size={20} weight="fill" className="text-blue-600" aria-hidden="true" />
        </span>
      </div>
      <p className="text-slate-600 text-sm -mt-2">
        Your Candidate Profile is the verified source of truth for your skills, projects, and work history.
        Fill in your basic information below to start building your career knowledge base.
      </p>

      <form onSubmit={handleSubmit} className="profile-form-grid" style={{ marginTop: "1rem" }}>
        <Field
          label="First Name *"
          name="first_name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          placeholder="e.g. Aarav"
          required
        />
        <Field
          label="Last Name"
          name="last_name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          placeholder="e.g. Mehta"
        />
        <Field
          label="Professional Headline"
          name="headline"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
          placeholder="e.g. Senior Frontend Engineer & UI Architect"
        />
        <Field
          label="Primary Role / Title"
          name="primary_title"
          value={primaryTitle}
          onChange={(e) => setPrimaryTitle(e.target.value)}
          placeholder="e.g. Frontend Engineer"
        />
        <SelectField
          label="Career Level"
          name="career_level"
          value={careerLevel}
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
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
          <Field
            label="City"
            name="city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="e.g. Bengaluru"
          />
          <Field
            label="Country"
            name="country"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="e.g. India"
          />
        </div>
        <div style={{ gridColumn: "1 / -1" }}>
          <TextareaField
            label="Base Professional Summary"
            name="summary"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Write a concise overview of your career background, specializations, and engineering philosophy..."
            rows={4}
          />
        </div>

        <div style={{ gridColumn: "1 / -1", display: "flex", justifyContent: "flex-end", marginTop: "1rem" }}>
          <Button
            type="submit"
            size="lg"
            loading={createProfileMutation.isPending}
            icon={<ArrowRight size={17} aria-hidden="true" />}
          >
            Create Master Profile
          </Button>
        </div>
      </form>
    </Card>
  );
}
