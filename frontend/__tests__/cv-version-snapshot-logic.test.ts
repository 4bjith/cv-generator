import { describe, it, expect } from "vitest";
import { CVContentSnapshot, CVPresentationSnapshot } from "@/types/cv";

describe("Frontend CV Snapshot & Presentation Logic", () => {
  it("resolves canonical vs legacy fields correctly for display and edits", () => {
    // Legacy snapshot
    const legacySnapshot: CVContentSnapshot = {
      basics: {
        first_name: "Aarav",
        last_name: "Mehta",
        professional_headline: "Senior Backend Developer",
        base_summary: "Passionate developer with 6 years experience.",
        email: "aarav@example.com",
      },
      experiences: [
        {
          id: "exp-1",
          company: "Tech Corp",
          position: "Lead Dev",
          start_date: "2020-01-01",
          responsibilities: ["Built microservices", "Led team of 5"],
        },
      ],
      skills: [{ id: "sk-1", name: "Python", proficiency: "Expert" }],
      certifications: [{ id: "cert-1", name: "AWS Solutions Architect", issuer: "Amazon" }],
      achievements: [{ id: "ach-1", title: "Top Innovator 2023", awarder: "Tech Corp" }],
    };

    // Headline resolution
    const headline = legacySnapshot.basics?.label || legacySnapshot.basics?.professional_headline;
    expect(headline).toBe("Senior Backend Developer");

    // Summary resolution
    const summary = legacySnapshot.basics?.summary || legacySnapshot.basics?.base_summary;
    expect(summary).toBe("Passionate developer with 6 years experience.");

    // Work resolution
    const workList = legacySnapshot.work || legacySnapshot.experiences || [];
    expect(workList.length).toBe(1);
    expect(workList[0].position).toBe("Lead Dev");
    const bullets = workList[0].highlights || workList[0].responsibilities || [];
    expect(bullets).toEqual(["Built microservices", "Led team of 5"]);

    // Certificates resolution
    const certList = legacySnapshot.certificates || legacySnapshot.certifications || [];
    expect(certList.length).toBe(1);
    expect(certList[0].name).toBe("AWS Solutions Architect");

    // Awards resolution
    const awardList = legacySnapshot.awards || legacySnapshot.achievements || [];
    expect(awardList.length).toBe(1);
    expect(awardList[0].title).toBe("Top Innovator 2023");
  });

  it("handles canonical schema 2.0.0 snapshots with presentation settings", () => {
    const canonicalSnapshot: CVContentSnapshot = {
      schema_version: "2.0.0",
      basics: {
        name: "Priya Sharma",
        label: "Staff AI Engineer",
        summary: "Specialized in LLM architectures and agents.",
        email: "priya@example.com",
        location: {
          city: "Bengaluru",
          region: "Karnataka",
          countryCode: "IN",
        },
      },
      work: [
        {
          id: "work-1",
          name: "DeepMind Partner",
          position: "Staff AI Engineer",
          startDate: "2022-01-01",
          highlights: ["Architected multi-agent system", "Reduced latency by 45%"],
        },
        {
          id: "work-2",
          name: "Startup Inc",
          position: "Senior ML Engineer",
          startDate: "2019-01-01",
          endDate: "2021-12-31",
          highlights: ["Fine-tuned transformer models"],
        },
      ],
      presentation: {
        section_order: ["basics", "skills", "work", "projects", "education"],
        hidden_sections: ["awards"],
        hidden_items: {
          work: ["work-2"],
        },
      },
    };

    expect(canonicalSnapshot.schema_version).toBe("2.0.0");
    expect(canonicalSnapshot.presentation?.section_order[1]).toBe("skills");
    expect(canonicalSnapshot.presentation?.hidden_sections).toContain("awards");
    expect(canonicalSnapshot.presentation?.hidden_items?.work).toContain("work-2");

    // Filter active items using presentation settings
    const activeWork = (canonicalSnapshot.work || []).filter(
      (item) => !canonicalSnapshot.presentation?.hidden_items?.work?.includes(item.id || "")
    );
    expect(activeWork.length).toBe(1);
    expect(activeWork[0].id).toBe("work-1");
  });

  it("applies reordering and visibility toggles immutably", () => {
    const initialPresentation: CVPresentationSnapshot = {
      section_order: ["basics", "work", "skills", "projects"],
      hidden_sections: [],
      hidden_items: {},
    };

    // Move "skills" up
    const order = [...initialPresentation.section_order];
    const skillsIdx = order.indexOf("skills");
    const [moved] = order.splice(skillsIdx, 1);
    order.splice(skillsIdx - 1, 0, moved);

    expect(order).toEqual(["basics", "skills", "work", "projects"]);

    // Toggle hidden section
    const hiddenSections = new Set(initialPresentation.hidden_sections);
    hiddenSections.add("projects");
    const updatedHidden = Array.from(hiddenSections);
    expect(updatedHidden).toEqual(["projects"]);

    // Toggle hidden item
    const currentHiddenItems = initialPresentation.hidden_items || {};
    const sectionHidden = new Set(currentHiddenItems["work"] || []);
    sectionHidden.add("item-1");
    const updatedHiddenItems = {
      ...currentHiddenItems,
      work: Array.from(sectionHidden),
    };
    expect(updatedHiddenItems.work).toEqual(["item-1"]);
  });
});
