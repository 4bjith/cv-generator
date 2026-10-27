"use client";

import {
  Bell,
  BookOpenText,
  Briefcase,
  ChartLineUp,
  FileText,
  Gear,
  GithubLogo,
  House,
  Lightning,
  List,
  MagnifyingGlass,
  Plus,
  Sparkle,
  Target,
  UserCircle,
  X,
} from "@phosphor-icons/react";
import type { Icon } from "@phosphor-icons/react";
import { ReactNode, useState } from "react";
import { AppView } from "@/types";
import { Avatar, Button, IconButton } from "@/components/ui";

type NavItem = { id: AppView; label: string; icon: Icon };
type NavGroup = { label: string; items: NavItem[] };

const navGroups: NavGroup[] = [
  { label: "Workspace", items: [{ id: "dashboard", label: "Overview", icon: House }, { id: "agent", label: "Autonomous Agent", icon: Lightning }, { id: "profile", label: "Candidate Profile", icon: UserCircle }, { id: "projects", label: "Projects & GitHub", icon: GithubLogo }] },
  { label: "Application Studio", items: [{ id: "add-job", label: "Target Jobs", icon: Target }, { id: "job-analysis", label: "Job Analysis", icon: ChartLineUp }, { id: "cv-editor", label: "CV Editor", icon: FileText }, { id: "interview", label: "Interview Prep", icon: BookOpenText }] },
  { label: "Track", items: [{ id: "applications", label: "Applications", icon: Briefcase }, { id: "settings", label: "Settings", icon: Gear }] },
];

export function Brand({ compact = false, onClick }: { compact?: boolean; onClick?: () => void }) {
  return <button className={`brand ${compact ? "brand-compact" : ""}`} onClick={onClick} aria-label="Go to overview"><span className="brand-mark"><Sparkle size={17} weight="fill" aria-hidden="true" /></span><span className="brand-name">{compact ? "ACM" : "AI CV Maker"}</span></button>;
}

export function WorkspaceShell({
  view,
  onNavigate,
  children,
  onSignOut,
  userName = "Aarav Mehta",
  userEmail = "Personal account",
}: {
  view: AppView;
  onNavigate: (view: AppView) => void;
  children: ReactNode;
  onSignOut: () => void;
  userName?: string;
  userEmail?: string;
}) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const currentLabel =
    navGroups.flatMap((group) => group.items).find((item) => item.id === view)?.label ||
    (view === "application-detail" ? "Application Details" : "Workspace");

  const initials = userName
    ? userName
        .split(" ")
        .filter(Boolean)
        .map((s) => s[0])
        .join("")
        .slice(0, 2)
        .toUpperCase() || "US"
    : "AM";

  const handleNavClick = (id: AppView) => {
    setMobileNavOpen(false);
    onNavigate(id);
  };

  return (
    <div className="app-shell">
      {/* Mobile Drawer Backdrop */}
      {mobileNavOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setMobileNavOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Main Sidebar (Desktop + Mobile Drawer) */}
      <aside className={`sidebar ${mobileNavOpen ? "sidebar-open" : ""}`} aria-label="Sidebar navigation">
        <div className="sidebar-top">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Brand onClick={() => handleNavClick("dashboard")} />
            {mobileNavOpen && (
              <IconButton label="Close navigation" onClick={() => setMobileNavOpen(false)}>
                <X size={18} aria-hidden="true" />
              </IconButton>
            )}
          </div>
          <span className="workspace-label">Personal workspace</span>
        </div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <p className="nav-group-label">{group.label}</p>
              {group.items.map((item) => {
                const Icon = item.icon;
                const active =
                  item.id === view ||
                  (item.id === "job-analysis" &&
                    [
                      "matching",
                      "clarifications",
                      "cv-generation",
                      "ats-analysis",
                      "cover-email",
                    ].includes(view));
                return (
                  <button
                    key={item.id}
                    className={`nav-item ${active ? "nav-item-active" : ""}`}
                    onClick={() => handleNavClick(item.id)}
                  >
                    <Icon size={18} weight={active ? "fill" : "regular"} aria-hidden="true" />
                    <span>{item.label}</span>
                    {item.id === "applications" ? <span className="nav-count">4</span> : null}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-tip">
            <Sparkle size={16} weight="fill" aria-hidden="true" />
            <div>
              <strong>Evidence first</strong>
              <span>Every claim stays traceable.</span>
            </div>
          </div>
          <button className="profile-chip" onClick={() => handleNavClick("settings")}>
            <Avatar initials={initials} size="sm" />
            <span>
              <strong>{userName}</strong>
              <small>{userEmail}</small>
            </span>
            <Gear size={15} aria-hidden="true" />
          </button>
        </div>
      </aside>
      <div className="mobile-shell-head">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <IconButton
            label="Open navigation menu"
            onClick={() => setMobileNavOpen(true)}
          >
            <List size={20} aria-hidden="true" />
          </IconButton>
          <Brand compact onClick={() => handleNavClick("dashboard")} />
        </div>
        <div className="mobile-head-actions">
          <IconButton label="Search" onClick={() => {}}>
            <MagnifyingGlass size={19} aria-hidden="true" />
          </IconButton>
          <IconButton label="Settings" onClick={() => handleNavClick("settings")}>
            <Avatar initials={initials} size="sm" />
          </IconButton>
        </div>
      </div>
      <main className="workspace-main" id="main-content">
        <header className="workspace-header">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-slash">/</span>
            <strong>{currentLabel}</strong>
          </div>
          <div className="header-actions">
            <label className="global-search">
              <MagnifyingGlass size={16} aria-hidden="true" />
              <input aria-label="Search workspace" placeholder="Search workspace…" />
              <kbd>⌘ K</kbd>
            </label>
            <IconButton label="Notifications">
              <Bell size={19} aria-hidden="true" />
            </IconButton>
            <div className="header-divider" />
            <Button
              size="sm"
              icon={<Plus size={16} weight="bold" aria-hidden="true" />}
              onClick={() => onNavigate("add-job")}
            >
              Add Job
            </Button>
          </div>
        </header>
        <div className="mobile-page-title">
          <span>{currentLabel}</span>
          <IconButton label="Close menu">
            <X size={18} aria-hidden="true" />
          </IconButton>
        </div>
        {children}
      </main>
    </div>
  );
}
