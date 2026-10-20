"use client";

import {
  Bell,
  Briefcase,
  CalendarCheck,
  Check,
  CheckCircle,
  Copy,
  Cpu,
  EnvelopeSimple,
  Eye,
  Lightning,
  LinkedinLogo,
  MapPin,
  Pause,
  Play,
  Plus,
  ShieldCheck,
  ShieldWarning,
  Sparkle,
  Target,
  Trash,
  UserCheck,
  WarningCircle,
  PencilSimple,
} from "@phosphor-icons/react";
import React, { useEffect, useState } from "react";
import { agentApi } from "@/services/agent/agent.api";
import {
  AgentDailyReport,
  ApplicationRecord,
  DiscoveredJob,
  JobSearchProfile,
  QAMemoryBankItem,
  RecruiterOutreach,
} from "@/types/agent";
import { Badge, Button, Card, SectionHeading } from "@/components/ui";

interface AgentDashboardProps {
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function AgentDashboardView({ onToast }: AgentDashboardProps) {
  const [profile, setProfile] = useState<JobSearchProfile | null>(null);
  const [jobs, setJobs] = useState<DiscoveredJob[]>([]);
  const [applications, setApplications] = useState<ApplicationRecord[]>([]);
  const [outreach, setOutreach] = useState<RecruiterOutreach[]>([]);
  const [qaItems, setQaItems] = useState<QAMemoryBankItem[]>([]);
  const [latestReport, setLatestReport] = useState<AgentDailyReport | null>(null);

  const [loading, setLoading] = useState(true);
  const [runningAgent, setRunningAgent] = useState(false);
  const [activeTab, setActiveTab] = useState<"briefing" | "jobs" | "applications" | "outreach" | "qa" | "preferences">("briefing");
  const [selectedScreenshot, setSelectedScreenshot] = useState<string | null>(null);

  // New QA Item Modal State
  const [newQaCategory, setNewQaCategory] = useState("custom");
  const [newQaPattern, setNewQaPattern] = useState("");
  const [newQaAnswer, setNewQaAnswer] = useState("");

  // Preferences Editing State
  const [isEditingPreferences, setIsEditingPreferences] = useState(false);
  const [editLocations, setEditLocations] = useState("");
  const [editRoles, setEditRoles] = useState("");
  const [editSkills, setEditSkills] = useState("");
  const [editDailyCap, setEditDailyCap] = useState(10);
  const [editAutoSubmit, setEditAutoSubmit] = useState(false);
  const [editFresherMode, setEditFresherMode] = useState(true);
  const [savingPreferences, setSavingPreferences] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [profData, jobsData, appsData, outreachData, qaData, repData] = await Promise.all([
        agentApi.getProfile(),
        agentApi.listJobs(),
        agentApi.listApplications(),
        agentApi.listOutreach(),
        agentApi.listQABank(),
        agentApi.getLatestReport(),
      ]);
      setProfile(profData);
      setJobs(jobsData);
      setApplications(appsData);
      setOutreach(outreachData);
      setQaItems(qaData);
      setLatestReport(repData);
    } catch (err: any) {
      onToast("Error loading agent data", err?.message || "Failed to fetch agent state", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunNow = async () => {
    try {
      setRunningAgent(true);
      onToast("Agent Triggered", "Scanning job feeds and tailoring applications for Abhijith AT...", "info");
      const res = await agentApi.runNow(2);
      onToast("Run Complete", res.message, "success");
      await loadData();
    } catch (err: any) {
      onToast("Run Failed", err?.response?.data?.error?.message || err?.message || "Error running agent", "error");
    } finally {
      setRunningAgent(false);
    }
  };

  const handleEmergencyStopToggle = async () => {
    if (!profile) return;
    try {
      if (profile.emergency_stopped) {
        const resumed = await agentApi.resume();
        setProfile(resumed);
        onToast("Agent Resumed", "Automated daily morning runs and application pre-fills are now active.", "success");
      } else {
        const stopped = await agentApi.emergencyStop();
        setProfile(stopped);
        onToast("Emergency Stop Activated", "All automated external operations are immediately halted.", "error");
      }
    } catch (err: any) {
      onToast("Action Failed", err?.message, "error");
    }
  };

  const startEditingPreferences = () => {
    if (!profile) return;
    setEditLocations(profile.target_locations.join(", "));
    setEditRoles(profile.target_roles.join(", "));
    setEditSkills(profile.primary_skills.join(", "));
    setEditDailyCap(profile.daily_application_cap);
    setEditAutoSubmit(profile.auto_submit_enabled);
    setEditFresherMode(profile.fresher_mode);
    setIsEditingPreferences(true);
  };

  const handleSavePreferences = async () => {
    try {
      setSavingPreferences(true);
      const locations = editLocations
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const roles = editRoles
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const skills = editSkills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const updated = await agentApi.updateProfile({
        target_locations: locations,
        target_roles: roles,
        primary_skills: skills,
        daily_application_cap: editDailyCap,
        auto_submit_enabled: editAutoSubmit,
        fresher_mode: editFresherMode,
      });
      setProfile(updated);
      setIsEditingPreferences(false);
      onToast("Preferences Saved", "Search locations, roles, and automation rules updated successfully.", "success");
    } catch (err: any) {
      onToast("Save Failed", err?.response?.data?.error?.message || err?.message || "Failed to update preferences", "error");
    } finally {
      setSavingPreferences(false);
    }
  };

  const addLocationPreset = (preset: string) => {
    const current = editLocations
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!current.includes(preset)) {
      current.push(preset);
      setEditLocations(current.join(", "));
    }
  };

  const handleApplySingleJob = async (jobId: string) => {
    try {
      onToast("Processing Application", "Generating zero-hallucination CV & cover letter...", "info");
      const app = await agentApi.applyToJob(jobId);
      onToast("Application Ready", `Status: ${app.status}. Screenshot recorded.`, "success");
      await loadData();
    } catch (err: any) {
      onToast("Application Failed", err?.response?.data?.error?.message || err?.message, "error");
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    onToast("Copied to Clipboard", `${label} copied and ready to paste.`, "success");
  };

  const handleAddQaItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQaPattern || !newQaAnswer) return;
    try {
      await agentApi.createQAItem({
        category: newQaCategory,
        question_pattern: newQaPattern,
        answer_value: newQaAnswer,
      });
      setNewQaPattern("");
      setNewQaAnswer("");
      onToast("QA Item Saved", "New verified answer added to memory bank.", "success");
      const updated = await agentApi.listQABank();
      setQaItems(updated);
    } catch (err: any) {
      onToast("Failed to save QA item", err?.message, "error");
    }
  };

  const handleDeleteQaItem = async (id: string) => {
    try {
      await agentApi.deleteQAItem(id);
      setQaItems((prev) => prev.filter((item) => item.id !== id));
      onToast("Item Deleted", "Removed from QA memory bank.", "info");
    } catch (err: any) {
      onToast("Delete Failed", err?.message, "error");
    }
  };

  if (loading) {
    return (
      <div className="page-frame" style={{ padding: "40px 0", textAlign: "center" }}>
        <p>Loading Personal Autonomous Career Agent...</p>
      </div>
    );
  }

  return (
    <div className="page-frame">
      {/* Header View */}
      <div className="view-title" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span className="eyebrow" style={{ margin: 0 }}>Candidate: Abhijith AT</span>
            {profile?.emergency_stopped ? (
              <Badge tone="red">Emergency Stopped</Badge>
            ) : (
              <Badge tone="green">Autonomous Scheduler: 07:00 AM IST Active</Badge>
            )}
          </div>
          <h1 style={{ fontSize: "28px", fontWeight: "bold", margin: "4px 0" }}>Autonomous Career Agent</h1>
          <p style={{ color: "#64748b", margin: 0 }}>
            End-to-end automated job discovery, fresher-friendly matching, Playwright application pre-fill, and recruiter outreach.
          </p>
        </div>

        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <Button
            variant={profile?.emergency_stopped ? "secondary" : "danger"}
            icon={profile?.emergency_stopped ? <Play size={16} /> : <ShieldWarning size={16} />}
            onClick={handleEmergencyStopToggle}
          >
            {profile?.emergency_stopped ? "Resume Agent" : "Emergency Stop"}
          </Button>

          <Button
            variant="primary"
            icon={<Lightning size={16} weight="bold" />}
            loading={runningAgent}
            disabled={profile?.emergency_stopped}
            onClick={handleRunNow}
          >
            Run Agent Now
          </Button>
        </div>
      </div>

      {/* Metric Cards Strip */}
      <div className="dashboard-stats" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "24px" }}>
        <Card className="stat-card">
          <div className="stat-icon stat-blue"><Target size={22} /></div>
          <div className="stat-copy">
            <span>Jobs Discovered</span>
            <strong>{jobs.length}</strong>
            <small>Across ATS & Feeds</small>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-icon stat-green"><Sparkle size={22} /></div>
          <div className="stat-copy">
            <span>High-Fit (&gt;80%)</span>
            <strong>{jobs.filter((j) => j.match_score >= 80).length}</strong>
            <small>Fresher-Compatible</small>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-icon stat-purple"><Briefcase size={22} /></div>
          <div className="stat-copy">
            <span>Applications Tracked</span>
            <strong>{applications.length}</strong>
            <small>{applications.filter((a) => a.status === "submitted_confirmed").length} confirmed</small>
          </div>
        </Card>

        <Card className="stat-card">
          <div className="stat-icon stat-orange"><LinkedinLogo size={22} /></div>
          <div className="stat-copy">
            <span>Recruiter Leads</span>
            <strong>{outreach.length}</strong>
            <small>300-char notes drafted</small>
          </div>
        </Card>
      </div>

      {/* Tabs Navigation */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid #e2e8f0", paddingBottom: "12px", marginBottom: "24px", overflowX: "auto" }}>
        {[
          { id: "briefing", label: "Morning Briefing" },
          { id: "jobs", label: `Discovered Jobs (${jobs.length})` },
          { id: "applications", label: `Applications Pipeline (${applications.length})` },
          { id: "outreach", label: `Recruiter Outreach (${outreach.length})` },
          { id: "qa", label: `QA Memory Bank (${qaItems.length})` },
          { id: "preferences", label: "Search & Preferences" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              border: "none",
              background: activeTab === tab.id ? "#1e293b" : "transparent",
              color: activeTab === tab.id ? "#ffffff" : "#64748b",
              fontWeight: 600,
              cursor: "pointer",
              fontSize: "14px",
              transition: "all 0.15s ease",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: MORNING BRIEFING */}
      {activeTab === "briefing" && (
        <div>
          {latestReport ? (
            <Card style={{ padding: "24px", whiteSpace: "pre-line", lineHeight: "1.7" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", borderBottom: "1px solid #f1f5f9", paddingBottom: "12px" }}>
                <div>
                  <h2 style={{ fontSize: "20px", fontWeight: "bold", margin: 0 }}>Latest Daily Briefing</h2>
                  <small style={{ color: "#64748b" }}>Generated for {latestReport.run_date}</small>
                </div>
                <Badge tone="blue">Automated Run</Badge>
              </div>

              <div style={{ fontFamily: "inherit", fontSize: "14px", color: "#334155" }}>
                {latestReport.summary_markdown}
              </div>
            </Card>
          ) : (
            <Card style={{ padding: "40px", textAlign: "center" }}>
              <Sparkle size={32} weight="fill" style={{ color: "#3b82f6", marginBottom: "12px" }} />
              <h3>No morning report generated yet</h3>
              <p style={{ color: "#64748b", maxWidth: "500px", margin: "8px auto 16px" }}>
                Click &quot;Run Agent Now&quot; to perform an immediate discovery, evaluation, and application cycle, or wait for the 07:00 AM IST scheduled run.
              </p>
              <Button variant="primary" onClick={handleRunNow} loading={runningAgent}>
                Trigger First Run Now
              </Button>
            </Card>
          )}
        </div>
      )}

      {/* TAB 2: DISCOVERED JOBS */}
      {activeTab === "jobs" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {jobs.map((job) => (
            <Card key={job.id} style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <h3 style={{ margin: 0, fontSize: "17px", fontWeight: "bold" }}>{job.title}</h3>
                    {job.is_remote && <Badge tone="blue">Remote</Badge>}
                    {job.employment_type === "internship" && <Badge tone="purple">Internship</Badge>}
                  </div>
                  <p style={{ margin: "4px 0", color: "#475569", fontSize: "14px" }}>
                    <strong>{job.company_name}</strong> · <MapPin size={14} style={{ display: "inline" }} /> {job.location}
                  </p>
                </div>

                <div style={{ textAlign: "right" }}>
                  <span style={{ fontSize: "20px", fontWeight: "bold", color: job.match_score >= 80 ? "#16a34a" : "#ca8a04" }}>
                    {job.match_score}%
                  </span>
                  <div style={{ fontSize: "12px", color: "#64748b" }}>Fit Score</div>
                </div>
              </div>

              <p style={{ background: "#f8fafc", padding: "10px 14px", borderRadius: "6px", fontSize: "13px", color: "#334155", margin: "12px 0" }}>
                <strong>AI Reasoning:</strong> {job.fit_reasoning}
              </p>

              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "16px" }}>
                {job.extracted_skills.map((skill) => (
                  <Badge key={skill} tone="neutral">{skill}</Badge>
                ))}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #f1f5f9", paddingTop: "12px" }}>
                <a href={job.apply_url} target="_blank" rel="noreferrer" style={{ fontSize: "13px", color: "#2563eb", textDecoration: "none" }}>
                  View Original Listing ↗
                </a>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleApplySingleJob(job.id)}
                >
                  Tailor & Apply (Playwright)
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* TAB 3: APPLICATIONS PIPELINE */}
      {activeTab === "applications" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {applications.map((app) => (
            <Card key={app.id} style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <Badge tone={app.status === "submitted_confirmed" ? "green" : app.status === "prepared" ? "blue" : "amber"}>
                    {app.status}
                  </Badge>
                  <p style={{ margin: "6px 0 0", fontSize: "13px", color: "#64748b" }}>
                    Mode: {app.submission_mode} · Created: {new Date(app.created_at).toLocaleDateString()}
                  </p>
                </div>

                {app.portal_confirmation_code && (
                  <Badge tone="neutral">Ref: {app.portal_confirmation_code}</Badge>
                )}
              </div>

              {app.failure_reason && (
                <div style={{ background: "#fffbeb", border: "1px solid #fde68a", padding: "10px 14px", borderRadius: "6px", fontSize: "13px", color: "#92400e", marginBottom: "12px" }}>
                  {app.failure_reason}
                </div>
              )}

              <div style={{ display: "flex", gap: "12px", alignItems: "center", borderTop: "1px solid #f1f5f9", paddingTop: "12px" }}>
                {app.screenshot_url && (
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={<Eye size={15} />}
                    onClick={() => {
                      setSelectedScreenshot(app.screenshot_url || null);
                      onToast("Screenshot Recorded", `Audit image stored at ${app.screenshot_url}`, "info");
                    }}
                  >
                    View Submission Audit
                  </Button>
                )}

                <Button
                  variant="quiet"
                  size="sm"
                  icon={<Copy size={15} />}
                  onClick={() => copyToClipboard(`https://4bjith.github.io/Portfolio-Website/`, "Portfolio URL")}
                >
                  Copy Candidate Links
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* TAB 4: RECRUITER OUTREACH STUDIO */}
      {activeTab === "outreach" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {outreach.map((item) => (
            <Card key={item.id} style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "bold" }}>
                    {item.company_name} — {item.contact_name}
                  </h3>
                  <p style={{ margin: "2px 0 0", color: "#64748b", fontSize: "13px" }}>{item.contact_title}</p>
                </div>

                <Badge tone={item.channel === "linkedin" ? "blue" : "purple"}>
                  {item.channel === "linkedin" ? "LinkedIn 300-Char Note" : "Executive Recruiter Email"}
                </Badge>
              </div>

              <div style={{ background: "#f8fafc", padding: "12px 16px", borderRadius: "8px", fontSize: "13px", lineHeight: "1.6", color: "#334155", margin: "12px 0", whiteSpace: "pre-line" }}>
                {item.message_content}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "12px", color: "#64748b" }}>
                  Status: <strong>{item.status}</strong>
                </span>

                <div style={{ display: "flex", gap: "8px" }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={<Copy size={15} />}
                    onClick={() => copyToClipboard(item.message_content, "Recruiter Message")}
                  >
                    Copy Message
                  </Button>

                  {item.profile_url && (
                    <a
                      href={item.profile_url}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        padding: "6px 12px",
                        borderRadius: "6px",
                        background: "#0077b5",
                        color: "#fff",
                        textDecoration: "none",
                        fontSize: "13px",
                        fontWeight: 600,
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <LinkedinLogo size={16} /> Open LinkedIn
                    </a>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* TAB 5: QA MEMORY BANK */}
      {activeTab === "qa" && (
        <div>
          <Card style={{ padding: "20px", marginBottom: "24px" }}>
            <h3 style={{ margin: "0 0 12px 0", fontSize: "16px", fontWeight: "bold" }}>Add Verified QA Memory Pattern</h3>
            <form onSubmit={handleAddQaItem} style={{ display: "grid", gridTemplateColumns: "1fr 2fr 3fr auto", gap: "12px", alignItems: "center" }}>
              <select
                value={newQaCategory}
                onChange={(e) => setNewQaCategory(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "13px" }}
              >
                <option value="work_authorization">Work Auth</option>
                <option value="notice_period">Notice Period</option>
                <option value="compensation">Compensation</option>
                <option value="relocation">Relocation</option>
                <option value="custom">Custom</option>
              </select>

              <input
                type="text"
                placeholder="Question keyword (e.g. sponsorship, notice)"
                value={newQaPattern}
                onChange={(e) => setNewQaPattern(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "13px" }}
                required
              />

              <input
                type="text"
                placeholder="Truthful verified answer"
                value={newQaAnswer}
                onChange={(e) => setNewQaAnswer(e.target.value)}
                style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "13px" }}
                required
              />

              <Button variant="primary" size="sm" type="submit" icon={<Plus size={15} />}>
                Add Answer
              </Button>
            </form>
          </Card>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {qaItems.map((item) => (
              <Card key={item.id} style={{ padding: "16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <Badge tone="neutral">{item.category}</Badge>
                    <strong style={{ fontSize: "14px" }}>Pattern: &quot;{item.question_pattern}&quot;</strong>
                  </div>
                  <p style={{ margin: 0, color: "#334155", fontSize: "13px" }}>
                    <strong>Answer:</strong> {item.answer_value}
                  </p>
                </div>

                <button
                  onClick={() => handleDeleteQaItem(item.id)}
                  style={{ background: "transparent", border: "none", color: "#ef4444", cursor: "pointer", padding: "6px" }}
                  title="Delete verified answer"
                >
                  <Trash size={18} />
                </button>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* TAB 6: PREFERENCES */}
      {activeTab === "preferences" && profile && (
        <Card style={{ padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "bold", margin: 0 }}>Candidate Search Configuration</h3>
              <p style={{ margin: "4px 0 0", fontSize: "13px", color: "#64748b" }}>
                Target roles, South Indian tech locations, skill verification, and automation safety rules.
              </p>
            </div>
            {!isEditingPreferences ? (
              <Button
                variant="secondary"
                size="sm"
                onClick={startEditingPreferences}
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              >
                <PencilSimple size={15} /> Edit Preferences
              </Button>
            ) : (
              <div style={{ display: "flex", gap: "8px" }}>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsEditingPreferences(false)}
                  disabled={savingPreferences}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSavePreferences}
                  disabled={savingPreferences}
                >
                  {savingPreferences ? "Saving..." : "Save Preferences"}
                </Button>
              </div>
            )}
          </div>

          {!isEditingPreferences ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                  Target Developer Roles
                </label>
                <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", fontSize: "13px", lineHeight: "1.6" }}>
                  {profile.target_roles.join(", ")}
                </div>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                  Target Locations (Remote & South India)
                </label>
                <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", fontSize: "13px", lineHeight: "1.6" }}>
                  {profile.target_locations.join(", ")}
                </div>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                  Primary Verified Skills
                </label>
                <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", fontSize: "13px", lineHeight: "1.6" }}>
                  {profile.primary_skills.join(", ")}
                </div>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                  Automation Rules
                </label>
                <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "6px", fontSize: "13px", lineHeight: "1.6" }}>
                  <div>Daily Application Cap: <strong>{profile.daily_application_cap}</strong></div>
                  <div>Schedule: <strong>{profile.cron_schedule} (07:00 AM IST)</strong></div>
                  <div>Mode: <strong>{profile.auto_submit_enabled ? "Autonomous Submit" : "Supervised (1-Click Approval)"}</strong></div>
                  <div>Fresher Friendliness: <strong>{profile.fresher_mode ? "Active" : "Disabled"}</strong></div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
                  Target Locations (Comma-separated)
                </label>
                <input
                  type="text"
                  value={editLocations}
                  onChange={(e) => setEditLocations(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "6px",
                    border: "1px solid #cbd5e1",
                    fontSize: "13px",
                    background: "#ffffff",
                  }}
                  placeholder="e.g. Remote, Bangalore, Bengaluru, Karnataka, Hyderabad, Telangana, Chennai, Kochi"
                />
                <div style={{ marginTop: "8px", display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", fontWeight: 600, color: "#64748b" }}>Quick Add South India Hubs:</span>
                  {[
                    "Bangalore",
                    "Bengaluru",
                    "Karnataka",
                    "Hyderabad",
                    "Telangana",
                    "Chennai",
                    "Coimbatore",
                    "Tamil Nadu",
                    "Kochi",
                    "Kozhikode",
                    "Kannur",
                    "Kerala",
                    "Remote",
                  ].map((preset) => (
                    <button
                      key={preset}
                      type="button"
                      onClick={() => addLocationPreset(preset)}
                      style={{
                        padding: "3px 8px",
                        borderRadius: "12px",
                        fontSize: "11px",
                        background: "#f1f5f9",
                        border: "1px solid #e2e8f0",
                        color: "#334155",
                        cursor: "pointer",
                      }}
                    >
                      + {preset}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
                  Target Developer Roles (Comma-separated)
                </label>
                <input
                  type="text"
                  value={editRoles}
                  onChange={(e) => setEditRoles(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "6px",
                    border: "1px solid #cbd5e1",
                    fontSize: "13px",
                    background: "#ffffff",
                  }}
                  placeholder="e.g. MERN Stack Developer, React Developer, Full Stack Developer, Junior Software Engineer"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
                  Primary Verified Skills (Comma-separated)
                </label>
                <input
                  type="text"
                  value={editSkills}
                  onChange={(e) => setEditSkills(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "6px",
                    border: "1px solid #cbd5e1",
                    fontSize: "13px",
                    background: "#ffffff",
                  }}
                  placeholder="e.g. JavaScript, React, Node.js, Express.js, MongoDB, REST APIs, Git"
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
                    Daily Application Cap
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={50}
                    value={editDailyCap}
                    onChange={(e) => setEditDailyCap(parseInt(e.target.value) || 10)}
                    style={{
                      width: "100%",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid #cbd5e1",
                      fontSize: "13px",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#334155", marginBottom: "6px" }}>
                    Submission Mode
                  </label>
                  <select
                    value={editAutoSubmit ? "autonomous" : "supervised"}
                    onChange={(e) => setEditAutoSubmit(e.target.value === "autonomous")}
                    style={{
                      width: "100%",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid #cbd5e1",
                      fontSize: "13px",
                      background: "#ffffff",
                    }}
                  >
                    <option value="supervised">Supervised Mode (Pre-fills & Awaits 1-Click Submit)</option>
                    <option value="autonomous">Autonomous Mode (Direct Auto-Submission)</option>
                  </select>
                </div>
              </div>

              <div style={{ display: "flex", gap: "20px", marginTop: "4px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={editFresherMode}
                    onChange={(e) => setEditFresherMode(e.target.checked)}
                  />
                  <span><strong>Fresher-Friendly Evaluation Active</strong> (evaluates project portfolio & internships)</span>
                </label>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
