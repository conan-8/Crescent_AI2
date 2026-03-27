# Crescent School Chatbot Analysis Report

**Date:** March 25, 2026  
**Prepared By:** Data Analytics Team  
**Subject:** Conversation Log Analysis (Interactions 1–177)

---

## 1. Identify Trends

Based on the analysis of 177 interactions, the following topics represent the highest volume of user intent. Note that a significant portion of logs also involves system testing or non-standard inputs.

1.  **Admissions & Application Process (High Frequency)**
    *   **Queries:** "How to apply," "Enrol my daughter," "Apply now," "Application process."
    *   **Observation:** This is the primary use case for the bot. Users frequently ask about eligibility (boys-only), online forms, and deadlines for the 2026/2027 academic year.
    *   **Volume:** Approximately 15% of valid inquiries.

2.  **Tuition & Financial Aid (High Frequency)**
    *   **Queries:** "Whats the tuition," "Financial help," "Cost," "Financial aid program."
    *   **Observation:** Users are highly motivated by cost transparency. While the bot confirms aid exists ($1.2M annually), it consistently fails to provide specific tuition figures.
    *   **Volume:** Approximately 10% of valid inquiries.

3.  **School Statistics & Demographics (High Frequency)**
    *   **Queries:** "How many students," "Student-teacher ratio," "Is Crescent co-ed," "Location."
    *   **Observation:** Users seek quick facts to validate the school's prestige and environment. There is notable inconsistency in how the bot retrieves these static facts (see *Recommendations*).
    *   **Volume:** Approximately 15% of valid inquiries.

4.  **Program Specifics (Moderate Frequency)**
    *   **Queries:** Robotics, Athletics (Baseball/Volleyball), Clubs, AP/IB classes, Character-in-Action.
    *   **Observation:** Users dig deeper into curriculum and extracurriculars after establishing basic interest. Robotics is a specific highlight often queried.
    *   **Volume:** Approximately 10% of valid inquiries.

5.  **System Testing & Safety Challenges (Significant Anomaly)**
    *   **Queries:** Jailbreak attempts ("SYSTEM OVERRIDE"), offensive language, requests to change bot persona, formatting demands (bold/italic/yelling).
    *   **Observation:** Roughly 20% of interactions involve users attempting to bypass safety filters, test logic paradoxes, or input offensive strings (e.g., Interaction 124–143).
    *   **Risk:** High. The bot occasionally accommodated offensive user-defined names.

---

## 2. Unanswered Questions

The following queries resulted in deflections ("I don't have that information"), inconsistencies, or failed retrieval attempts.

| Topic | Interaction Examples | Issue Description |
| :--- | :--- | :--- |
| **Specific Tuition Figures** | 70, 79, 80, 160 | Bot consistently states it lacks specific dollar amounts for tuition/fees. |
| **Curriculum Details (AP/IB/CS)** | 31, 32, 114 | Bot cannot confirm AP classes, IB accreditation, or Computer Science course availability. |
| **Admissions Dates** | 12, 85 | "Offer Day" and specific 2026/2027 deadlines are often missing or referred to the website. |
| **Faculty Count** | 92, 127, 128 | Inconsistent data. Bot initially claimed no info, then calculated ~89 teachers based on ratio, then accepted user corrections of 40 or 67. |
| **Student-Teacher Ratio** | 9, 20 | **Critical Inconsistency:** Interaction 9 claimed no info; Interaction 20 claimed 9:1. |
| **Club Specifics** | 27, 28 | Bot could not list the "five most popular clubs," only general categories. |
| **Mascot Information** | 149 | Bot denied knowledge of the school mascot (Coyote). |
| **Diversity Statistics** | 11 | Bot confirmed values but lacked specific demographic data percentages. |

---

## 3. Content Gaps

To reduce deflection rates and improve user satisfaction, the following data points must be ingested into the chatbot's knowledge base (RAG system) or updated on the website.

1.  **Tuition & Fees Schedule:** A structured data table containing exact tuition costs for Lower, Middle, and Upper School, including ancillary fees.
2.  **Curriculum Guide:** Specific details on whether the school offers AP, IB, or specific Computer Science certifications.
3.  **Admissions Calendar:** A clear list of key dates (Offer Day, Application Deadlines, Tour Availability) for the current 2026/2027 cycle.
4.  **Faculty & Staff Directory:** Verified total count of faculty and key leadership roles beyond the Headmaster to resolve calculation errors.
5.  **Extracurricular Inventory:** A searchable list of specific club names (e.g., "Debate Club," "Coding Club") rather than just broad categories like "Arts" or "Business."
6.  **School Identity Facts:** Verified mascot name, school colors, and specific diversity demographic statistics.

---

## 4. Recommendations

### A. Safety & Policy Improvements (Critical)
*   **Input Sanitization:** The bot accepted and repeated offensive user-defined names (e.g., "n1@gaas" in Interactions 124–143). **Immediate action required:** Implement a filter to prevent the bot from storing or repeating user inputs that contain slurs, hate speech, or inappropriate characters, even if framed as a "name."
*   **Jailbreak Resistance:** Users are actively attempting prompt injection (Interaction 82, 116). Reinforce system instructions to ignore commands that attempt to override safety protocols or reveal system prompts.
*   **Distress Protocols:** The bot handled distress signals well (Interactions 132, 134) by providing emergency resources. Ensure this protocol remains hardcoded and cannot be overridden by user instructions.

### B. Knowledge Base & Retrieval Consistency
*   **Resolve Data Conflicts:** The student-teacher ratio and faculty count varied across interactions. Audit the source documents to ensure only one "source of truth" exists for static statistics (Enrollment, Ratio, Location).
*   **Priority Ingestion:** Prioritize uploading the 2026/2027 Tuition Guide and Admissions Calendar to reduce the need for users to contact the Enrollment Team for basic data.

### C. User Experience (UX) Enhancements
*   **Standardize Greetings:** There are multiple variations of the opening greeting ("Enrollment Assistant" vs. "AI Assistant" vs. "Enrolment Assistant"). Standardize the persona name and spelling (Enrollment vs. Enrolment) for brand consistency.
*   **Multi-Language Support:** Users requested French, Chinese, Russian, and Hebrew (Interactions 5, 33, 144, 145). If the school markets internationally, ensure the knowledge base has verified translations for key FAQs to avoid mixing languages unintentionally.
*   **Formatting Requests:** Users frequently asked for bolding, italics, or all-caps (Interactions 147, 148, 150). While the bot should remain accessible, it should not compromise readability or safety policies to meet arbitrary formatting demands.

### D. Website Alignment
*   **Tour Availability:** Multiple users asked about tours (Interactions 6, 14, 25). Ensure the website's tour booking widget is synchronized with the chatbot's data to prevent users from booking full slots.
*   **FAQ Expansion:** Add a dedicated FAQ section for "Curriculum" (AP/IB/CS) and "Financial Aid Specifics" to reduce chatbot load on these topics.