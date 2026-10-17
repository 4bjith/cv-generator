"use client";

import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Bell,
  BookOpen,
  Briefcase,
  CalendarBlank,
  CaretDown,
  CaretRight,
  Check,
  CheckCircle,
  ClipboardText,
  Clock,
  Code,
  Copy,
  DotsThree,
  DownloadSimple,
  EnvelopeSimple,
  Eye,
  FileArrowUp,
  FileText,
  Funnel,
  GithubLogo,
  GlobeHemisphereWest,
  Lightning,
  LinkSimple,
  ListChecks,
  MagnifyingGlass,
  MapPin,
  PencilSimple,
  Plus,
  Question,
  Rows,
  SealCheck,
  SlidersHorizontal,
  Sparkle,
  Target,
  Trash,
  TrendUp,
  UserCircle,
  UsersThree,
  WarningCircle,
  X,
} from "@phosphor-icons/react";
import { useEffect, useMemo, useState } from "react";
import { analyzeRepository, generateCoverEmail, generateCv, getAtsReport, getInterviewPrep, submitClarification, updateApplicationStatus } from "@/lib/api/mock-api";
import { Application, ApplicationStatus, AppView, AtsReport, CandidateProfile, ClarificationQuestion, CvDocument, InterviewQuestion, Job, MatchState, Project, Skill } from "@/types";
import { Badge, Button, Card, CheckMark, Field, IconButton, InlineNotice, Modal, ProgressBar, SectionHeading, SelectField, StatusIcon, TextareaField } from "@/components/ui";

const statusTone: Record<ApplicationStatus, string> = { Saved: "neutral", Applied: "blue", Screening: "amber", Interview: "green", "Technical Round": "purple", "Final Round": "purple", Offer: "green", Rejected: "red", Withdrawn: "red" };
const matchTone: Record<MatchState, string> = { strong: "green", partial: "amber", weak: "orange", none: "red", unknown: "neutral" };
const matchLabel: Record<MatchState, string> = { strong: "Strong", partial: "Partial", weak: "Weak", none: "No evidence", unknown: "Unknown" };

function PageFrame({ children, className = "" }: { children: React.ReactNode; className?: string }) { return <div className={`page-frame ${className}`}>{children}</div>; }
function ViewTitle({ eyebrow, title, description, actions }: { eyebrow?: string; title: string; description?: string; actions?: React.ReactNode }) { return <div className="view-title"><div><p className="eyebrow">{eyebrow || "Workspace"}</p><h1>{title}</h1>{description ? <p>{description}</p> : null}</div>{actions ? <div className="view-title-actions">{actions}</div> : null}</div>; }
function StatCard({ label, value, detail, icon, tone = "blue" }: { label: string; value: string; detail: string; icon: React.ReactNode; tone?: string }) { return <Card className="stat-card"><div className={`stat-icon stat-${tone}`}>{icon}</div><div className="stat-copy"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></Card>; }
function StatusBadge({ status }: { status: ApplicationStatus }) { return <Badge tone={statusTone[status]}>{status}</Badge>; }
function MatchBadge({ state }: { state: MatchState }) { return <Badge tone={matchTone[state]}>{matchLabel[state]}</Badge>; }
function CompanyMark({ initials, tone = "blue" }: { initials: string; tone?: string }) { return <span className={`company-mark company-${tone}`}>{initials}</span>; }

export function DashboardView({ profile, job, applications, onNavigate, onToast }: { profile: CandidateProfile; job: Job; applications: Application[]; onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const interview = applications.filter((app) => app.status === "Interview" || app.status === "Technical Round").length;
  return <PageFrame><ViewTitle eyebrow="Monday, October 02" title={`Good morning, ${profile.name.split(" ")[0]}`} description="Your next useful step is already clear." actions={<Button icon={<Plus size={17} weight="bold" aria-hidden="true" />} onClick={() => onNavigate("add-job")}>Add Job</Button>} /><div className="dashboard-stats"><StatCard label="Profile readiness" value={`${profile.profileScore}%`} detail="2 details to review" icon={<TrendUp size={21} aria-hidden="true" />} tone="blue" /><StatCard label="Active applications" value={`${applications.length}`} detail="1 needs attention" icon={<Briefcase size={21} aria-hidden="true" />} tone="green" /><StatCard label="Interview pipeline" value={`${interview}`} detail="Next: Oct 08" icon={<CalendarBlank size={21} aria-hidden="true" />} tone="purple" /><StatCard label="Verified evidence" value="18" detail="Across 4 sources" icon={<SealCheck size={21} weight="fill" aria-hidden="true" />} tone="orange" /></div><div className="dashboard-grid"><Card className="next-step-panel"><div className="panel-kicker"><span className="panel-kicker-icon"><Sparkle size={15} weight="fill" aria-hidden="true" /></span><span>Recommended next step</span></div><div className="next-step-content"><div><h2>Close the loop on your Lattice application</h2><p>Two requirements need your input before the tailored CV is ready. It should take about 4 minutes.</p><div className="next-step-meta"><span><Clock size={15} aria-hidden="true" /> 4 min</span><span><Target size={15} aria-hidden="true" /> 84% match</span></div></div><Button size="lg" icon={<ArrowRight size={17} aria-hidden="true" />} onClick={() => onNavigate("matching")}>Review Match</Button></div><div className="next-step-line"><span style={{ width: "72%" }} /></div><div className="next-step-foot"><span>Application workflow</span><span>4 of 6 steps complete</span></div></Card><Card className="evidence-card"><div className="card-heading"><div><p className="eyebrow">Evidence spotlight</p><h2>Design systems</h2></div><Button variant="quiet" size="sm" onClick={() => onNavigate("profile")}>View profile <ArrowUpRight size={15} aria-hidden="true" /></Button></div><div className="evidence-quote"><span className="quote-mark">“</span><p>Created a token-driven component system adopted by 4 product teams.</p></div><div className="evidence-source"><div className="source-icon"><Code size={16} aria-hidden="true" /></div><span><strong>Northstar Labs</strong><small>Experience · User confirmed</small></span><CheckCircle size={17} weight="fill" className="source-check" aria-hidden="true" /></div></Card></div><Card className="applications-preview"><div className="card-heading"><div><p className="eyebrow">Your pipeline</p><h2>Recent applications</h2></div><Button variant="quiet" size="sm" onClick={() => onNavigate("applications")}>View all <ArrowRight size={15} aria-hidden="true" /></Button></div><div className="application-table"><div className="application-table-head"><span>Role</span><span>Match</span><span>Status</span><span>Next step</span><span /></div>{applications.slice(0, 4).map((app) => <button className="application-row" key={app.id} onClick={() => onNavigate("application-detail")}><span className="application-role"><CompanyMark initials={app.initials} /><span><strong>{app.role}</strong><small>{app.company} · {app.location}</small></span></span><span className="match-number">{app.matchScore}%</span><span><StatusBadge status={app.status} /></span><span className="application-next">{app.nextStep}<small>{app.nextDate ? `Due ${app.nextDate}` : "No date yet"}</small></span><CaretRight size={17} aria-hidden="true" /></button>)}</div></Card><div className="dashboard-bottom"><Card className="quick-actions"><div className="card-heading"><div><p className="eyebrow">Shortcuts</p><h2>Keep momentum</h2></div></div><button onClick={() => onNavigate("profile")}><span className="quick-icon quick-blue"><UserCircle size={18} aria-hidden="true" /></span><span><strong>Complete your profile</strong><small>Add one missing metric</small></span><ArrowRight size={16} aria-hidden="true" /></button><button onClick={() => onNavigate("projects")}><span className="quick-icon quick-purple"><GithubLogo size={18} aria-hidden="true" /></span><span><strong>Review project evidence</strong><small>1 repository needs analysis</small></span><ArrowRight size={16} aria-hidden="true" /></button><button onClick={() => onNavigate("interview")}><span className="quick-icon quick-green"><BookOpen size={18} aria-hidden="true" /></span><span><strong>Practice interview prep</strong><small>4 questions ready</small></span><ArrowRight size={16} aria-hidden="true" /></button></Card><Card className="principles-card"><div className="principles-card-top"><Sparkle size={19} weight="fill" aria-hidden="true" /><span>How the workspace thinks</span></div><h2>Good applications are specific, not inflated.</h2><p>AI CV Maker keeps strong evidence close to every generated claim, so you can move faster without losing your voice.</p><button className="text-link" onClick={() => onNavigate("profile")}>Explore your evidence <ArrowUpRight size={16} aria-hidden="true" /></button></Card></div></PageFrame>;
}

import { ProfileEditor } from "@/components/profile/profile-editor";

export function ProfileView({
  onNavigate,
  onToast,
  userName,
  userEmail,
}: {
  profile?: CandidateProfile;
  skills?: Skill[];
  experience?: import("@/types").Experience[];
  onNavigate: (view: AppView) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  userName?: string;
  userEmail?: string;
}) {
  return (
    <ProfileEditor
      onNavigate={onNavigate}
      onToast={onToast}
      userName={userName}
      userEmail={userEmail}
    />
  );
}

export function ProjectsView({ projects, setProjects, onNavigate, onToast }: { projects: Project[]; setProjects: React.Dispatch<React.SetStateAction<Project[]>>; onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  const runAnalysis = async (project: Project) => { setAnalyzing(project.id); const updated = await analyzeRepository(project); setProjects((items) => items.map((item) => item.id === project.id ? updated : item)); setAnalyzing(null); onToast("Project analyzed", `${project.name} is now available as evidence.`); };
  return <PageFrame><ViewTitle eyebrow="Candidate Knowledge Base" title="Projects & GitHub" description="Choose which work should inform your next application." actions={<Button icon={<GithubLogo size={17} aria-hidden="true" />} onClick={() => onToast("GitHub connection simulated", "Your public project list is already connected.")}>Sync GitHub</Button>} /><div className="project-summary-row"><Card className="project-summary"><GithubLogo size={22} aria-hidden="true" /><div><strong>github.com/aaravmehta</strong><span>Connected 4 days ago</span></div><Badge tone="green">Connected</Badge></Card><Card className="project-summary"><SealCheck size={22} weight="fill" aria-hidden="true" /><div><strong>{projects.filter((project) => project.analyzed).length} analyzed projects</strong><span>Evidence is selective by design</span></div><Button variant="quiet" size="sm" onClick={() => onNavigate("profile")}>View evidence</Button></Card></div><SectionHeading eyebrow="Your project shelf" title="Projects worth talking about" description="Analysis separates what the repository shows from what you personally contributed." /><div className="project-grid">{projects.map((project) => <Card className="project-card" key={project.id}><div className="project-card-head"><span className="project-glyph"><Code size={20} aria-hidden="true" /></span><IconButton label={`More options for ${project.name}`} onClick={() => onToast("Project menu", `${project.name} actions are ready in the full project editor.`)}><DotsThree size={21} aria-hidden="true" /></IconButton></div><h2>{project.name}</h2><p>{project.description}</p><div className="stack-list">{project.stack.map((stack) => <Badge key={stack} tone="neutral">{stack}</Badge>)}</div><div className="project-stats"><span><GithubLogo size={14} aria-hidden="true" /> {project.stars} stars</span><span>{project.forks} forks</span><span>{project.lastUpdated}</span></div><div className="project-card-foot">{project.analyzed ? <span className="analyzed-label"><CheckCircle size={15} weight="fill" aria-hidden="true" /> Analyzed</span> : <span className="review-label"><WarningCircle size={15} weight="fill" aria-hidden="true" /> Needs analysis</span>}<Button variant={project.analyzed ? "quiet" : "secondary"} size="sm" loading={analyzing === project.id} onClick={() => runAnalysis(project)}>{project.analyzed ? "Re-analyze" : "Analyze Project"}</Button></div></Card>)}</div><InlineNotice title="Selective by default">AI CV Maker reads the README, package manifests, source structure, tests, and deployment context. It does not ingest every file automatically.</InlineNotice></PageFrame>;
}

export function AddJobView({ onNavigate, onJobReady, onToast }: { onNavigate: (view: AppView) => void; onJobReady: (job: Job) => void; onToast: (title: string, message: string) => void }) {
  const [mode, setMode] = useState<"paste" | "upload" | "url">("paste");
  const [text, setText] = useState("Senior Frontend Engineer\nLattice Systems\n\nWe are looking for a frontend engineer to shape an accessible, high-quality product platform with React, TypeScript, design systems, and a strong testing culture. Experience with GraphQL and mentoring is a plus.");
  const [loading, setLoading] = useState(false);
  const submit = async () => { setLoading(true); await new Promise((resolve) => setTimeout(resolve, 850)); const { getJobAnalysis } = await import("@/lib/api/mock-api"); onJobReady(await getJobAnalysis()); setLoading(false); onNavigate("job-analysis"); };
  return <PageFrame><ViewTitle eyebrow="Application Studio" title="Add a job" description="Bring the role into the workspace. We’ll show you what is clear and what needs a question." actions={<Button variant="ghost" onClick={() => onNavigate("applications")}>Back to Applications</Button>} /><div className="add-job-layout"><Card className="job-input-card"><div className="input-mode-tabs" role="tablist">{([{id:"paste",label:"Paste text",icon:<ClipboardText size={17} aria-hidden="true" />},{id:"upload",label:"Upload file",icon:<FileArrowUp size={17} aria-hidden="true" />},{id:"url",label:"Public URL",icon:<GlobeHemisphereWest size={17} aria-hidden="true" />}]).map((item) => <button key={item.id} role="tab" aria-selected={mode === item.id} className={mode === item.id ? "active" : ""} onClick={() => setMode(item.id as typeof mode)}>{item.icon}{item.label}</button>)}</div>{mode === "paste" ? <TextareaField label="Job description" name="job-description" value={text} onChange={(event) => setText(event.target.value)} rows={15} hint="Paste the full role description for the clearest analysis." /> : mode === "upload" ? <div className="large-upload-zone"><span className="upload-icon"><FileArrowUp size={30} aria-hidden="true" /></span><h2>Drop a job description here</h2><p>PDF, DOCX, or image files up to 10 MB.</p><Button variant="secondary" onClick={() => onToast("Prototype upload", "The file extraction pipeline will connect in the next phase.")}>Choose File</Button></div> : <Field label="Public job URL" name="job-url" type="url" placeholder="https://company.com/careers/frontend-engineer…" hint="Only use pages that are public and legally accessible." />}{mode === "paste" ? <div className="job-input-foot"><span><CheckCircle size={15} weight="fill" aria-hidden="true" /> Private prototype input</span><Button size="lg" loading={loading} icon={<Sparkle size={17} weight="fill" aria-hidden="true" />} onClick={submit}>Analyze This Job</Button></div> : <div className="job-input-foot"><span /><Button size="lg" loading={loading} icon={<Sparkle size={17} weight="fill" aria-hidden="true" />} onClick={submit}>Analyze This Job</Button></div>}</Card><Card className="job-input-side"><div className="side-icon"><Sparkle size={20} weight="fill" aria-hidden="true" /></div><h2>What happens next?</h2><div className="side-steps"><div><span>1</span><p><strong>Extract signal</strong><small>Title, responsibilities, skills, and context.</small></p></div><div><span>2</span><p><strong>Compare evidence</strong><small>Your profile against each requirement.</small></p></div><div><span>3</span><p><strong>Ask only what is missing</strong><small>Small, specific questions before generation.</small></p></div></div><div className="side-quote"><span>“</span><p>No invented achievements. No silent assumptions.</p></div></Card></div></PageFrame>;
}

export function JobAnalysisView({ job, onNavigate, onToast }: { job: Job; onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const required = job.requirements.filter((item) => item.type === "required");
  const strong = required.filter((item) => item.state === "strong").length;
  return <PageFrame><ViewTitle eyebrow="Job Intelligence" title={job.title} description={`${job.company} · ${job.location}`} actions={<><Button variant="secondary" icon={<PencilSimple size={17} aria-hidden="true" />} onClick={() => onToast("Job details", "Editing job details is available in the full job record.")}>Edit Job</Button><Button icon={<ArrowRight size={17} aria-hidden="true" />} onClick={() => onNavigate("matching")}>Review Match</Button></>} /><Card className="job-overview-card"><div className="job-company-line"><CompanyMark initials="LS" tone="purple" /><div><h2>{job.company}</h2><p><MapPin size={15} aria-hidden="true" /> {job.location} <span>·</span> {job.mode} <span>·</span> {job.salary}</p></div><Badge tone="green">{job.matchScore}% match</Badge></div><p className="job-description">{job.description}</p><div className="job-meta-row"><span><Clock size={15} aria-hidden="true" /> {job.posted}</span><span><Briefcase size={15} aria-hidden="true" /> Full-time</span><button className="text-link" onClick={() => onToast("Job link", "A public job link would open here.")}>View original <ArrowUpRight size={15} aria-hidden="true" /></button></div></Card><div className="analysis-grid"><Card><div className="card-heading"><div><p className="eyebrow">Extracted requirements</p><h2>What the role asks for</h2></div><Badge tone="blue">{job.requirements.length} signals</Badge></div><div className="requirement-cloud">{job.requirements.map((item) => <div className="requirement-chip" key={item.id}><span className={`requirement-dot dot-${matchTone[item.state]}`} /><strong>{item.name}</strong><small>{item.type === "required" ? "Required" : "Preferred"}</small></div>)}</div></Card><Card className="match-summary-card"><div className="match-score-large"><span>{job.matchScore}</span><small>% match</small></div><div><p className="eyebrow">Current profile match</p><h2>Strong enough to explore</h2><p>{strong} of {required.length} required signals have strong evidence. Two items need a conversation.</p></div><ProgressBar value={job.matchScore} label="Match strength" /></Card></div><Card className="analysis-breakdown"><div className="card-heading"><div><p className="eyebrow">A closer look</p><h2>Signals by confidence</h2></div><Button variant="quiet" size="sm" onClick={() => onNavigate("matching")}>Open full match <ArrowRight size={15} aria-hidden="true" /></Button></div><div className="confidence-bars"><div><span><i className="legend-dot dot-green" />Strong evidence</span><b>{strong}</b><div className="confidence-track"><span style={{ width: `${(strong / job.requirements.length) * 100}%` }} /></div></div><div><span><i className="legend-dot dot-amber" />Needs review</span><b>{job.requirements.filter((item) => item.state === "partial" || item.state === "weak").length}</b><div className="confidence-track confidence-amber"><span style={{ width: "38%" }} /></div></div><div><span><i className="legend-dot dot-neutral" />Unknown</span><b>{job.requirements.filter((item) => item.state === "unknown" || item.state === "none").length}</b><div className="confidence-track confidence-neutral"><span style={{ width: "18%" }} /></div></div></div></Card></PageFrame>;
}

export function MatchingView({ job, onNavigate }: { job: Job; onNavigate: (view: AppView) => void }) {
  const [filter, setFilter] = useState<"all" | MatchState>("all");
  const requirements = filter === "all" ? job.requirements : job.requirements.filter((item) => item.state === filter);
  return <PageFrame><ViewTitle eyebrow="Job Intelligence" title="Candidate ↔ job match" description="Review the evidence behind every requirement before you generate anything." actions={<Button icon={<ArrowRight size={17} aria-hidden="true" />} onClick={() => onNavigate("clarifications")}>Answer Questions</Button>} /><div className="match-hero"><div className="match-score-large match-score-hero"><span>{job.matchScore}</span><small>%</small></div><div><p className="eyebrow">Lattice Systems · Senior Frontend Engineer</p><h2>Strong foundation with 3 useful follow-ups</h2><p>Most core requirements are supported by clear evidence from your profile and projects.</p></div><div className="match-hero-meta"><div><strong>{job.requirements.filter((item) => item.state === "strong").length}</strong><span>Strong</span></div><div><strong>{job.requirements.filter((item) => item.state === "partial" || item.state === "weak").length}</strong><span>Review</span></div><div><strong>{job.requirements.filter((item) => item.state === "unknown").length}</strong><span>Unknown</span></div></div></div><div className="filter-row"><div className="filter-tabs"><button className={filter === "all" ? "active" : ""} onClick={() => setFilter("all")}>All {job.requirements.length}</button><button className={filter === "strong" ? "active" : ""} onClick={() => setFilter("strong")}>Strong</button><button className={filter === "partial" ? "active" : ""} onClick={() => setFilter("partial")}>Review</button><button className={filter === "unknown" ? "active" : ""} onClick={() => setFilter("unknown")}>Unknown</button></div><span className="filter-note"><Target size={15} aria-hidden="true" /> Evidence is the source of truth</span></div><Card className="match-table-card"><div className="match-table-head"><span>Requirement</span><span>Evidence state</span><span>Source & context</span><span /></div>{requirements.map((item) => <div className="match-row" key={item.id}><div className="match-requirement"><span className={`match-state-icon state-${matchTone[item.state]}`}>{item.state === "strong" ? <CheckCircle size={17} weight="fill" aria-hidden="true" /> : item.state === "unknown" ? <Question size={17} weight="bold" aria-hidden="true" /> : <WarningCircle size={17} weight="fill" aria-hidden="true" />}</span><span><strong>{item.name}</strong><small>{item.type === "required" ? "Required" : "Preferred"}</small></span></div><MatchBadge state={item.state} /><div className="match-evidence"><strong>{item.evidence || "No evidence recorded"}</strong><small>{item.note || "Needs user context before it can be used."}</small></div><CaretRight size={17} aria-hidden="true" /></div>)}</Card><InlineNotice tone="info" title="Why this matters">The prototype will never turn an unknown requirement into a confident CV claim. You decide what becomes part of your permanent profile.</InlineNotice></PageFrame>;
}

export function ClarificationsView({ questions, setQuestions, onNavigate, onToast }: { questions: ClarificationQuestion[]; setQuestions: React.Dispatch<React.SetStateAction<ClarificationQuestion[]>>; onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const [saving, setSaving] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const answered = questions.filter((question) => question.answered).length;
  const saveAnswer = async (question: ClarificationQuestion) => { const answer = answers[question.id]?.trim(); if (!answer) return onToast("Add a little context", "Answer the question before saving it."); setSaving(question.id); await submitClarification(question.id, answer); setQuestions((items) => items.map((item) => item.id === question.id ? { ...item, answered: true, answer } : item)); setSaving(null); onToast("Answer saved", "This answer is available in the application context."); };
  return <PageFrame><ViewTitle eyebrow="Clarification Engine" title="A few questions before generation" description="Small answers now keep the application accurate later." actions={<Button variant="ghost" onClick={() => onNavigate("matching")} icon={<ArrowLeft size={17} aria-hidden="true" />}>Back to Match</Button>} /><div className="clarification-progress"><div><span><Sparkle size={16} weight="fill" aria-hidden="true" /> Application context</span><strong>{answered} of {questions.length} answered</strong></div><ProgressBar value={(answered / questions.length) * 100} /></div><div className="question-stack">{questions.map((question, index) => <Card className={`question-card ${question.answered ? "question-answered" : ""}`} key={question.id}><div className="question-number">0{index + 1}</div><div className="question-content"><div className="question-top"><div><Badge tone={question.answered ? "green" : "amber"}>{question.requirement}</Badge><h2>{question.question}</h2></div>{question.answered ? <CheckCircle className="question-done" size={22} weight="fill" aria-label="Answered" /> : null}</div><p>{question.context}</p>{question.answered ? <div className="saved-answer"><span>Your answer</span><p>{question.answer}</p><button className="text-link" onClick={() => setQuestions((items) => items.map((item) => item.id === question.id ? { ...item, answered: false } : item))}>Edit answer</button></div> : <div className="question-answer"><TextareaField label="Your answer" name={`answer-${question.id}`} aria-label={`Answer for ${question.requirement}`} value={answers[question.id] || ""} onChange={(event) => setAnswers({ ...answers, [question.id]: event.target.value })} rows={3} placeholder="Share the context you want to use…" /><Button variant="secondary" loading={saving === question.id} onClick={() => saveAnswer(question)}>Save Answer</Button></div>}</div></Card>)}</div><Card className="clarification-footer"><div><CheckCircle size={20} weight="fill" aria-hidden="true" /><div><strong>Ready to create from what is verified?</strong><span>Unanswered questions will stay out of factual CV content.</span></div></div><Button size="lg" icon={<Sparkle size={17} weight="fill" aria-hidden="true" />} onClick={() => onNavigate("cv-generation")}>Generate Tailored CV</Button></Card></PageFrame>;
}

export function CvGenerationView({ cv, setCv, onNavigate }: { cv: CvDocument; setCv: React.Dispatch<React.SetStateAction<CvDocument>>; onNavigate: (view: AppView) => void }) {
  const [phase, setPhase] = useState<"processing" | "ready">("processing");
  useEffect(() => { let active = true; generateCv().then((document) => { if (active) { setCv(document); setPhase("ready"); } }); return () => { active = false; }; }, [setCv]);
  return <PageFrame className="generation-page"><div className="generation-center"><div className={`generation-orbit ${phase === "ready" ? "generation-ready" : ""}`}>{phase === "ready" ? <CheckCircle size={31} weight="fill" aria-hidden="true" /> : <Sparkle size={31} weight="fill" aria-hidden="true" />}</div><p className="eyebrow">AI CV Maker · Tailored output</p><h1>{phase === "processing" ? "Building your tailored CV" : "Your tailored CV is ready"}</h1><p>{phase === "processing" ? "Selecting evidence, aligning language, and checking every claim against your profile." : "The first draft is based on verified evidence for Senior Frontend Engineer at Lattice Systems."}</p>{phase === "processing" ? <div className="generation-steps"><div className="generation-step done"><CheckCircle size={17} weight="fill" aria-hidden="true" /><span>Read job requirements</span></div><div className="generation-step active"><span className="generation-spinner"><Lightning size={13} weight="fill" aria-hidden="true" /></span><span>Select relevant evidence</span></div><div className="generation-step"><span className="generation-empty" /><span>Shape the document</span></div><div className="generation-step"><span className="generation-empty" /><span>Run safety checks</span></div></div> : <div className="generation-result"><div><span>Version</span><strong>CV v{cv.version}</strong></div><div><span>Evidence used</span><strong>14 verified items</strong></div><div><span>Updated</span><strong>{cv.updatedAt}</strong></div></div>}{phase === "ready" ? <div className="generation-actions"><Button size="lg" icon={<ArrowRight size={17} aria-hidden="true" />} onClick={() => onNavigate("cv-editor")}>Open CV Editor</Button><Button variant="ghost" onClick={() => onNavigate("matching")}>Back to Match</Button></div> : <p className="generation-note">Usually takes less than a minute in production</p>}</div></PageFrame>;
}

function CvPreview({ cv }: { cv: CvDocument }) { return <div className={`cv-paper cv-template-${cv.template}`}><div className="cv-paper-head"><div><h2>{cv.candidateName}</h2><p>{cv.targetRole}</p></div><span>aarav.mehta@example.com<br />Bengaluru, India</span></div>{cv.sections.filter((section) => section.visible).map((section) => <div className="cv-paper-section" key={section.id}><h3>{section.title}</h3>{section.content.map((line) => <p key={line}>{line}</p>)}</div>)}</div>; }

export function CvEditorView({ cv, setCv, onNavigate, onToast }: { cv: CvDocument; setCv: React.Dispatch<React.SetStateAction<CvDocument>>; onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const [draft, setDraft] = useState(cv);
  const [saved, setSaved] = useState(false);
  const save = () => { setCv({ ...draft, version: draft.version + 1, updatedAt: "Just now" }); setSaved(true); onToast("CV saved", `Version ${draft.version + 1} is ready for review.`); setTimeout(() => setSaved(false), 2200); };
  return <PageFrame className="editor-page"><ViewTitle eyebrow="Document Studio" title="CV Editor" description="Edit the story. Keep the evidence intact." actions={<><Button variant="secondary" icon={<Eye size={17} aria-hidden="true" />} onClick={() => onToast("Preview mode", "You are already viewing the live preview beside the editor.")}>Preview</Button><Button icon={<DownloadSimple size={17} aria-hidden="true" />} onClick={() => onToast("Export simulated", "A PDF export will be connected after the renderer is built.")}>Export PDF</Button></>} /><div className="editor-toolbar"><div className="template-switcher"><span>Template</span>{([{id:"signal",label:"Signal"},{id:"editorial",label:"Editorial"},{id:"compact",label:"Compact"}] as const).map((template) => <button key={template.id} className={draft.template === template.id ? "active" : ""} onClick={() => setDraft({ ...draft, template: template.id })}>{template.label}</button>)}</div><span className="editor-version"><CheckCircle size={15} weight="fill" aria-hidden="true" /> {saved ? "Saved just now" : `Draft v${draft.version}`}</span></div><div className="editor-layout"><Card className="editor-controls"><div className="card-heading"><div><p className="eyebrow">Content</p><h2>Sections</h2></div><Button variant="quiet" size="sm" icon={<Plus size={15} aria-hidden="true" />} onClick={() => onToast("Add section", "Add a custom section in the full document editor.")}>Add</Button></div><div className="editor-section-list">{draft.sections.map((section, index) => <div className="editor-section-item" key={section.id}><div className="editor-section-top"><button className="drag-handle" aria-label={`Move ${section.title}`}><Rows size={17} aria-hidden="true" /></button><div><strong>{section.title}</strong><small>{section.content.length} content lines</small></div><button className={`visibility-toggle ${section.visible ? "" : "is-hidden"}`} aria-label={`${section.visible ? "Hide" : "Show"} ${section.title}`} onClick={() => setDraft({ ...draft, sections: draft.sections.map((item) => item.id === section.id ? { ...item, visible: !item.visible } : item) })}>{section.visible ? <Eye size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}</button></div><textarea aria-label={`Edit ${section.title}`} value={section.content.join("\n")} onChange={(event) => setDraft({ ...draft, sections: draft.sections.map((item) => item.id === section.id ? { ...item, content: event.target.value.split("\n") } : item) })} rows={Math.min(5, Math.max(2, section.content.length + 1))} /></div>)}</div><div className="editor-save-row"><Button className="full-width" onClick={save} icon={<Check size={17} aria-hidden="true" />}>Save Changes</Button></div></Card><div className="cv-preview-wrap"><div className="preview-meta"><span>Live preview</span><span>One page · ATS-friendly</span></div><CvPreview cv={draft} /></div></div><InlineNotice title="Editable by design">This draft stays connected to the requirements and evidence you reviewed. Changing a section does not change your permanent profile.</InlineNotice><div className="editor-next"><Button variant="ghost" onClick={() => onNavigate("job-analysis")} icon={<ArrowLeft size={17} aria-hidden="true" />}>Back to Job Analysis</Button><Button onClick={() => onNavigate("ats-analysis")} icon={<ArrowRight size={17} aria-hidden="true" />}>Run ATS Analysis</Button></div></PageFrame>;
}

export function AtsAnalysisView({ ats, onNavigate }: { ats: AtsReport; onNavigate: (view: AppView) => void }) { return <PageFrame><ViewTitle eyebrow="Document Studio" title="ATS Analysis" description="A practical review of how this CV may be read by a hiring workflow." actions={<Button icon={<ArrowRight size={17} aria-hidden="true" />} onClick={() => onNavigate("cover-email")}>Write Cover Email</Button>} /><div className="ats-top-grid"><Card className="ats-score-card"><div className="ats-score-ring" style={{ "--score": `${ats.score * 3.6}deg` } as React.CSSProperties}><div><strong>{ats.score}</strong><span>/ 100</span></div></div><div><p className="eyebrow">Overall readiness</p><h2>Strong foundation</h2><p>Clear sections and relevant language give this CV a good parsing baseline.</p></div></Card><Card className="ats-keyword-card"><div className="card-heading"><div><p className="eyebrow">Keyword coverage</p><h2>{ats.keywordCoverage}%</h2></div><Badge tone="green">Healthy</Badge></div><ProgressBar value={ats.keywordCoverage} label="High-signal keyword coverage" /><p>14 of 18 important terms appear naturally in the current draft.</p><div className="missing-keywords"><span>Review next</span>{ats.missingKeywords.map((keyword) => <Badge key={keyword} tone="amber">{keyword}</Badge>)}</div></Card></div><Card className="ats-checks"><div className="card-heading"><div><p className="eyebrow">Parser checks</p><h2>What passed, what needs a look</h2></div><Button variant="quiet" size="sm" onClick={() => onNavigate("cv-editor")}>Edit CV <PencilSimple size={15} aria-hidden="true" /></Button></div><div className="ats-check-list">{ats.checks.map((check) => <div className="ats-check-row" key={check.id}><StatusIcon status={check.status} /><div><strong>{check.label}</strong><span>{check.detail}</span></div><Badge tone={check.status === "pass" ? "green" : "amber"}>{check.status === "pass" ? "Pass" : "Review"}</Badge></div>)}</div></Card><div className="ats-bottom"><InlineNotice tone="warning" title="No ATS score is a guarantee">This report highlights potential parsing and relevance issues. A hiring team still decides what matters.</InlineNotice><Button size="lg" onClick={() => onNavigate("cover-email")} icon={<EnvelopeSimple size={18} aria-hidden="true" />}>Continue to Cover Email</Button></div></PageFrame>; }

export function CoverEmailView({ onNavigate, onToast }: { onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const [subject, setSubject] = useState("Senior Frontend Engineer application: Aarav Mehta");
  const [body, setBody] = useState("Hi Lattice team,\n\nI’m excited to apply for the Senior Frontend Engineer role. I’ve spent the last four years turning complex product workflows into fast, understandable interfaces, most recently leading frontend work for Northstar’s workflow platform.\n\nThe role’s focus on thoughtful systems and operator experience is a strong match for how I work. I’d love to share how I built a token-driven component system adopted by four teams and helped reduce task completion time by 31%.\n\nThank you for your time,\nAarav Mehta");
  const [loading, setLoading] = useState(false);
  const regenerate = async () => { setLoading(true); const email = await generateCoverEmail(); setSubject(email.subject); setBody(email.body); setLoading(false); onToast("Email refreshed", "The draft was regenerated from the same verified evidence."); };
  return <PageFrame><ViewTitle eyebrow="Application Studio" title="Cover Email" description="A concise note that sounds like you and points to relevant proof." actions={<Button variant="secondary" onClick={regenerate} loading={loading} icon={<Sparkle size={17} weight="fill" aria-hidden="true" />}>Regenerate Draft</Button>} /><div className="email-layout"><Card className="email-editor"><div className="card-heading"><div><p className="eyebrow">Editable draft</p><h2>To the Lattice team</h2></div><Badge tone="green">Evidence aligned</Badge></div><Field label="Subject" name="email-subject" value={subject} onChange={(event) => setSubject(event.target.value)} /><TextareaField label="Message" name="email-body" value={body} onChange={(event) => setBody(event.target.value)} rows={18} /><div className="email-actions"><Button variant="secondary" icon={<Copy size={16} aria-hidden="true" />} onClick={() => onToast("Draft copied", "The email text is ready to paste into your mail client.")}>Copy Email</Button><Button onClick={() => onToast("Email saved", "Cover Email v1 is attached to this application.")} icon={<Check size={16} aria-hidden="true" />}>Save Draft</Button></div></Card><Card className="email-guide"><div className="side-icon"><EnvelopeSimple size={21} aria-hidden="true" /></div><h2>Why this draft works</h2><div className="guide-list"><div><CheckCircle size={17} weight="fill" aria-hidden="true" /><span>Names the role and intent quickly.</span></div><div><CheckCircle size={17} weight="fill" aria-hidden="true" /><span>Uses one relevant project signal.</span></div><div><CheckCircle size={17} weight="fill" aria-hidden="true" /><span>Stays concise enough to scan.</span></div></div><InlineNotice title="Keep your voice">The best edit is the one that makes the draft sound more like something you would actually send.</InlineNotice></Card></div><div className="editor-next"><Button variant="ghost" onClick={() => onNavigate("ats-analysis")} icon={<ArrowLeft size={17} aria-hidden="true" />}>Back to ATS Analysis</Button><Button onClick={() => onNavigate("interview")} icon={<ArrowRight size={17} aria-hidden="true" />}>Prepare for Interview</Button></div></PageFrame>;
}

export function InterviewView({ questions, setQuestions, onNavigate, onToast }: { questions: InterviewQuestion[]; setQuestions: React.Dispatch<React.SetStateAction<InterviewQuestion[]>>; onNavigate: (view: AppView) => void; onToast: (title: string, message: string) => void }) {
  const [category, setCategory] = useState<"All" | InterviewQuestion["category"]>("All");
  const visible = category === "All" ? questions : questions.filter((question) => question.category === category);
  return <PageFrame><ViewTitle eyebrow="Interview Studio" title="Interview Preparation" description="Practice questions grounded in the role and the projects you can actually discuss." actions={<Button icon={<Briefcase size={17} aria-hidden="true" />} onClick={() => onNavigate("applications")}>View Application</Button>} /><div className="interview-hero"><div className="interview-hero-icon"><BookOpen size={24} aria-hidden="true" /></div><div><p className="eyebrow">For Lattice Systems</p><h2>Prepare stories, not scripts</h2><p>Use the evidence in your profile as the starting point. Your answer can still sound like you.</p></div><div className="interview-progress"><strong>{questions.filter((question) => question.prepared).length}/{questions.length}</strong><span>prepared</span><ProgressBar value={(questions.filter((question) => question.prepared).length / questions.length) * 100} /></div></div><div className="filter-row"><div className="filter-tabs">{["All", "Technical", "Project", "Role-specific", "Behavioral"].map((item) => <button key={item} className={category === item ? "active" : ""} onClick={() => setCategory(item as typeof category)}>{item}</button>)}</div><span className="filter-note"><Lightning size={15} weight="fill" aria-hidden="true" /> 4 tailored questions</span></div><div className="interview-list">{visible.map((question, index) => <Card className={`interview-question ${question.prepared ? "prepared" : ""}`} key={question.id}><div className="interview-question-number">0{index + 1}</div><div className="interview-question-content"><div className="interview-question-head"><Badge tone={question.category === "Technical" ? "blue" : question.category === "Project" ? "purple" : question.category === "Behavioral" ? "orange" : "green"}>{question.category}</Badge>{question.prepared ? <Badge tone="green"><Check size={13} weight="bold" aria-hidden="true" /> Prepared</Badge> : null}</div><h2>{question.question}</h2><div className="question-evidence"><div><span>Why it may be asked</span><p>{question.why}</p></div><div><span>Your evidence</span><p>{question.evidence}</p></div></div><button className="prepare-toggle" onClick={() => { setQuestions((items) => items.map((item) => item.id === question.id ? { ...item, prepared: !item.prepared } : item)); onToast(question.prepared ? "Marked for review" : "Marked as prepared", "Your interview plan is updated."); }}>{question.prepared ? <CheckCircle size={17} weight="fill" aria-hidden="true" /> : <span className="empty-check" />} {question.prepared ? "Prepared" : "Mark as prepared"}</button></div></Card>)}</div></PageFrame>;
}

export function ApplicationsView({ applications, setApplications, onNavigate }: { applications: Application[]; setApplications: React.Dispatch<React.SetStateAction<Application[]>>; onNavigate: (view: AppView) => void }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"All" | ApplicationStatus>("All");
  const visible = applications.filter((app) => (filter === "All" || app.status === filter) && `${app.company} ${app.role}`.toLowerCase().includes(query.toLowerCase()));
  const updateStatus = async (id: string, status: ApplicationStatus) => { await updateApplicationStatus(id, status); setApplications((items) => items.map((item) => item.id === id ? { ...item, status } : item)); };
  return <PageFrame><ViewTitle eyebrow="Application Tracker" title="Applications" description="A calm view of every role you are considering or moving through." actions={<Button icon={<Plus size={17} weight="bold" aria-hidden="true" />} onClick={() => onNavigate("add-job")}>Add Job</Button>} /><div className="application-summary"><div><span>All applications</span><strong>{applications.length}</strong></div><div><span>In motion</span><strong>{applications.filter((app) => ["Applied", "Screening", "Interview", "Technical Round", "Final Round"].includes(app.status)).length}</strong></div><div><span>Interview stage</span><strong>{applications.filter((app) => ["Interview", "Technical Round", "Final Round"].includes(app.status)).length}</strong></div><div><span>Average match</span><strong>{Math.round(applications.reduce((sum, app) => sum + app.matchScore, 0) / applications.length)}%</strong></div></div><Card className="applications-card"><div className="applications-toolbar"><label className="table-search"><MagnifyingGlass size={16} aria-hidden="true" /><input aria-label="Search applications" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search company or role…" /></label><div className="filter-select-wrap"><Funnel size={15} aria-hidden="true" /><select aria-label="Filter applications" value={filter} onChange={(event) => setFilter(event.target.value as typeof filter)}><option>All</option>{(["Saved", "Applied", "Screening", "Interview", "Technical Round", "Final Round", "Offer", "Rejected"] as ApplicationStatus[]).map((status) => <option key={status}>{status}</option>)}</select><CaretDown size={15} aria-hidden="true" /></div></div><div className="applications-table"><div className="application-table-head"><span>Company & role</span><span>Match</span><span>Status</span><span>Next step</span><span>Added</span><span /></div>{visible.map((app) => <div className="application-table-row" key={app.id}><button className="application-role" onClick={() => onNavigate("application-detail")}><CompanyMark initials={app.initials} /><span><strong>{app.company}</strong><small>{app.role} · {app.location}</small></span></button><span className="match-number">{app.matchScore}%</span><select className="status-select" aria-label={`Status for ${app.company}`} value={app.status} onChange={(event) => updateStatus(app.id, event.target.value as ApplicationStatus)}><option>{app.status}</option>{(["Saved", "Applied", "Screening", "Interview", "Technical Round", "Final Round", "Offer", "Rejected", "Withdrawn"] as ApplicationStatus[]).filter((status) => status !== app.status).map((status) => <option key={status}>{status}</option>)}</select><span className="application-next">{app.nextStep}{app.nextDate ? <small>{app.nextDate}</small> : null}</span><span className="application-date">{app.appliedDate}</span><IconButton label={`More options for ${app.company}`} onClick={() => onNavigate("application-detail")}><DotsThree size={20} aria-hidden="true" /></IconButton></div>)}</div>{visible.length === 0 ? <div className="empty-state"><MagnifyingGlass size={28} aria-hidden="true" /><h2>No applications found</h2><p>Try a different company name or clear the status filter.</p></div> : null}</Card></PageFrame>;
}

export function ApplicationDetailView({ application, onBack, onToast }: { application: Application; onBack: () => void; onToast: (title: string, message: string) => void }) {
  const stages: ApplicationStatus[] = ["Saved", "Applied", "Screening", "Interview", "Technical Round", "Final Round", "Offer"];
  const current = stages.indexOf(application.status);
  const [note, setNote] = useState(application.note);
  const [status, setStatus] = useState(application.status);
  return <PageFrame><button className="back-link" onClick={onBack}><ArrowLeft size={16} aria-hidden="true" /> Back to Applications</button><ViewTitle eyebrow="Application Detail" title={application.role} description={`${application.company} · ${application.location}`} actions={<StatusBadge status={status} />} /><div className="detail-grid"><div className="detail-main"><Card className="status-card"><div className="card-heading"><div><p className="eyebrow">Application progress</p><h2>Keep the next step visible</h2></div><Button variant="secondary" size="sm" onClick={() => onToast("Status updated", "The application timeline is ready for your next update.")}>Update Status</Button></div><div className="status-timeline">{stages.map((stage, index) => <button key={stage} className={`timeline-stage ${index <= current ? "complete" : ""} ${stage === status ? "current" : ""}`} onClick={() => setStatus(stage)}><span>{index < current ? <Check size={13} weight="bold" aria-hidden="true" /> : index === current ? <span /> : null}</span><small>{stage}</small></button>)}</div></Card><Card><div className="card-heading"><div><p className="eyebrow">Your notes</p><h2>Keep the context close</h2></div><Badge tone="blue">Private note</Badge></div><TextareaField label="Application note" name="application-note" value={note} onChange={(event) => setNote(event.target.value)} rows={5} /><div className="detail-card-footer"><span>Last edited just now</span><Button size="sm" onClick={() => onToast("Note saved", "Your private application note is updated.")}>Save Note</Button></div></Card><Card><div className="card-heading"><div><p className="eyebrow">Artifacts</p><h2>Documents attached</h2></div><Button variant="quiet" size="sm" onClick={() => onToast("Add artifact", "Choose a document version to attach here.")} icon={<Plus size={15} aria-hidden="true" />}>Add</Button></div><div className="artifact-list"><button onClick={() => onToast("CV v3", "Opening the saved CV version.")}><span className="artifact-icon artifact-blue"><FileText size={17} aria-hidden="true" /></span><span><strong>Tailored CV v3</strong><small>Created Oct 02 · Signal template</small></span><ArrowUpRight size={16} aria-hidden="true" /></button><button onClick={() => onToast("Cover Email v1", "Opening the saved email draft.")}><span className="artifact-icon artifact-purple"><EnvelopeSimple size={17} aria-hidden="true" /></span><span><strong>Cover Email v1</strong><small>Created Oct 02 · Evidence aligned</small></span><ArrowUpRight size={16} aria-hidden="true" /></button><button onClick={() => onToast("Interview Prep v1", "Opening the interview plan.")}><span className="artifact-icon artifact-green"><BookOpen size={17} aria-hidden="true" /></span><span><strong>Interview Prep v1</strong><small>4 questions · 1 prepared</small></span><ArrowUpRight size={16} aria-hidden="true" /></button></div></Card></div><aside className="detail-side"><Card className="detail-company"><CompanyMark initials={application.initials} tone="purple" /><h2>{application.company}</h2><p>{application.role}</p><a href="#job"><LinkSimple size={14} aria-hidden="true" /> Job description</a><div className="detail-meta"><span><CalendarBlank size={15} aria-hidden="true" /> Added {application.appliedDate}</span><span><Target size={15} aria-hidden="true" /> {application.matchScore}% match</span><span><MapPin size={15} aria-hidden="true" /> {application.location}</span></div></Card><Card><div className="card-heading"><div><p className="eyebrow">Next step</p><h2>{application.nextStep}</h2></div><Badge tone="amber">{application.nextDate || "No date"}</Badge></div><p className="next-step-detail">Use your design system story as the anchor. Keep the metric and the adoption outcome together.</p><Button className="full-width" variant="secondary" onClick={() => onToast("Reminder set", "You will see this next step in the tracker.")}>Set Reminder</Button></Card></aside></div></PageFrame>;
}

export function SettingsView({
  onToast,
  onSignOut,
  userName = "Aarav Mehta",
  userEmail = "aarav.mehta@example.com",
}: {
  onToast: (title: string, message: string) => void;
  onSignOut?: () => void;
  userName?: string;
  userEmail?: string;
}) {
  const [notifications, setNotifications] = useState({ applications: true, weekly: true, product: false });
  return (
    <PageFrame>
      <ViewTitle
        eyebrow="Workspace"
        title="Settings"
        description="Control how your profile and application workspace behave."
        actions={
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {onSignOut ? (
              <Button variant="secondary" onClick={onSignOut}>
                Sign Out
              </Button>
            ) : null}
            <Button onClick={() => onToast("Settings saved", "Your workspace preferences are updated.")}>
              Save Changes
            </Button>
          </div>
        }
      />
      <div className="settings-layout">
        <Card>
          <div className="card-heading">
            <div>
              <p className="eyebrow">Account</p>
              <h2>Personal details</h2>
            </div>
            <Badge tone="green">Verified Session</Badge>
          </div>
          <div className="profile-form-grid">
            <Field label="Full name" name="settings-name" defaultValue={userName} key={userName} autoComplete="name" />
            <Field label="Email address" name="settings-email" type="email" defaultValue={userEmail} key={userEmail} autoComplete="email" />
            <Field label="Location" name="settings-location" defaultValue="Bengaluru, India" autoComplete="address-level2" />
            <SelectField label="Default CV template" name="settings-template" defaultValue="signal">
              <option value="signal">Signal</option>
              <option value="editorial">Editorial</option>
              <option value="compact">Compact</option>
            </SelectField>
          </div>
        </Card>
        <Card>
          <div className="card-heading">
            <div>
              <p className="eyebrow">Notifications</p>
              <h2>Useful, not noisy</h2>
            </div>
            <Bell size={21} aria-hidden="true" />
          </div>
          <div className="settings-toggles">
            <label>
              <span>
                <strong>Application reminders</strong>
                <small>Upcoming interviews and follow-ups.</small>
              </span>
              <input
                type="checkbox"
                checked={notifications.applications}
                onChange={(event) => setNotifications({ ...notifications, applications: event.target.checked })}
              />
            </label>
            <label>
              <span>
                <strong>Weekly profile check-in</strong>
                <small>One useful suggestion to keep your evidence fresh.</small>
              </span>
              <input
                type="checkbox"
                checked={notifications.weekly}
                onChange={(event) => setNotifications({ ...notifications, weekly: event.target.checked })}
              />
            </label>
            <label>
              <span>
                <strong>Product updates</strong>
                <small>New workflow features and improvements.</small>
              </span>
              <input
                type="checkbox"
                checked={notifications.product}
                onChange={(event) => setNotifications({ ...notifications, product: event.target.checked })}
              />
            </label>
          </div>
        </Card>
        <Card>
          <div className="card-heading">
            <div>
              <p className="eyebrow">Data & privacy</p>
              <h2>Your information stays yours</h2>
            </div>
            <SealCheck size={21} weight="fill" aria-hidden="true" />
          </div>
          <div className="settings-links">
            {onSignOut ? (
              <button onClick={onSignOut}>
                <span>
                  <ArrowRight size={17} aria-hidden="true" />
                  <strong>Sign out of workspace</strong>
                  <small>Revoke current session token on the backend.</small>
                </span>
                <ArrowUpRight size={16} aria-hidden="true" />
              </button>
            ) : null}
            <button onClick={() => onToast("Export requested", "A downloadable profile export would be prepared here.")}>
              <span>
                <DownloadSimple size={17} aria-hidden="true" />
                <strong>Export your profile</strong>
                <small>Download your verified profile and evidence.</small>
              </span>
              <ArrowUpRight size={16} aria-hidden="true" />
            </button>
            <button onClick={() => onToast("Sessions checked", "Active FastAPI session verified.")}>
              <span>
                <UsersThree size={17} aria-hidden="true" />
                <strong>Review active sessions</strong>
                <small>Connected to PostgreSQL authentication.</small>
              </span>
              <ArrowUpRight size={16} aria-hidden="true" />
            </button>
            <button className="danger-link" onClick={() => onToast("Account deletion", "This destructive flow requires explicit confirmation in production.")}>
              <span>
                <Trash size={17} aria-hidden="true" />
                <strong>Delete account</strong>
                <small>This would permanently remove your workspace.</small>
              </span>
              <ArrowUpRight size={16} aria-hidden="true" />
            </button>
          </div>
        </Card>
      </div>
    </PageFrame>
  );
}
