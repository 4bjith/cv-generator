"use client";

import { useState } from "react";
import {
  UserCircle,
  Briefcase,
  Code,
  GraduationCap,
  Certificate,
  Trophy,
  Translate,
  SlidersHorizontal,
  Trash,
  IdentificationCard,
  Folders,
  Sparkle,
} from "@phosphor-icons/react";
import { Button, Modal } from "@/components/ui";
import { ProfileSkeleton } from "@/components/skeletons";
import {
  useCandidateProfile,
  useDeleteCandidateProfile,
  useProfileStrength,
} from "@/hooks/use-profile";
import { InitialProfileCard } from "./initial-profile-card";
import { ProfileStrengthPanel } from "./profile-strength-panel";
import { PersonalInfoSection } from "./personal-info-section";
import { ProfessionalIdentitySection } from "./professional-identity-section";
import { ExperienceSection } from "./experience-section";
import { SkillsSection } from "./skills-section";
import { ProjectsSection } from "./projects-section";
import { EducationSection } from "./education-section";
import { CertificationsSection } from "./certifications-section";
import { AchievementsSection } from "./achievements-section";
import { LanguagesSection } from "./languages-section";
import { PreferencesSection } from "./preferences-section";
import { EvidenceSection } from "./evidence-section";
import { AppView } from "@/types";

type ProfileTab =
  | "personal"
  | "identity"
  | "experience"
  | "skills"
  | "projects"
  | "evidence"
  | "education"
  | "certifications"
  | "achievements"
  | "languages"
  | "preferences";

interface ProfileEditorProps {
  onNavigate?: (view: AppView) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  userName?: string;
  userEmail?: string;
}

const PROFILE_TABS: { id: ProfileTab; label: string; icon: React.ReactNode; badgeKey?: string }[] = [
  { id: "personal", label: "Identity & Links", icon: <UserCircle size={17} weight="bold" /> },
  { id: "identity", label: "Professional Identity", icon: <IdentificationCard size={17} weight="bold" /> },
  { id: "experience", label: "Work Experience", icon: <Briefcase size={17} weight="bold" /> },
  { id: "skills", label: "Skills & Mapping", icon: <Code size={17} weight="bold" /> },
  { id: "projects", label: "Projects", icon: <Folders size={17} weight="bold" /> },
  { id: "evidence", label: "Evidence Vault", icon: <Sparkle size={17} weight="bold" /> },
  { id: "education", label: "Education", icon: <GraduationCap size={17} weight="bold" /> },
  { id: "certifications", label: "Certifications", icon: <Certificate size={17} weight="bold" /> },
  { id: "achievements", label: "Achievements", icon: <Trophy size={17} weight="bold" /> },
  { id: "languages", label: "Languages", icon: <Translate size={17} weight="bold" /> },
  { id: "preferences", label: "Career Preferences", icon: <SlidersHorizontal size={17} weight="bold" /> },
];

export function ProfileEditor({ onNavigate, onToast, userName = "", userEmail = "" }: ProfileEditorProps) {
  const { data: profile, isLoading, error } = useCandidateProfile();
  const { data: strength } = useProfileStrength();
  const deleteProfileMutation = useDeleteCandidateProfile();

  const [activeTab, setActiveTab] = useState<ProfileTab>("personal");
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  // If candidate profile hasn't been created yet, show initialization onboarding card
  if (!profile || error) {
    return (
      <div className="page-frame">
        <div className="view-title">
          <div>
            <p className="eyebrow">Candidate Knowledge Base</p>
            <h1>Master Candidate Profile</h1>
            <p>Your master career knowledge base for all future CVs and applications.</p>
          </div>
        </div>
        <InitialProfileCard
          initialName={userName}
          initialEmail={userEmail}
          onToast={onToast}
        />
      </div>
    );
  }

  const handleDeleteProfile = async () => {
    try {
      await deleteProfileMutation.mutateAsync();
      setDeleteModalOpen(false);
      onToast("Profile deleted", "Your candidate profile has been reset.", "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete profile.";
      onToast("Delete failed", msg, "error");
    }
  };

  const candidateFullName = [profile.first_name, profile.last_name].filter(Boolean).join(" ") || "Candidate";

  return (
    <div className="page-frame">
      {/* Page Title / Header */}
      <div className="view-title">
        <div>
          <p className="eyebrow">Candidate Knowledge Base</p>
          <h1>{candidateFullName}</h1>
          <p>
            {profile.professional_headline ||
              profile.primary_title ||
              "Your evidence-backed source of truth for every career application."}
          </p>
        </div>
        <div className="view-title-actions" style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {onNavigate ? (
            <Button
              variant="ghost"
              size="sm"
              icon={<Sparkle size={16} weight="fill" />}
              onClick={() => onNavigate("dashboard")}
            >
              Dashboard
            </Button>
          ) : null}
          <Button
            variant="quiet"
            size="sm"
            icon={<Trash size={16} />}
            onClick={() => setDeleteModalOpen(true)}
          >
            Reset Profile
          </Button>
        </div>
      </div>

      {/* Profile Strength & Readiness Breakdown */}
      <ProfileStrengthPanel
        strength={strength}
        onNavigateSection={(tabId) => setActiveTab(tabId as ProfileTab)}
      />

      {/* Horizontal Nav Tabs */}
      <div
        className="workspace-tabs"
        role="tablist"
        style={{
          overflowX: "auto",
          whiteSpace: "nowrap",
          paddingBottom: "0.25rem",
          display: "flex",
          gap: "0.25rem",
        }}
      >
        {PROFILE_TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              className={isActive ? "active" : ""}
              onClick={() => setActiveTab(tab.id)}
              style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      <div className="profile-tab-content" style={{ marginTop: "1rem" }}>
        {activeTab === "personal" && (
          <PersonalInfoSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "identity" && (
          <ProfessionalIdentitySection profile={profile} onToast={onToast} />
        )}

        {activeTab === "experience" && (
          <ExperienceSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "skills" && (
          <SkillsSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "projects" && (
          <ProjectsSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "evidence" && (
          <EvidenceSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "education" && (
          <EducationSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "certifications" && (
          <CertificationsSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "achievements" && (
          <AchievementsSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "languages" && (
          <LanguagesSection profile={profile} onToast={onToast} />
        )}

        {activeTab === "preferences" && (
          <PreferencesSection profile={profile} onToast={onToast} />
        )}
      </div>

      {/* Confirm Profile Reset / Delete Modal */}
      <Modal
        open={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Reset Candidate Profile"
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.875rem", lineHeight: "1.5" }}>
            Are you sure you want to delete your entire Candidate Profile? This will remove all
            your stored work experiences, skills, projects, certifications, education, and career preferences.
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="secondary"
              loading={deleteProfileMutation.isPending}
              onClick={handleDeleteProfile}
              style={{ color: "var(--color-red, #dc2626)" }}
            >
              Delete Master Profile
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
