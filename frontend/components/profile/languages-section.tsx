"use client";

import { useState } from "react";
import { Plus, Trash, PencilSimple, Translate } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal, SelectField } from "@/components/ui";
import {
  useAddLanguage,
  useDeleteLanguage,
  useUpdateLanguage,
} from "@/hooks/use-profile";
import { CandidateLanguage, CandidateProfileData, LanguageProficiency } from "@/types/profile";

interface LanguagesSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const PROFICIENCY_LABELS: Record<string, string> = {
  basic: "Basic / Elementary",
  conversational: "Conversational",
  professional: "Professional Working",
  fluent: "Full Professional / Fluent",
  native: "Native or Bilingual",
};

const PROFICIENCY_TONES: Record<string, string> = {
  basic: "neutral",
  conversational: "blue",
  professional: "purple",
  fluent: "green",
  native: "green",
};

export function LanguagesSection({ profile, onToast }: LanguagesSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<CandidateLanguage | null>(null);

  const [name, setName] = useState("");
  const [proficiency, setProficiency] = useState<LanguageProficiency>("professional");

  const addLanguageMutation = useAddLanguage();
  const updateLanguageMutation = useUpdateLanguage();
  const deleteLanguageMutation = useDeleteLanguage();

  const handleOpenAdd = () => {
    setEditingItem(null);
    setName("");
    setProficiency("professional");
    setModalOpen(true);
  };

  const handleOpenEdit = (lang: CandidateLanguage) => {
    setEditingItem(lang);
    setName(lang.name);
    setProficiency((lang.proficiency as LanguageProficiency) || "professional");
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      onToast("Language name required", "Please enter a language name.", "error");
      return;
    }

    try {
      if (editingItem) {
        await updateLanguageMutation.mutateAsync({
          id: editingItem.id,
          payload: {
            name: name.trim(),
            proficiency,
          },
        });
        onToast("Language updated", `Saved ${name}.`, "success");
      } else {
        await addLanguageMutation.mutateAsync({
          name: name.trim(),
          proficiency,
        });
        onToast("Language added", `Added ${name}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save language.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, langName: string) => {
    try {
      await deleteLanguageMutation.mutateAsync(id);
      onToast("Language deleted", `Removed ${langName}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete language.";
      onToast("Delete failed", msg, "error");
    }
  };

  const languages = profile.languages || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Languages & Spoken Proficiencies
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Spoken and written language capabilities with verified proficiency ratings.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Language
        </Button>
      </div>

      {languages.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 18rem), 1fr))", gap: "1rem" }}>
          {languages.map((lang) => (
            <Card
              key={lang.id}
              style={{
                padding: "1.25rem 1.5rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <Translate size={22} className="text-blue-600 flex-shrink-0" aria-hidden="true" />
                <div>
                  <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#09090b" }}>
                    {lang.name}
                  </h3>
                  <Badge tone={PROFICIENCY_TONES[lang.proficiency] || "neutral"} style={{ marginTop: "0.25rem" }}>
                    {PROFICIENCY_LABELS[lang.proficiency] || lang.proficiency}
                  </Badge>
                </div>
              </div>

              <div style={{ display: "flex", gap: "0.25rem" }}>
                <IconButton label={`Edit ${lang.name}`} onClick={() => handleOpenEdit(lang)}>
                  <PencilSimple size={15} aria-hidden="true" />
                </IconButton>
                <IconButton label={`Delete ${lang.name}`} onClick={() => handleDelete(lang.id, lang.name)}>
                  <Trash size={15} aria-hidden="true" />
                </IconButton>
              </div>
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
          <Translate size={32} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No languages added
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add the languages you speak or write professionally.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Language
          </Button>
        </Card>
      )}

      {/* Modal */}
      <Modal
        open={modalOpen}
        title={editingItem ? "Edit Language" : "Add Language"}
        description="Add a language and your proficiency level."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addLanguageMutation.isPending || updateLanguageMutation.isPending}
            >
              {editingItem ? "Save Changes" : "Save Language"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Field
            label="Language Name *"
            name="lang_name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. English, Spanish, Japanese"
            required
          />
          <SelectField
            label="Proficiency Level *"
            name="lang_proficiency"
            value={proficiency}
            onChange={(e) => setProficiency(e.target.value as LanguageProficiency)}
          >
            <option value="basic">Basic / Elementary</option>
            <option value="conversational">Conversational</option>
            <option value="professional">Professional Working</option>
            <option value="fluent">Full Professional / Fluent</option>
            <option value="native">Native or Bilingual</option>
          </SelectField>
        </form>
      </Modal>
    </div>
  );
}
