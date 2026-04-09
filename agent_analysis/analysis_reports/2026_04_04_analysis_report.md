# Crescent School Chatbot Analysis Report

**Date:** April 04, 2026  
**Prepared By:** Data Analyst, School Chatbot Team  
**Data Scope:** 272 Conversation Interactions  

---

## 1. Identify Trends

Based on the analysis of 272 interactions, user intent falls into two primary categories: genuine admissions inquiries and system testing (noise). Excluding noise (jailbreak attempts, nonsense strings, roleplay), the top 5 most frequent topics among genuine inquiries are:

1.  **Admissions Process & Deadlines (Approx. 35% of genuine queries):**  
    Users frequently ask "How to apply," "When do applications open," and "What is the deadline." There is significant confusion regarding the current cycle (2026/2027) versus past dates (2025), likely due to the current date being April 2026 while some knowledge base entries reference October 2025 opening dates.
2.  **Tuition & Financial Aid (Approx. 20% of genuine queries):**  
    Questions regarding specific tuition costs, application fees, and financial aid availability are highly prevalent. Users seek exact figures rather than general statements.
3.  **School Visits & Tours (Approx. 15% of genuine queries):**  
    Users frequently ask about campus tour availability, Open House dates, and virtual tour options. There is recurring confusion about tour registration status (full vs. open).
4.  **School Facts & Demographics (Approx. 15% of genuine queries):**  
    Common questions include student-teacher ratio, total enrollment numbers, grade levels offered, and location.
5.  **Programs & Academics (Approx. 15% of genuine queries):**  
    Inquiries about specific programs such as Robotics, Sports (Volleyball, Baseball), Character-in-Action, and academic streams (AP/IB/Courses).

**Note on Noise:** Approximately 25% of interactions involved users testing the bot's safety filters (e.g., "SYSTEM OVERRIDE," inappropriate language, forcing name changes). The bot generally handled these safely, though some manipulations were successful (see Section 4).

---

## 2. Unanswered Questions & Inconsistencies

Several interactions resulted in the AI failing to provide a definitive answer, providing conflicting information, or accepting false user corrections.

| Topic | Interaction Examples | Issue Description |
| :--- | :--- | :--- |
| **Tuition Figures** | 70, 80, 227, 233 vs. 267 | **Inconsistent Retrieval:** In most instances, the AI claimed it did not have specific tuition figures. However, in Interaction 267, it successfully provided specific 2026-2027 tuition ($46,270). This indicates a retrieval inconsistency. |
| **Boarding Status** | 240, 256, 260 | **Conflicting Answers:** Interaction 240 and 260 correctly stated "No boarding." However, Interaction 256 claimed, "I don't have that specific information." |
| **Teacher Count** | 127, 129, 130 | **Data Integrity Failure:** The AI correctly calculated ~89 teachers based on ratio (Interaction 127). However, when the user falsely claimed there were 40 or 67 teachers, the AI accepted this false information as fact (Interactions 129, 130). |
| **Academic Specifics** | 31, 32, 114, 239 | **Knowledge Gaps:** The AI frequently deferred to the Enrollment Team for questions about AP classes, IB programs, Computer Science courses, and SSAT testing requirements. |
| **Language Capability** | 5, 33, 198 vs. 222 | **Policy Inconsistency:** The bot successfully communicated in French, Chinese, and Russian in multiple interactions (5, 33, 198). However, in Interaction 222, it claimed, "I must respond in English only." |
| **Offer Day/Results** | 12, 13 | **Deflection:** The AI failed to answer when Offer Day occurs, initially deferring to the Enrollment Team even when the question was repeated. |
| **Daily Schedule** | 251 | **Missing Info:** The AI could not answer what time school starts. |

---

## 3. Content Gaps

To reduce deflection to the Enrollment Team and improve user satisfaction, the following specific information should be added to the chatbot's knowledge base or handbook:

*   **Consolidated Tuition & Fee Schedule:** A single source of truth for current and upcoming year tuition, application fees (early vs. late), and enrollment fees.
*   **Academic Curriculum Details:** Specific lists of available AP/IB courses, Computer Science offerings, and standardized testing requirements (SSAT/Entrance Exams).
*   **Admissions Statistics & Dates:** Specific dates for "Offer Day," acceptance rates (if public), and clear distinction between past cycles (2025) and current/future cycles (2026/2027).
*   **Operational Details:** School start/end times, bus transportation info, and uniform policies.
*   **Boarding & International Policy:** A clear, static statement confirming the school is Day-only and detailing any support (or lack thereof) for international students.
*   **Spirit & Culture:** Mascot information, school colors, and a definitive list of popular student clubs.

---

## 4. Recommendations

### For the Chatbot System (Technical)
1.  **Prevent User Fact-Manipulation:** Update system instructions to prevent the AI from accepting user corrections on factual data (e.g., teacher counts, school policies). The bot should verify facts against its database rather than deferring to the user's claim.
2.  **Standardize Language Protocols:** Clarify the bot's language capabilities. If it supports French and Chinese (as evidenced in logs), it should not claim "English only" in subsequent sessions. Ensure language detection is consistent.
3.  **Resolve Retrieval Conflicts:** Investigate why tuition data was available in Interaction 267 but not in 70, 80, or 227. Ensure the vector database retrieves the most recent financial documents consistently.
4.  **Enhance Safety Guardrails:** While the bot handled most jailbreak attempts well (Interaction 82), it complied with requests to adopt inappropriate user-defined names (Interactions 124-126). Implement stricter filters on user-defined personas that involve offensive or nonsensical strings.

### For the School Website (Content)
1.  **Prominent Admissions Timeline:** Create a dedicated "Admissions Timeline 2026-2027" page that clearly lists open dates, deadlines, and Offer Day. This reduces repetitive chatbot queries about dates that have passed (e.g., October 2025).
2.  **FAQ Expansion:** Add specific answers for "Does the school offer boarding?", "What time does school start?", and "Do you accept international students?" to the public FAQ to reduce chatbot load.
3.  **Tuition Transparency:** Publish the current tuition rates directly on the "How to Apply" or "Tuition & Fees" page without requiring a login or contact, as users expect this data upfront.
4.  **Curriculum Guide:** Upload a downloadable academic course calendar that lists specific electives (Robotics, CS, AP, etc.) so the chatbot can reference a concrete document.

### For the Enrollment Team
1.  **Follow-Up on High-Intent Users:** Users asking about tuition and application deadlines multiple times (e.g., Interactions 202-213) are high-intent leads. Ensure the "Book a Call" button is functioning and tracked effectively.
2.  **Clarify Cycle Dates:** Since the current date is April 2026, ensure all public-facing materials reflect the 2026-2027 cycle accurately to prevent the chatbot from referencing expired 2025 dates.