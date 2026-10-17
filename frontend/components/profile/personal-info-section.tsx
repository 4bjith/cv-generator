"use client";

import { useState } from "react";
import { LinkSimple, Plus, Trash, PencilSimple, Check, Globe } from "@phosphor-icons/react";
import { Button, Card, Field, IconButton, Modal, SelectField } from "@/components/ui";
import {
  useAddLink,
  useDeleteLink,
  useUpdateCandidateProfile,
  useUpdateLink,
} from "@/hooks/use-profile";
import { CandidateLink, CandidateProfileData } from "@/types/profile";

interface PersonalInfoSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function PersonalInfoSection({ profile, onToast }: PersonalInfoSectionProps) {
  // Identity & Contact Editing State
  const [editingIdentity, setEditingIdentity] = useState(false);
  const [firstName, setFirstName] = useState(profile.first_name);
  const [lastName, setLastName] = useState(profile.last_name || "");
  const [preferredName, setPreferredName] = useState(profile.preferred_name || "");
  const [headline, setHeadline] = useState(profile.professional_headline || "");
  const [email, setEmail] = useState(profile.email || "");
  const [phone, setPhone] = useState(profile.phone || "");
  const [city, setCity] = useState(profile.city || "");
  const [state, setState] = useState(profile.state || "");
  const [country, setCountry] = useState(profile.country || "");
  const [countryCode, setCountryCode] = useState(profile.country_code || "");

  // Link Modal State
  const [linkModalOpen, setLinkModalOpen] = useState(false);
  const [editingLink, setEditingLink] = useState<CandidateLink | null>(null);
  const [linkType, setLinkType] = useState("github");
  const [linkLabel, setLinkLabel] = useState("");
  const [linkUrl, setLinkUrl] = useState("");

  const updateProfileMutation = useUpdateCandidateProfile();
  const addLinkMutation = useAddLink();
  const updateLinkMutation = useUpdateLink();
  const deleteLinkMutation = useDeleteLink();

  const handleSaveIdentity = async () => {
    if (!firstName.trim()) {
      onToast("First name required", "First name cannot be empty.", "error");
      return;
    }
    try {
      await updateProfileMutation.mutateAsync({
        first_name: firstName.trim(),
        last_name: lastName.trim() || undefined,
        preferred_name: preferredName.trim() || undefined,
        professional_headline: headline.trim() || undefined,
        email: email.trim() || undefined,
        phone: phone.trim() || undefined,
        city: city.trim() || undefined,
        state: state.trim() || undefined,
        country: country.trim() || undefined,
        country_code: countryCode.trim() || undefined,
      });
      setEditingIdentity(false);
      onToast("Personal Info Saved", "Your identity and contact information were updated.", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update personal info.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleOpenAddLink = () => {
    setEditingLink(null);
    setLinkType("github");
    setLinkLabel("");
    setLinkUrl("");
    setLinkModalOpen(true);
  };

  const handleOpenEditLink = (link: CandidateLink) => {
    setEditingLink(link);
    setLinkType(link.type);
    setLinkLabel(link.label);
    setLinkUrl(link.url);
    setLinkModalOpen(true);
  };

  const handleSaveLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!linkLabel.trim() || !linkUrl.trim()) {
      onToast("Missing fields", "Label and URL are required.", "error");
      return;
    }

    try {
      if (editingLink) {
        await updateLinkMutation.mutateAsync({
          id: editingLink.id,
          payload: {
            type: linkType,
            label: linkLabel.trim(),
            url: linkUrl.trim(),
          },
        });
        onToast("Link updated", `Updated ${linkLabel}.`, "success");
      } else {
        await addLinkMutation.mutateAsync({
          type: linkType,
          label: linkLabel.trim(),
          url: linkUrl.trim(),
          order_index: (profile.links?.length || 0),
        });
        onToast("Link added", `Added ${linkLabel}.`, "success");
      }
      setLinkModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save link.";
      onToast("Link error", msg, "error");
    }
  };

  const handleDeleteLink = async (id: string, label: string) => {
    try {
      await deleteLinkMutation.mutateAsync(id);
      onToast("Link deleted", `Removed ${label}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete link.";
      onToast("Delete failed", msg, "error");
    }
  };

  return (
    <div className="profile-grid">
      {/* Identity & Contact Card */}
      <Card>
        <div className="card-heading">
          <div>
            <p className="eyebrow">Identity & Contact Facts</p>
            <h2>Personal Context</h2>
          </div>
          <Button
            variant={editingIdentity ? "primary" : "secondary"}
            size="sm"
            onClick={editingIdentity ? handleSaveIdentity : () => setEditingIdentity(true)}
            loading={updateProfileMutation.isPending}
            icon={editingIdentity ? <Check size={16} aria-hidden="true" /> : <PencilSimple size={16} aria-hidden="true" />}
          >
            {editingIdentity ? "Save Changes" : "Edit Identity"}
          </Button>
        </div>

        <div className="profile-form-grid">
          <Field
            label="First Name *"
            name="first_name"
            value={firstName}
            readOnly={!editingIdentity}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <Field
            label="Last Name"
            name="last_name"
            value={lastName}
            readOnly={!editingIdentity}
            onChange={(e) => setLastName(e.target.value)}
          />
          <Field
            label="Preferred / Display Name"
            name="preferred_name"
            value={preferredName}
            readOnly={!editingIdentity}
            onChange={(e) => setPreferredName(e.target.value)}
            placeholder="e.g. Alex"
          />
          <Field
            label="Professional Headline"
            name="headline"
            value={headline}
            readOnly={!editingIdentity}
            onChange={(e) => setHeadline(e.target.value)}
            placeholder="e.g. Senior Frontend Engineer"
          />
          <Field
            label="Email Address"
            name="email"
            type="email"
            value={email}
            readOnly={!editingIdentity}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Field
            label="Phone Number"
            name="phone"
            value={phone}
            readOnly={!editingIdentity}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+1 (555) 000-0000"
          />
          <Field
            label="City"
            name="city"
            value={city}
            readOnly={!editingIdentity}
            onChange={(e) => setCity(e.target.value)}
            placeholder="e.g. San Francisco"
          />
          <Field
            label="State / Region"
            name="state"
            value={state}
            readOnly={!editingIdentity}
            onChange={(e) => setState(e.target.value)}
            placeholder="e.g. CA"
          />
          <Field
            label="Country"
            name="country"
            value={country}
            readOnly={!editingIdentity}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="e.g. United States"
          />
          <Field
            label="Country Code"
            name="country_code"
            value={countryCode}
            readOnly={!editingIdentity}
            onChange={(e) => setCountryCode(e.target.value)}
            placeholder="e.g. US"
          />
        </div>
      </Card>

      {/* Professional Links Card */}
      <Card>
        <div className="card-heading">
          <div>
            <p className="eyebrow">Public Evidence</p>
            <h2>Professional Links</h2>
          </div>
          <Button
            variant="secondary"
            size="sm"
            icon={<Plus size={16} aria-hidden="true" />}
            onClick={handleOpenAddLink}
          >
            Add Link
          </Button>
        </div>

        {profile.links && profile.links.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {profile.links.map((link) => (
              <div
                key={link.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.75rem 1rem",
                  backgroundColor: "#f8fafc",
                  borderRadius: "0.75rem",
                  border: "1px solid #e2e8f0",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", minWidth: 0 }}>
                  <Globe size={18} className="text-blue-600 flex-shrink-0" aria-hidden="true" />
                  <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
                    <span style={{ fontSize: "0.875rem", fontWeight: 600, color: "#09090b" }}>
                      {link.label}
                    </span>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        fontSize: "0.75rem",
                        color: "#2563eb",
                        textOverflow: "ellipsis",
                        overflow: "hidden",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {link.url}
                    </a>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", flexShrink: 0 }}>
                  <IconButton
                    label={`Edit ${link.label}`}
                    onClick={() => handleOpenEditLink(link)}
                  >
                    <PencilSimple size={15} aria-hidden="true" />
                  </IconButton>
                  <IconButton
                    label={`Delete ${link.label}`}
                    onClick={() => handleDeleteLink(link.id, link.label)}
                  >
                    <Trash size={15} aria-hidden="true" />
                  </IconButton>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div
            style={{
              padding: "2rem 1rem",
              textAlign: "center",
              backgroundColor: "#f8fafc",
              borderRadius: "0.75rem",
              border: "1px dashed #cbd5e1",
            }}
          >
            <LinkSimple size={24} className="text-slate-400 mx-auto mb-2" aria-hidden="true" />
            <p style={{ fontSize: "0.875rem", fontWeight: 600, color: "#334155" }}>
              No professional links added yet
            </p>
            <p style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
              Add your GitHub, LinkedIn, personal website, or portfolio.
            </p>
          </div>
        )}
      </Card>

      {/* Link Modal */}
      <Modal
        open={linkModalOpen}
        title={editingLink ? "Edit Professional Link" : "Add Professional Link"}
        description="Add generic or platform-specific professional web links."
        onClose={() => setLinkModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setLinkModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSaveLink}
              loading={addLinkMutation.isPending || updateLinkMutation.isPending}
            >
              {editingLink ? "Save Changes" : "Add Link"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSaveLink} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <SelectField
            label="Platform / Type"
            name="link_type"
            value={linkType}
            onChange={(e) => setLinkType(e.target.value)}
          >
            <option value="github">GitHub</option>
            <option value="linkedin">LinkedIn</option>
            <option value="portfolio">Portfolio</option>
            <option value="website">Personal Website</option>
            <option value="behance">Behance</option>
            <option value="dribbble">Dribbble</option>
            <option value="stackoverflow">Stack Overflow</option>
            <option value="kaggle">Kaggle</option>
            <option value="medium">Medium</option>
            <option value="other">Other</option>
          </SelectField>
          <Field
            label="Label *"
            name="link_label"
            value={linkLabel}
            onChange={(e) => setLinkLabel(e.target.value)}
            placeholder="e.g. GitHub Profile"
            required
          />
          <Field
            label="Destination URL *"
            name="link_url"
            type="url"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            placeholder="https://github.com/username"
            hint="Must start with https:// or http://"
            required
          />
        </form>
      </Modal>
    </div>
  );
}
