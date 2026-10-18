"use client";

import { lazy, Suspense, useEffect, useState, useTransition } from "react";
import { WorkspaceShell } from "@/components/app-shell";
import {
  AddJobSkeleton,
  ApplicationDetailSkeleton,
  ApplicationsSkeleton,
  AtsAnalysisSkeleton,
  AuthSkeleton,
  ClarificationsSkeleton,
  CoverEmailSkeleton,
  CvEditorSkeleton,
  CvGenerationSkeleton,
  DashboardSkeleton,
  InterviewSkeleton,
  JobAnalysisSkeleton,
  LandingSkeleton,
  MatchingSkeleton,
  OnboardingSkeleton,
  ProfileSkeleton,
  ProjectsSkeleton,
  SettingsSkeleton,
} from "@/components/skeletons";
import { useCurrentUser, useLogout } from "@/hooks/use-auth";
import { getAtsReport, getDashboardData, getInterviewPrep } from "@/lib/api/mock-api";
import {
  mockApplications,
  mockAts,
  mockCv,
  mockInterview,
  mockJob,
  mockProfile,
  mockProjects,
  mockQuestions,
} from "@/lib/mock";
import {
  Application,
  AppView,
  AtsReport,
  CandidateProfile,
  ClarificationQuestion,
  CvDocument,
  InterviewQuestion,
  Job,
  Project,
  ToastMessage,
} from "@/types";
import { ToastViewport } from "@/components/ui";

// Lazy-loaded pages & views
const LandingPage = lazy(() => import("@/components/landing").then((m) => ({ default: m.LandingPage })));
const AuthPage = lazy(() => import("@/components/auth").then((m) => ({ default: m.AuthPage })));
const OnboardingPage = lazy(() => import("@/components/onboarding").then((m) => ({ default: m.OnboardingPage })));

const DashboardView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.DashboardView })));
const ProfileView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.ProfileView })));
const ProjectsView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.ProjectsView })));
const JobTargetsView = lazy(() => import("@/components/jobs/job-targets-view").then((m) => ({ default: m.JobTargetsView })));
const JobAnalysisView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.JobAnalysisView })));
const MatchingView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.MatchingView })));
const ClarificationsView = lazy(() => import("@/components/clarification/clarifications-view").then((m) => ({ default: m.ClarificationsView })));
const CVVersionsView = lazy(() => import("@/components/cv/cv-versions-view").then((m) => ({ default: m.CVVersionsView })));
const AtsAnalysisView = lazy(() => import("@/components/ats").then((m) => ({ default: m.AtsAnalysisView })));
const CoverLetterView = lazy(() => import("@/components/cover-letter").then((m) => ({ default: m.CoverLetterView })));
const InterviewView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.InterviewView })));
const ApplicationsView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.ApplicationsView })));
const ApplicationDetailView = lazy(() =>
  import("@/components/workspace").then((m) => ({ default: m.ApplicationDetailView }))
);
const SettingsView = lazy(() => import("@/components/workspace").then((m) => ({ default: m.SettingsView })));

const VALID_VIEWS: Set<AppView> = new Set<AppView>([
  "landing",
  "auth",
  "onboarding",
  "dashboard",
  "profile",
  "projects",
  "add-job",
  "job-analysis",
  "matching",
  "clarifications",
  "cv-generation",
  "cv-editor",
  "ats-analysis",
  "cover-email",
  "interview",
  "applications",
  "application-detail",
  "settings",
]);

function initialView(): AppView {
  if (typeof window === "undefined") return "landing";
  const view = new URLSearchParams(window.location.search).get("view") as AppView | null;
  if (view && VALID_VIEWS.has(view)) {
    return view;
  }
  return "landing";
}

export default function Home() {
  const [view, setView] = useState<AppView>(initialView);
  const [authMode, setAuthMode] = useState<"register" | "login">("register");
  const [, startTransition] = useTransition();

  // Authentication State via TanStack Query
  const { user, isLoading: authLoading, isAuthenticated } = useCurrentUser();
  const logoutMutation = useLogout();

  // Local Prototype State (Deferred to future phases)
  const [profile] = useState<CandidateProfile>(mockProfile);
  const [job, setJob] = useState<Job>(mockJob);
  const [projects, setProjects] = useState<Project[]>(mockProjects);
  const [questions, setQuestions] = useState<ClarificationQuestion[]>(mockQuestions);
  const [cv, setCv] = useState<CvDocument>(mockCv);
  const [ats, setAts] = useState<AtsReport>(mockAts);
  const [interview, setInterview] = useState<InterviewQuestion[]>(mockInterview);
  const [applications, setApplications] = useState<Application[]>(mockApplications);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handlePopState = () => setView(initialView());
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    if (view === "ats-analysis") getAtsReport().then(setAts);
    if (view === "interview") getInterviewPrep().then(setInterview);
    if (view === "dashboard") getDashboardData();
  }, [view]);

  const addToast = (title: string, message: string, type: ToastMessage["type"] = "success") => {
    const id = Date.now();
    setToasts((items) => [...items, { id, title, message, type }]);
    window.setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), 4200);
  };

  const navigate = (nextView: AppView) => {
    startTransition(() => {
      setView(nextView);
    });
    if (typeof window !== "undefined") {
      window.history.pushState({}, "", nextView === "landing" ? "/" : `/?view=${nextView}`);
    }
  };

  const handleSignOut = async () => {
    try {
      await logoutMutation.mutateAsync();
      addToast("Signed out", "You have successfully signed out.", "info");
    } catch {
      addToast("Signed out", "Signed out locally.", "info");
    } finally {
      navigate("landing");
    }
  };

  const currentUserName = user?.full_name || profile.name;
  const currentUserEmail = user?.email || profile.email;

  const renderWorkspaceView = () => {
    switch (view) {
      case "dashboard":
        return (
          <Suspense fallback={<DashboardSkeleton />}>
            <DashboardView
              profile={profile}
              job={job}
              applications={applications}
              onNavigate={navigate}
              onToast={addToast}
            />
          </Suspense>
        );
      case "profile":
        return (
          <Suspense fallback={<ProfileSkeleton />}>
            <ProfileView
              onNavigate={navigate}
              onToast={addToast}
              userName={currentUserName}
              userEmail={currentUserEmail}
            />
          </Suspense>
        );
      case "projects":
        return (
          <Suspense fallback={<ProjectsSkeleton />}>
            <ProjectsView
              projects={projects}
              setProjects={setProjects}
              onNavigate={navigate}
              onToast={addToast}
            />
          </Suspense>
        );
      case "add-job":
      case "job-analysis":
        return (
          <Suspense fallback={<AddJobSkeleton />}>
            <JobTargetsView onToast={addToast} onNavigate={navigate} />
          </Suspense>
        );
      case "matching":
        return (
          <Suspense fallback={<MatchingSkeleton />}>
            <MatchingView job={job} onNavigate={navigate} />
          </Suspense>
        );
      case "clarifications":
        return (
          <Suspense fallback={<ClarificationsSkeleton />}>
            <ClarificationsView
              onNavigate={navigate}
              onToast={addToast}
            />
          </Suspense>
        );
      case "cv-generation":
      case "cv-editor":
        return (
          <Suspense fallback={<CvGenerationSkeleton />}>
            <CVVersionsView onToast={addToast} onNavigate={navigate} />
          </Suspense>
        );
      case "ats-analysis":
        return (
          <Suspense fallback={<AtsAnalysisSkeleton />}>
            <AtsAnalysisView onNavigate={navigate} onToast={addToast} />
          </Suspense>
        );
      case "cover-email":
        return (
          <Suspense fallback={<CoverEmailSkeleton />}>
            <CoverLetterView onNavigate={navigate} onToast={addToast} />
          </Suspense>
        );
      case "interview":
        return (
          <Suspense fallback={<InterviewSkeleton />}>
            <InterviewView
              questions={interview}
              setQuestions={setInterview}
              onNavigate={navigate}
              onToast={addToast}
            />
          </Suspense>
        );
      case "applications":
        return (
          <Suspense fallback={<ApplicationsSkeleton />}>
            <ApplicationsView
              applications={applications}
              setApplications={setApplications}
              onNavigate={navigate}
            />
          </Suspense>
        );
      case "application-detail":
        return (
          <Suspense fallback={<ApplicationDetailSkeleton />}>
            <ApplicationDetailView
              application={applications[0]}
              onBack={() => navigate("applications")}
              onToast={addToast}
            />
          </Suspense>
        );
      case "settings":
        return (
          <Suspense fallback={<SettingsSkeleton />}>
            <SettingsView
              onToast={addToast}
              onSignOut={handleSignOut}
              userName={currentUserName}
              userEmail={currentUserEmail}
            />
          </Suspense>
        );
      default:
        return (
          <Suspense fallback={<DashboardSkeleton />}>
            <DashboardView
              profile={profile}
              job={job}
              applications={applications}
              onNavigate={navigate}
              onToast={addToast}
            />
          </Suspense>
        );
    }
  };

  const toastElement = (
    <ToastViewport
      toasts={toasts}
      onDismiss={(id) => setToasts((items) => items.filter((item) => item.id !== id))}
    />
  );

  // 1. Initial Session Resolution Loading Screen
  if (authLoading) {
    return (
      <>
        <AuthSkeleton />
        {toastElement}
      </>
    );
  }

  // 2. Landing Page
  if (view === "landing") {
    return (
      <>
        <Suspense fallback={<LandingSkeleton />}>
          <LandingPage
            onStart={() => {
              if (isAuthenticated) {
                navigate("dashboard");
              } else {
                setAuthMode("register");
                navigate("auth");
              }
            }}
            onLogin={() => {
              if (isAuthenticated) {
                navigate("dashboard");
              } else {
                setAuthMode("login");
                navigate("auth");
              }
            }}
          />
        </Suspense>
        {toastElement}
      </>
    );
  }

  // 3. Auth Page (Register / Login)
  if (view === "auth") {
    return (
      <>
        <Suspense fallback={<AuthSkeleton />}>
          <AuthPage
            initialMode={authMode}
            onBack={() => navigate("landing")}
            onComplete={() => navigate("dashboard")}
          />
        </Suspense>
        {toastElement}
      </>
    );
  }

  // 4. Protected Workspace Views (Require active authentication)
  if (!isAuthenticated && view !== "onboarding") {
    return (
      <>
        <Suspense fallback={<AuthSkeleton />}>
          <AuthPage
            initialMode="login"
            onBack={() => navigate("landing")}
            onComplete={() => navigate(view)}
          />
        </Suspense>
        {toastElement}
      </>
    );
  }

  // 5. Onboarding View
  if (view === "onboarding") {
    return (
      <>
        <Suspense fallback={<OnboardingSkeleton />}>
          <OnboardingPage onComplete={() => navigate("dashboard")} onToast={addToast} />
        </Suspense>
        {toastElement}
      </>
    );
  }

  // 6. Authenticated Workspace Shell
  return (
    <>
      <WorkspaceShell
        view={view}
        onNavigate={navigate}
        onSignOut={handleSignOut}
        userName={currentUserName}
        userEmail={currentUserEmail}
      >
        {renderWorkspaceView()}
      </WorkspaceShell>
      {toastElement}
    </>
  );
}
