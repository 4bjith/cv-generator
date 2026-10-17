import {
  Application,
  AtsReport,
  CandidateProfile,
  ClarificationQuestion,
  CvDocument,
  Education,
  Experience,
  InterviewQuestion,
  Job,
  Project,
  Skill,
} from "@/types";

export const mockProfile: CandidateProfile = {
  name: "Aarav Mehta",
  role: "Frontend Engineer",
  location: "Bengaluru, India",
  email: "aarav.mehta@example.com",
  phone: "+91 98765 43210",
  summary:
    "Frontend engineer who turns complex product workflows into clear, fast interfaces. Strong in React, TypeScript, and design systems, with a bias toward evidence-backed decisions.",
  yearsExperience: 4,
  profileScore: 82,
  linkedin: "linkedin.com/in/aaravmehta",
  github: "github.com/aaravmehta",
};

export const mockSkills: Skill[] = [
  { id: "react", name: "React", category: "Frontend", evidenceCount: 6, confidence: 96, status: "verified" },
  { id: "typescript", name: "TypeScript", category: "Frontend", evidenceCount: 5, confidence: 94, status: "verified" },
  { id: "next", name: "Next.js", category: "Frontend", evidenceCount: 4, confidence: 88, status: "verified" },
  { id: "design-systems", name: "Design Systems", category: "Product", evidenceCount: 3, confidence: 86, status: "verified" },
  { id: "node", name: "Node.js", category: "Backend", evidenceCount: 3, confidence: 76, status: "verified" },
  { id: "testing", name: "Jest", category: "Quality", evidenceCount: 1, confidence: 54, status: "review" },
];

export const mockExperience: Experience[] = [
  {
    id: "northstar",
    company: "Northstar Labs",
    role: "Frontend Engineer",
    start: "Jan 2023",
    end: "Present",
    location: "Bengaluru, India",
    description: "Own the frontend platform for a workflow automation product used by 20,000+ operators.",
    highlights: [
      "Reduced task completion time by 31% through a reusable command and review flow.",
      "Created a token-driven component system adopted by 4 product teams.",
      "Partnered with research and product to turn qualitative findings into shippable UI decisions.",
    ],
  },
  {
    id: "orbit",
    company: "Orbit Commerce",
    role: "Product Engineer",
    start: "Jul 2021",
    end: "Dec 2022",
    location: "Remote",
    description: "Built customer-facing commerce flows across web and mobile web.",
    highlights: [
      "Improved mobile checkout conversion by 18% after a progressive disclosure redesign.",
      "Introduced typed API contracts and shared validation for a high-volume checkout surface.",
    ],
  },
];

export const mockEducation: Education[] = [
  { id: "pes", school: "PES University", degree: "B.Tech in Computer Science", period: "2017 to 2021", detail: "Bengaluru, India" },
];

export const mockProjects: Project[] = [
  {
    id: "voyago",
    name: "Voyago",
    description: "Real-time travel planning workspace with collaborative itineraries and location-aware recommendations.",
    stack: ["Next.js", "TypeScript", "Socket.IO", "PostgreSQL"],
    stars: 42,
    forks: 8,
    lastUpdated: "2 days ago",
    analyzed: true,
    repoUrl: "github.com/aaravmehta/voyago",
  },
  {
    id: "signalboard",
    name: "Signalboard",
    description: "A lightweight observability dashboard for product teams to spot workflow friction before it becomes a ticket.",
    stack: ["React", "Vite", "Node.js", "Chart.js"],
    stars: 19,
    forks: 3,
    lastUpdated: "1 week ago",
    analyzed: true,
    repoUrl: "github.com/aaravmehta/signalboard",
  },
  {
    id: "papertrail",
    name: "Papertrail",
    description: "A small document tagging experiment that explores keyboard-first review patterns.",
    stack: ["React", "Zod", "SQLite"],
    stars: 7,
    forks: 1,
    lastUpdated: "3 weeks ago",
    analyzed: false,
    repoUrl: "github.com/aaravmehta/papertrail",
  },
];

export const mockJob: Job = {
  id: "lattice-frontend",
  company: "Lattice Systems",
  title: "Senior Frontend Engineer",
  location: "Bengaluru or Remote",
  mode: "Hybrid",
  salary: "₹28L to ₹38L",
  posted: "Posted 2 days ago",
  description:
    "Lattice Systems is building the operating layer for modern support teams. You will shape the web platform used by thousands of agents, working closely with product, design, and infrastructure.",
  matchScore: 84,
  requirements: [
    { id: "react", name: "React", type: "required", state: "strong", evidence: "6 verified evidence items", note: "Northstar platform and Voyago" },
    { id: "typescript", name: "TypeScript", type: "required", state: "strong", evidence: "5 verified evidence items", note: "Used across recent work" },
    { id: "design-systems", name: "Design systems", type: "required", state: "strong", evidence: "3 verified evidence items", note: "Token-driven system at Northstar" },
    { id: "testing", name: "Jest or Vitest", type: "required", state: "partial", evidence: "1 review item", note: "Needs one user confirmation" },
    { id: "graphql", name: "GraphQL", type: "preferred", state: "weak", evidence: "Mentioned in a project dependency", note: "Personal contribution unclear" },
    { id: "accessibility", name: "Accessible UI", type: "required", state: "strong", evidence: "4 verified evidence items", note: "Review flow and component library" },
    { id: "mentoring", name: "Mentoring", type: "preferred", state: "unknown", note: "No reliable evidence yet" },
  ],
};

export const mockQuestions: ClarificationQuestion[] = [
  {
    id: "jest",
    requirement: "Jest or Vitest",
    question: "Which testing framework did you use at Northstar Labs, and what did you test with it?",
    context: "The job asks for production-quality frontend testing. We found one review item that needs your confirmation.",
    answered: false,
  },
  {
    id: "graphql",
    requirement: "GraphQL",
    question: "Did you personally build or maintain GraphQL integrations in Voyago or another project?",
    context: "GraphQL appears in a project dependency, but your exact contribution is not yet clear.",
    answered: false,
  },
  {
    id: "mentoring",
    requirement: "Mentoring",
    question: "Have you mentored teammates, interns, or community members in a structured way?",
    context: "This is a preferred skill. You can skip it if it does not belong in your professional profile.",
    answered: false,
  },
];

export const mockCv: CvDocument = {
  title: "Senior Frontend Engineer",
  candidateName: "Aarav Mehta",
  targetRole: "Senior Frontend Engineer at Lattice Systems",
  template: "signal",
  version: 3,
  updatedAt: "Today at 10:42 AM",
  sections: [
    {
      id: "summary",
      title: "Summary",
      visible: true,
      content: ["Frontend engineer with 4 years of experience shaping clear, fast workflows with React, TypeScript, and design systems."],
    },
    {
      id: "experience",
      title: "Experience",
      visible: true,
      content: ["Frontend Engineer, Northstar Labs | Jan 2023 to Present", "Product Engineer, Orbit Commerce | Jul 2021 to Dec 2022"],
    },
    {
      id: "projects",
      title: "Selected Projects",
      visible: true,
      content: ["Voyago | Next.js, TypeScript, Socket.IO, PostgreSQL", "Signalboard | React, Vite, Node.js, Chart.js"],
    },
    { id: "skills", title: "Skills", visible: true, content: ["React, TypeScript, Next.js, Design Systems, Node.js, Jest, Accessibility"] },
    { id: "education", title: "Education", visible: true, content: ["B.Tech in Computer Science, PES University | 2017 to 2021"] },
  ],
};

export const mockAts: AtsReport = {
  score: 88,
  keywordCoverage: 78,
  missingKeywords: ["GraphQL", "Vitest", "Mentoring"],
  checks: [
    { id: "keywords", label: "Keyword coverage", detail: "14 of 18 high-signal terms appear naturally.", status: "pass" },
    { id: "sections", label: "Standard sections", detail: "All expected sections are easy for parsers to identify.", status: "pass" },
    { id: "contact", label: "Contact details", detail: "Email, phone, location, and profile links are present.", status: "pass" },
    { id: "density", label: "Content density", detail: "Experience bullets are concise and scan-friendly.", status: "pass" },
    { id: "missing", label: "Missing terms", detail: "3 preferred or uncertain terms need review before export.", status: "warning" },
  ],
};

export const mockInterview: InterviewQuestion[] = [
  { id: "q1", category: "Technical", question: "How would you structure a React feature that needs to stay fast as the workflow grows?", why: "The role owns a large product surface with complex operator flows.", evidence: "Northstar workflow platform", prepared: false },
  { id: "q2", category: "Project", question: "Walk us through the real-time architecture behind Voyago.", why: "The project gives you a concrete way to show systems thinking.", evidence: "Voyago and Socket.IO", prepared: true },
  { id: "q3", category: "Role-specific", question: "How do you decide when a component belongs in a design system?", why: "Lattice is looking for someone who can scale patterns across teams.", evidence: "Northstar token-driven system", prepared: false },
  { id: "q4", category: "Behavioral", question: "Tell us about a time user research changed a frontend decision.", why: "The team works closely with product and design partners.", evidence: "Northstar research partnership", prepared: false },
];

export const mockApplications: Application[] = [
  { id: "app-1", company: "Lattice Systems", role: "Senior Frontend Engineer", location: "Bengaluru or Remote", status: "Interview", matchScore: 84, appliedDate: "Sep 28, 2026", nextStep: "Technical interview", nextDate: "Oct 08", initials: "LS", note: "Strong product fit. Prepare a concise story about the design system rollout." },
  { id: "app-2", company: "Pinecone Studio", role: "Product Engineer", location: "Remote", status: "Screening", matchScore: 76, appliedDate: "Sep 24, 2026", nextStep: "Recruiter call", nextDate: "Oct 04", initials: "PS", note: "Emphasize cross-functional work and performance wins." },
  { id: "app-3", company: "Cedar Health", role: "Frontend Platform Engineer", location: "Hyderabad", status: "Applied", matchScore: 71, appliedDate: "Sep 20, 2026", nextStep: "Waiting for response", initials: "CH", note: "Application sent with CV v2." },
  { id: "app-4", company: "Kite Commerce", role: "Senior React Engineer", location: "Remote", status: "Saved", matchScore: 68, appliedDate: "Sep 18, 2026", nextStep: "Tailor application", initials: "KC", note: "Needs a stronger testing story before applying." },
];
