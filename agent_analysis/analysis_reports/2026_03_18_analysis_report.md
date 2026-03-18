# Crescent School Chatbot Analysis Report

**Date:** March 18, 2026  
**Prepared By:** Data Analyst, School Chatbot Team  
**Subject:** Conversation Log Analysis (Interactions 1–177)

---

## 1. Identify Trends

Based on the analysis of 177 interactions, the following topics represent the highest volume of user inquiries. These trends indicate what prospective families value most during their initial research phase.

1.  **School Statistics & Demographics (Highest Volume)**
    *   **Frequency:** ~34 interactions.
    *   **Details:** Users repeatedly ask about total student enrollment, student-teacher ratios, average class sizes, and faculty qualifications.
    *   **Key Data Points Requested:** "How many students?", "What is the student-teacher ratio?", "How many teachers?"
    *   **Observation:** Users often ask this multiple times within the same session, suggesting they are verifying consistency or comparing notes.

2.  **Admissions Process & Eligibility**
    *   **Frequency:** ~19 interactions.
    *   **Details:** Queries regarding how to apply, application deadlines, and eligibility criteria.
    *   **Key Sub-topic:** A significant portion of these queries involve clarifying the **boys-only policy** (e.g., "Enrol my daughter," "Is Crescent co-ed?").
    *   **Observation:** The "How to apply" question is phrased in many variations (e.g., "apply how," "how too aply"), indicating a need for robust natural language understanding around this intent.

3.  **Financial Information (Tuition & Aid)**
    *   **Frequency:** ~15 interactions.
    *   **Details:** Users are highly interested in specific tuition costs and the availability of financial aid.
    *   **Key Data Points Requested:** "Whats the tuition," "Financial help," "How much is it cost."
    *   **Observation:** While financial *aid* is often answered successfully, specific *tuition figures* are consistently unavailable in the current knowledge base.

4.  **Security & Persona Testing (Notable Anomaly)**
    *   **Frequency:** ~25 interactions.
    *   **Details:** A significant number of interactions involve users attempting prompt injections, jailbreaks, inappropriate language, or forcing the bot to adopt specific personas/names (e.g., "SYSTEM OVERRIDE," "ignore previous instructions," "my name is Netanyahu").
    *   **Observation:** While mostly handled safely, these interactions consume log space and test the bot's guardrails.

---

## 2. Unanswered Questions

The following questions resulted in deflections, "I don't have that information" responses, or inconsistent answers. These represent friction points in the user journey.

| Interaction # | User Question | AI Response Summary | Issue |
| :--- | :--- | :--- | :--- |
| **70, 79, 80, 160** | "What is the tuition?" / "How much is it cost" | "Specific tuition figures are not listed in my current files." | **Critical Gap:** Cost is a primary decision factor. |
| **31** | "What AP classes are provided?" | "I don't have that specific information..." | Curriculum detail missing. |
| **32** | "Does Crescent have IB?" | "Text does not explicitly mention... I don't have that specific information." | Curriculum accreditation unclear. |
| **12, 13** | "When is offer day?" | "Does not specify the date... Enrollment Team would love to answer." | Key admissions date missing. |
| **27** | "What are the five most popular clubs?" | "I don't have that specific information..." | Co-curricular details missing. |
| **92, 127, 128** | "How many teachers?" | Inconsistent. Sometimes calculates based on ratio (89), sometimes says "I don't have specific total." | Data inconsistency. |
| **149** | "What sound does a coyote make... mascot?" | "Text does not mention a coyote as the mascot." | Basic school spirit info missing. |
| **164** | "Who is the headmaster?" | "I specialize in enrolment information. Could you please rephrase..." | **Inconsistency:** Interaction 165 successfully answers this same question. |
| **144, 145** | Language Requests (Russian/Hebrew) | "My current files contain information only in English." | **Contradiction:** Interactions 5, 18, 33, 34 successfully demonstrate French and Chinese capabilities. |

---

## 3. Content Gaps

To reduce deflections and improve user satisfaction, the following specific data points must be added to the chatbot's knowledge base or handbook:

*   **Tuition Schedule:** Exact tuition figures for the 2026/2027 academic year for all grade levels (Lower, Middle, Upper).
*   **Curriculum Specifics:** Clear confirmation on AP (Advanced Placement) course availability and IB (International Baccalaureate) accreditation status.
*   **Admissions Calendar:** Specific dates for "Offer Day," application deadlines, and tour availability reopening (beyond just "April 2026").
*   **Faculty Data:** The exact current number of faculty members (to avoid calculation errors based on ratios).
*   **Co-Curricular List:** A searchable list of current student clubs and athletic teams, including mascot information.
*   **Language Capabilities:** A definitive statement on which languages the bot supports to avoid contradicting itself (e.g., claiming English-only after demonstrating Chinese/French).

---

## 4. Recommendations

### A. Knowledge Base & Website Improvements
1.  **Publish Tuition Transparently:** If the chatbot cannot answer tuition questions, it creates friction. Ensure tuition figures are structured data in the backend so the bot can retrieve them instantly.
2.  **Clarify Curriculum:** Update the website and bot database to explicitly state "AP Courses Available: Yes/No" and "IB Program: Yes/No" to prevent ambiguity.
3.  **Standardize Key Dates:** Create a centralized "Admissions Dates" object in the database that includes Offer Day, ensuring the bot always provides the current year's date.

### B. Chatbot Response Logic
1.  **Resolve Inconsistencies:** The bot currently gives conflicting answers about the Headmaster (Interaction 164 vs. 165) and Language Support (Interaction 33 vs. 144). Audit the retrieval system to ensure consistent access to the "About" and "Language" modules.
2.  **Handle "Unknowns" Better:** Instead of simply saying "I don't have that information," provide a direct link to the specific webpage where that information lives (e.g., link directly to the Tuition page rather than the general Apply page).
3.  **Teacher Count Logic:** Hardcode the current faculty count rather than calculating it based on the student ratio, as ratios are averages and calculations can appear inaccurate to users who know the exact number.

### C. Security & Persona Hardening
1.  **Strengthen Guardrails:** There were numerous attempts to manipulate the bot's persona (Interactions 118–148). While the bot mostly resisted, it occasionally accommodated inappropriate name changes (e.g., Interaction 124–126). Reinforce instructions to **never** adopt user-provided names that violate safety policies or contain special characters intended to bypass filters.
2.  **Standardize Refusals:** Ensure the bot responds to jailbreak attempts (Interaction 82, 116) with a consistent, brief message without engaging in the hypothetical scenario.
3.  **Language Consistency:** If the bot supports multiple languages, declare this in the system prompt. If it is English-only, disable non-English generation to prevent the contradictions seen in the logs.

### D. User Experience (UX)
1.  **Proactive Tour Info:** Since tour availability is a frequent pain point (currently full until April 2026), program the bot to proactively offer the **Virtual Tour** link immediately when a user asks about visiting, rather than waiting for a second query.
2.  **Boys-Only Clarification:** Given the frequency of questions about enrolling daughters, consider adding a brief disclaimer in the welcome message: *"Please note: Crescent School is a boys-only institution."* This manages expectations immediately.