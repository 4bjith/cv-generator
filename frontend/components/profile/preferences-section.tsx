"use client";

import { useState } from "react";
import { Check, PencilSimple, X } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, SelectField } from "@/components/ui";
import { useUpdateCareerPreferences } from "@/hooks/use-profile";
import {
  AvailabilityStatus,
  CandidateProfileData,
  RemotePreference,
} from "@/types/profile";

interface PreferencesSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function PreferencesSection({ profile, onToast }: PreferencesSectionProps) {
  const prefs = profile.career_preferences;

  const [editing, setEditing] = useState(false);
  const [targetRoles, setTargetRoles] = useState<string[]>(prefs?.target_roles || []);
  const [newRole, setNewRole] = useState("");
  const [targetIndustries, setTargetIndustries] = useState<string[]>(prefs?.target_industries || []);
  const [newIndustry, setNewIndustry] = useState("");
  const [preferredLocations, setPreferredLocations] = useState<string[]>(prefs?.preferred_locations || []);
  const [newLocation, setNewLocation] = useState("");
  const [remotePref, setRemotePref] = useState<RemotePreference>(
    (prefs?.remote_preference as RemotePreference) || "remote"
  );
  const [availability, setAvailability] = useState<AvailabilityStatus>(
    (prefs?.availability_status as AvailabilityStatus) || "open_to_opportunities"
  );
  const [availableFrom, setAvailableFrom] = useState(prefs?.available_from || "");
  const [noticePeriod, setNoticePeriod] = useState(prefs?.notice_period_days?.toString() || "");

  const updatePreferencesMutation = useUpdateCareerPreferences();

  const handleAddRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRole.trim()) return;
    if (!targetRoles.includes(newRole.trim())) {
      setTargetRoles([...targetRoles, newRole.trim()]);
    }
    setNewRole("");
  };

  const handleRemoveRole = (role: string) => {
    setTargetRoles(targetRoles.filter((r) => r !== role));
  };

  const handleAddIndustry = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newIndustry.trim()) return;
    if (!targetIndustries.includes(newIndustry.trim())) {
      setTargetIndustries([...targetIndustries, newIndustry.trim()]);
    }
    setNewIndustry("");
  };

  const handleRemoveIndustry = (ind: string) => {
    setTargetIndustries(targetIndustries.filter((i) => i !== ind));
  };

  const handleAddLocation = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLocation.trim()) return;
    if (!preferredLocations.includes(newLocation.trim())) {
      setPreferredLocations([...preferredLocations, newLocation.trim()]);
    }
    setNewLocation("");
  };

  const handleRemoveLocation = (loc: string) => {
    setPreferredLocations(preferredLocations.filter((l) => l !== loc));
  };

  const handleSave = async () => {
    const parsedNotice = noticePeriod.trim() ? parseInt(noticePeriod, 10) : undefined;
    try {
      await updatePreferencesMutation.mutateAsync({
        target_roles: targetRoles,
        target_industries: targetIndustries,
        preferred_locations: preferredLocations,
        remote_preference: remotePref,
        availability_status: availability,
        available_from: availableFrom.trim() || undefined,
        notice_period_days: parsedNotice,
      });
      setEditing(false);
      onToast("Preferences saved", "Your job search and workplace preferences were updated.", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update preferences.";
      onToast("Save failed", msg, "error");
    }
  };

  return (
    <Card style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div className="card-heading">
        <div>
          <p className="eyebrow">Job Search & Workplace Context</p>
          <h2>Career Preferences</h2>
        </div>
        <Button
          variant={editing ? "primary" : "secondary"}
          size="sm"
          onClick={editing ? handleSave : () => setEditing(true)}
          loading={updatePreferencesMutation.isPending}
          icon={editing ? <Check size={16} aria-hidden="true" /> : <PencilSimple size={16} aria-hidden="true" />}
        >
          {editing ? "Save Preferences" : "Edit Preferences"}
        </Button>
      </div>

      <p style={{ fontSize: "0.8125rem", color: "#64748b", marginTop: "-0.5rem" }}>
        Career preferences represent your search intentions and work parameters. They guide application matching
        and interview preparation without appearing directly on standard CV templates.
      </p>

      <div className="profile-form-grid">
        <SelectField
          label="Remote & Workplace Preference"
          name="remote_pref"
          value={remotePref}
          disabled={!editing}
          onChange={(e) => setRemotePref(e.target.value as RemotePreference)}
        >
          <option value="remote">Remote Only</option>
          <option value="hybrid">Hybrid</option>
          <option value="onsite">On-site</option>
          <option value="flexible">Flexible / Any</option>
        </SelectField>

        <SelectField
          label="Availability Status"
          name="availability_status"
          value={availability}
          disabled={!editing}
          onChange={(e) => setAvailability(e.target.value as AvailabilityStatus)}
        >
          <option value="actively_looking">Actively Looking</option>
          <option value="open_to_opportunities">Open to Opportunities</option>
          <option value="not_looking">Not Looking</option>
        </SelectField>

        <Field
          label="Available From"
          name="available_from"
          value={availableFrom}
          readOnly={!editing}
          onChange={(e) => setAvailableFrom(e.target.value)}
          placeholder="e.g. Immediately, 2026-11-01"
        />

        <Field
          label="Notice Period (Days)"
          name="notice_period"
          type="number"
          min="0"
          value={noticePeriod}
          readOnly={!editing}
          onChange={(e) => setNoticePeriod(e.target.value)}
          placeholder="e.g. 30"
        />
      </div>

      {/* Target Roles */}
      <div>
        <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
          Target Roles
        </label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {targetRoles.map((role) => (
            <Badge key={role} tone="blue">
              {role}
              {editing && (
                <button
                  type="button"
                  onClick={() => handleRemoveRole(role)}
                  style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                  aria-label={`Remove ${role}`}
                >
                  <X size={12} aria-hidden="true" />
                </button>
              )}
            </Badge>
          ))}
          {targetRoles.length === 0 && !editing && (
            <span style={{ fontSize: "0.8125rem", color: "#94a3b8", fontStyle: "italic" }}>
              No target roles specified.
            </span>
          )}
        </div>
        {editing && (
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
            <input
              className="input"
              placeholder="e.g. Staff Frontend Engineer, Principal UI Architect"
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleAddRole(e);
                }
              }}
            />
            <Button size="sm" variant="secondary" onClick={handleAddRole}>
              Add Role
            </Button>
          </div>
        )}
      </div>

      {/* Target Industries */}
      <div>
        <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
          Target Industries & Domains
        </label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {targetIndustries.map((ind) => (
            <Badge key={ind} tone="purple">
              {ind}
              {editing && (
                <button
                  type="button"
                  onClick={() => handleRemoveIndustry(ind)}
                  style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                  aria-label={`Remove ${ind}`}
                >
                  <X size={12} aria-hidden="true" />
                </button>
              )}
            </Badge>
          ))}
          {targetIndustries.length === 0 && !editing && (
            <span style={{ fontSize: "0.8125rem", color: "#94a3b8", fontStyle: "italic" }}>
              No target industries specified.
            </span>
          )}
        </div>
        {editing && (
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
            <input
              className="input"
              placeholder="e.g. AI Tools, Enterprise SaaS, Developer Platforms"
              value={newIndustry}
              onChange={(e) => setNewIndustry(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleAddIndustry(e);
                }
              }}
            />
            <Button size="sm" variant="secondary" onClick={handleAddIndustry}>
              Add Industry
            </Button>
          </div>
        )}
      </div>

      {/* Preferred Locations */}
      <div>
        <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
          Preferred Geographical Locations
        </label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {preferredLocations.map((loc) => (
            <Badge key={loc} tone="neutral">
              {loc}
              {editing && (
                <button
                  type="button"
                  onClick={() => handleRemoveLocation(loc)}
                  style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                  aria-label={`Remove ${loc}`}
                >
                  <X size={12} aria-hidden="true" />
                </button>
              )}
            </Badge>
          ))}
          {preferredLocations.length === 0 && !editing && (
            <span style={{ fontSize: "0.8125rem", color: "#94a3b8", fontStyle: "italic" }}>
              No preferred locations specified.
            </span>
          )}
        </div>
        {editing && (
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
            <input
              className="input"
              placeholder="e.g. San Francisco, CA, London, UK, Remote Worldwide"
              value={newLocation}
              onChange={(e) => setNewLocation(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleAddLocation(e);
                }
              }}
            />
            <Button size="sm" variant="secondary" onClick={handleAddLocation}>
              Add Location
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}
