import { describe, it, expect } from "vitest";
import React from "react";
import { renderToString } from "react-dom/server";
import {
  getAllTemplates,
  getTemplate,
  registerTemplate,
  MODERN_PROFESSIONAL,
  CLASSIC_EXECUTIVE,
  ATS_MINIMAL,
  TECHNICAL_DEVELOPER,
  CONTEMPORARY_TWO_COLUMN,
  ACADEMIC_RESEARCH,
} from "@/components/cv/templates/registry";
import { TemplateDefinition } from "@/components/cv/templates/types";
import { CVContentSnapshot, CVPresentationSnapshot } from "@/types/cv";

const sampleSnapshot: CVContentSnapshot = {
  schema_version: "2.0.0",
  basics: {
    name: "Dr. Evelyn Reed",
    label: "Principal AI Research Scientist",
    email: "evelyn.reed@example.com",
    phone: "+1 555-0199",
    url: "https://evelynreed.ai",
    summary: "Distinguished researcher with 10+ years advancing deep learning architectures, transformer models, and scalable distributed training.",
    location: {
      city: "Cambridge",
      region: "MA",
      country: "USA",
      countryCode: "US",
    },
    profiles: [
      { network: "GitHub", username: "ereed", url: "https://github.com/ereed" },
      { network: "LinkedIn", username: "evelynreed", url: "https://linkedin.com/in/evelynreed" },
    ],
  },
  work: [
    {
      id: "exp-1",
      name: "DeepMind Horizon Labs",
      position: "Lead Research Scientist",
      startDate: "2021-03",
      is_current: true,
      summary: "Directing neural architecture search and multimodal transformer research.",
      highlights: [
        "Architected sparse attention mechanism improving inference speed by 3.2x.",
        "Published 4 tier-1 papers at NeurIPS and ICML.",
      ],
      metrics: [
        { metric_name: "Inference Speedup", value: "3.2x", context: "Sparse attention" },
      ],
      technologies: ["PyTorch", "JAX", "CUDA", "TensorRT"],
    },
    {
      id: "exp-2",
      name: "MIT CSAIL",
      position: "Postdoctoral Research Fellow",
      startDate: "2018-09",
      endDate: "2021-02",
      summary: "Investigated sample-efficient reinforcement learning algorithms.",
      highlights: [
        "Authored open-source benchmark library adopted by 50+ research labs.",
      ],
      technologies: ["Python", "TensorFlow", "Ray"],
    },
  ],
  education: [
    {
      id: "edu-1",
      institution: "Massachusetts Institute of Technology",
      studyType: "Ph.D.",
      area: "Computer Science & Artificial Intelligence",
      startDate: "2014-09",
      endDate: "2018-06",
      score: "4.0 GPA",
      courses: ["Advanced Machine Learning", "Distributed Computing"],
      achievements: ["Doctoral Fellowship Award", "Best Thesis Finalist"],
    },
  ],
  skills: [
    { id: "sk-1", name: "PyTorch", category: "Frameworks", proficiency: "Expert" },
    { id: "sk-2", name: "JAX", category: "Frameworks", proficiency: "Advanced" },
    { id: "sk-3", name: "Distributed Training", category: "Core Competencies", proficiency: "Expert" },
    { id: "sk-4", name: "C++", category: "Languages", proficiency: "Proficient" },
  ],
  projects: [
    {
      id: "proj-1",
      name: "SparseTransformer-X",
      role: "Lead Author & Maintainer",
      url: "https://github.com/ereed/sparse-transformer",
      description: "High-performance transformer implementation for long-context sequences.",
      highlights: ["Achieved state-of-the-art memory efficiency on 100k token contexts."],
      technologies: ["Python", "C++", "Triton"],
    },
  ],
  certificates: [
    {
      id: "cert-1",
      name: "AWS Certified Machine Learning - Specialty",
      issuer: "Amazon Web Services",
      date: "2022-05",
      url: "https://aws.amazon.com/verify/123",
    },
  ],
  awards: [
    {
      id: "award-1",
      title: "Outstanding Research Paper Award",
      awarder: "NeurIPS 2023",
      date: "2023-12",
      summary: "Recognized among top 1% of submissions for breakthroughs in sparse attention.",
    },
  ],
  languages: [
    { id: "lang-1", language: "English", fluency: "Native" },
    { id: "lang-2", language: "German", fluency: "Professional" },
  ],
  presentation: {
    template: "modern-professional",
    typography: "sans",
    color_scheme: "slate",
    page_size: "a4",
    spacing: "normal",
    section_order: [
      "basics",
      "work",
      "skills",
      "projects",
      "education",
      "certificates",
      "awards",
      "languages",
    ],
    section_visibility: {
      basics: true,
      work: true,
      skills: true,
      projects: true,
      education: true,
      certificates: true,
      awards: true,
      languages: true,
    },
    item_visibility: {},
  },
};

describe("CV Template Design System & Registry", () => {
  it("registers all six distinct templates at launch with complete metadata", () => {
    const templates = getAllTemplates();
    expect(templates.length).toBeGreaterThanOrEqual(6);

    const ids = templates.map((t) => t.id);
    expect(ids).toContain("modern-professional");
    expect(ids).toContain("classic-executive");
    expect(ids).toContain("ats-minimal");
    expect(ids).toContain("technical-developer");
    expect(ids).toContain("contemporary-two-column");
    expect(ids).toContain("academic-research");

    templates.forEach((t) => {
      expect(t.name).toBeTruthy();
      expect(t.description).toBeTruthy();
      expect(t.recommendedFor).toBeTruthy();
      expect(t.component).toBeTypeOf("function");
      expect(t.features.length).toBeGreaterThan(0);
    });
  });

  it("resolves template aliases and falls back gracefully", () => {
    expect(getTemplate("modern").id).toBe("modern-professional");
    expect(getTemplate("corporate").id).toBe("modern-professional");
    expect(getTemplate("executive").id).toBe("classic-executive");
    expect(getTemplate("minimal").id).toBe("ats-minimal");
    expect(getTemplate("ats").id).toBe("ats-minimal");
    expect(getTemplate("technical").id).toBe("technical-developer");
    expect(getTemplate("two-column").id).toBe("contemporary-two-column");
    expect(getTemplate("academic").id).toBe("academic-research");
    expect(getTemplate("non-existent-template").id).toBe("modern-professional");
    expect(getTemplate(null).id).toBe("modern-professional");
  });

  it("allows registering an additional custom template without modifying core", () => {
    const customTemplate: TemplateDefinition = {
      id: "creative-portfolio",
      aliases: ["creative"],
      name: "Creative Portfolio",
      category: "Creative",
      description: "Expressive design with bold visual accents.",
      recommendedFor: "Designers and art directors.",
      defaultTypography: "sans",
      defaultColorScheme: "emerald",
      layoutType: "single-column",
      features: ["Custom hero", "Bold typography"],
      component: () => React.createElement("div", { className: "custom-template" }, "Custom Output"),
    };

    registerTemplate(customTemplate);
    expect(getTemplate("creative-portfolio").name).toBe("Creative Portfolio");
    expect(getTemplate("creative").name).toBe("Creative Portfolio");
  });

  it("renders Template 1 (Modern Professional) with corporate single-column styling", () => {
    const TemplateComp = MODERN_PROFESSIONAL.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: sampleSnapshot.presentation })
    );

    expect(html).toContain("template-modern-professional");
    expect(html).toContain("Dr. Evelyn Reed");
    expect(html).toContain("Principal AI Research Scientist");
    expect(html).toContain("DeepMind Horizon Labs");
    expect(html).toContain("sparse attention mechanism");
    expect(html).toContain("3.2x");
  });

  it("renders Template 2 (Classic Executive) with centered header and leadership focus", () => {
    const TemplateComp = CLASSIC_EXECUTIVE.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: sampleSnapshot.presentation })
    );

    expect(html).toContain("template-classic-executive");
    expect(html).toContain("Dr. Evelyn Reed");
    expect(html).toContain("cv-header-center");
    expect(html).toContain("Executive Profile");
    expect(html).toContain("Leadership &amp; Career History");
  });

  it("renders Template 3 (ATS-Friendly Minimal) with text-first linear structure and zero decorative friction", () => {
    const TemplateComp = ATS_MINIMAL.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: sampleSnapshot.presentation })
    );

    expect(html).toContain("template-ats-minimal");
    expect(html).toContain("Dr. Evelyn Reed");
    expect(html).toContain("PROFESSIONAL SUMMARY");
    expect(html).toContain("WORK EXPERIENCE");
    expect(html).toContain("SKILLS");
  });

  it("renders Template 4 (Technical Developer) with monospace accents and technical skills matrix", () => {
    const TemplateComp = TECHNICAL_DEVELOPER.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: sampleSnapshot.presentation })
    );

    expect(html).toContain("template-technical-developer");
    expect(html).toContain("Dr. Evelyn Reed");
    expect(html).toContain("// TECHNICAL SKILLS &amp; STACK");
    expect(html).toContain("// ENGINEERING EXPERIENCE");
    expect(html).toContain("// SYSTEMS &amp; OPEN SOURCE PROJECTS");
    expect(html).toContain("SparseTransformer-X");
  });

  it("renders Template 5 (Contemporary Two-Column) with asymmetric sidebar and main column", () => {
    const TemplateComp = CONTEMPORARY_TWO_COLUMN.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: sampleSnapshot.presentation })
    );

    expect(html).toContain("template-contemporary-two-column");
    expect(html).toContain("<aside");
    expect(html).toContain("<main");
    expect(html).toContain("Dr. Evelyn Reed");
    expect(html).toContain("evelyn.reed@example.com");
  });

  it("renders Template 6 (Academic Research) with education-first scholarly hierarchy and publications", () => {
    const TemplateComp = ACADEMIC_RESEARCH.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: sampleSnapshot.presentation })
    );

    expect(html).toContain("template-academic-research");
    expect(html).toContain("Dr. Evelyn Reed");
    expect(html).toContain("EDUCATION &amp; ACADEMIC APPOINTMENTS");
    expect(html).toContain("RESEARCH &amp; TEACHING EXPERIENCE");
    expect(html).toContain("PUBLICATIONS &amp; RESEARCH PROJECTS");
    expect(html).toContain("GRANTS, HONORS &amp; FELLOWSHIPS");
    expect(html).toContain("Massachusetts Institute of Technology");
  });

  it("respects section visibility settings cleanly without broken headers", () => {
    const presentationWithHidden: CVPresentationSnapshot = {
      ...sampleSnapshot.presentation!,
      section_visibility: {
        ...sampleSnapshot.presentation!.section_visibility,
        projects: false,
        awards: false,
      },
    };

    const TemplateComp = MODERN_PROFESSIONAL.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: presentationWithHidden })
    );

    expect(html).not.toContain("Featured Projects");
    expect(html).not.toContain("SparseTransformer-X");
    expect(html).not.toContain("Honors &amp; Achievements");
    // Work and Education remain visible
    expect(html).toContain("Professional Experience");
    expect(html).toContain("Education");
  });

  it("respects individual item visibility settings", () => {
    const presentationWithHiddenItem: CVPresentationSnapshot = {
      ...sampleSnapshot.presentation!,
      item_visibility: {
        "exp-1": false, // hide DeepMind Horizon Labs
      },
    };

    const TemplateComp = MODERN_PROFESSIONAL.component;
    const html = renderToString(
      React.createElement(TemplateComp, { snapshot: sampleSnapshot, presentation: presentationWithHiddenItem })
    );

    expect(html).not.toContain("DeepMind Horizon Labs");
    // exp-2 remains visible
    expect(html).toContain("MIT CSAIL");
  });

  it("handles missing and optional fields gracefully without crashing", () => {
    const minimalSnapshot: CVContentSnapshot = {
      schema_version: "2.0.0",
      basics: {
        name: "Jane Doe",
      },
      work: [],
      education: [],
      skills: [],
    };

    // Render all 6 launch templates against minimal snapshot
    const launchTemplates = [
      MODERN_PROFESSIONAL,
      CLASSIC_EXECUTIVE,
      ATS_MINIMAL,
      TECHNICAL_DEVELOPER,
      CONTEMPORARY_TWO_COLUMN,
      ACADEMIC_RESEARCH,
    ];
    launchTemplates.forEach((tpl) => {
      expect(() => {
        const Comp = tpl.component;
        const html = renderToString(React.createElement(Comp, { snapshot: minimalSnapshot }));
        expect(html).toContain("Jane Doe");
      }).not.toThrow();
    });
  });

  it("verifies layout types and default styles for all templates", () => {
    const templates = getAllTemplates();
    const layoutTypes = templates.map((t) => t.layoutType);
    expect(layoutTypes).toContain("single-column");
    expect(layoutTypes).toContain("two-column");
    expect(layoutTypes).toContain("academic-dense");

    expect(MODERN_PROFESSIONAL.layoutType).toBe("single-column");
    expect(CLASSIC_EXECUTIVE.layoutType).toBe("single-column");
    expect(ATS_MINIMAL.layoutType).toBe("single-column");
    expect(TECHNICAL_DEVELOPER.layoutType).toBe("single-column");
    expect(CONTEMPORARY_TWO_COLUMN.layoutType).toBe("two-column");
    expect(ACADEMIC_RESEARCH.layoutType).toBe("academic-dense");

    expect(MODERN_PROFESSIONAL.defaultTypography).toBe("sans");
    expect(CLASSIC_EXECUTIVE.defaultTypography).toBe("serif");
    expect(ATS_MINIMAL.defaultTypography).toBe("sans");
    expect(TECHNICAL_DEVELOPER.defaultTypography).toBe("mono");
    expect(CONTEMPORARY_TWO_COLUMN.defaultTypography).toBe("sans");
    expect(ACADEMIC_RESEARCH.defaultTypography).toBe("serif");
  });
});
