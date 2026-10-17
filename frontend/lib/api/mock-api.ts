import { mockAts, mockApplications, mockCv, mockInterview, mockJob, mockProjects, mockQuestions } from "@/lib/mock";
import { ApplicationStatus, CvDocument, Job, Project } from "@/types";

const wait = (milliseconds = 450) => new Promise((resolve) => setTimeout(resolve, milliseconds));

export async function getDashboardData() {
  await wait(180);
  return { applications: mockApplications, job: mockJob, profileScore: 82 };
}

export async function getJobAnalysis(): Promise<Job> {
  await wait(600);
  return structuredClone(mockJob);
}

export async function analyzeRepository(project: Project): Promise<Project> {
  await wait(950);
  return { ...project, analyzed: true, lastUpdated: "Just now" };
}

export async function submitClarification(questionId: string, answer: string) {
  await wait(450);
  return { questionId, answer, answered: true };
}

export async function generateCv(): Promise<CvDocument> {
  await wait(1300);
  return { ...structuredClone(mockCv), version: mockCv.version + 1, updatedAt: "Just now" };
}

export async function generateCoverEmail() {
  await wait(850);
  return {
    subject: "Senior Frontend Engineer application: Aarav Mehta",
    body: `Hi Lattice team,\n\nI’m excited to apply for the Senior Frontend Engineer role. I’ve spent the last four years turning complex product workflows into fast, understandable interfaces, most recently leading frontend work for Northstar’s workflow platform.\n\nThe role’s focus on thoughtful systems and operator experience is a strong match for how I work. I’d love to share how I built a token-driven component system adopted by four teams and helped reduce task completion time by 31%.\n\nThank you for your time,\nAarav Mehta`,
  };
}

export async function updateApplicationStatus(applicationId: string, status: ApplicationStatus) {
  await wait(350);
  return { applicationId, status };
}

export async function getInterviewPrep() {
  await wait(250);
  return structuredClone(mockInterview);
}

export async function getAtsReport() {
  await wait(280);
  return structuredClone(mockAts);
}

export async function getClarifications() {
  await wait(250);
  return structuredClone(mockQuestions);
}
