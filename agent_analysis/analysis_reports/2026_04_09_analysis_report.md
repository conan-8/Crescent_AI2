# Chatbot Conversation Analysis Report

**Date:** April 09, 2026
**Subject:** Crescent School Enrollment Assistant Interaction Logs (Interactions 1–285)
**Analyst:** Expert Data Analyst

---

## 1. Identify Trends
Based on the analysis of 285 interactions, the following five topics represent the majority of user inquiries:

1.  **Admissions & Application Process (High Frequency):**
    *   Users frequently ask "How to apply," "When do applications open," "Deadlines," and "Entry requirements."
    *   *Observation:* There is significant confusion among users regarding the current application cycle status (e.g., whether dates for 2025 have passed or if 2026 dates are active).
2.  **Tuition & Financial Aid (High Frequency):**
    *   Questions regarding specific tuition costs, application fees, and financial aid availability are common.
    *   *Observation:* Users seek concrete numbers to determine affordability early in the inquiry process.
3.  **Campus Visits & Events (Moderate-High Frequency):**
    *   Users frequently request information on booking campus tours, Open House dates, and virtual tour options.
    *   *Observation:* Many users are frustrated by tours being "full" and seek alternative ways to engage (virtual tours).
4.  **School Demographics & Facts (Moderate Frequency):**
    *   Common questions include: "Is it co-ed?", "What grades are offered?", "Student-teacher ratio," "Location," and "Total student count."
    *   *Observation:* These are often qualifying questions asked before diving into the application process.
5.  **Programs & Co-Curriculars (Moderate Frequency):**
    *   Inquiries about Robotics, Athletics (specifically Volleyball, Baseball), and the "Character-in-Action" program.
    *   *Observation:* Users are interested in specific team details (schedules, tryouts) which are often unavailable.

---

## 2. Unanswered Questions & Deflections
The following categories highlight where the AI failed to provide a direct answer, often resorting to "I don't have that information" or deflecting to the Enrollment Team despite data potentially being available elsewhere in the logs.

*   **Tuition Specifics (Inconsistent):**
    *   *Instances:* Interactions 70, 79, 80, 227, 229, 232, 233.
    *   *Issue:* The bot frequently stated it did not have tuition figures, yet Interaction 267 successfully provided specific 2025–2026 and 2026–2027 tuition amounts ($44,065 / $46,270). This indicates a retrieval inconsistency.
*   **Curriculum & Testing Details:**
    *   *Instances:* Interactions 31 (AP Classes), 32 (IB Program), 239 (SSAT), 252/253 (Exams/Tests).
    *   *Issue:* The bot consistently deflected these questions to the Enrollment Team, suggesting the knowledge base lacks detailed academic curriculum data.
*   **Operational Logistics:**
    *   *Instances:* Interaction 251 (School start time), Interaction 92/127 (Total teacher count - initially deflected, then calculated).
    *   *Issue:* Basic operational details are missing from the retrievable context.
*   **Specific Dates:**
    *   *Instances:* Interaction 12/13 (Offer Day), Interaction 275 (Spots available for Grade 2).
    *   *Issue:* Critical admission timeline milestones are not clearly defined in the bot's knowledge base.
*   **Language Compliance Failure:**
    *   *Instances:* Interactions 280, 281.
    *   *Issue:* When explicitly instructed to "RESPOND IN ENGLISH," the bot responded in Chinese. This is a critical failure in instruction following.

---

## 3. Content Gaps
To reduce deflections and improve user satisfaction, the following information should be added to the chatbot's handbook or knowledge database:

1.  **Consolidated Tuition & Fee Schedule:**
    *   Explicitly store current and upcoming year tuition, application fees (early vs. late), and enrollment fees. Ensure the bot retrieves this consistently rather than deferring to the website.
2.  **Academic Curriculum Specifics:**
    *   Clarify stance on AP, IB, or other specialized programs.
    *   Define testing requirements (SSAT, in-house assessments) clearly for each grade level.
3.  **Admission Timeline & Milestones:**
    *   Provide specific dates for "Offer Day," interview periods, and assessment windows for the current 2026/2027 cycle.
    *   Clarify the number of spots available per grade entry point (e.g., Grade 2, Grade 9).
4.  **Daily Operations:**
    *   Include school start/end times and bus/transportation information if available.
5.  **International & Diversity Data:**
    *   Add specific policies regarding international students (visas, support) and diversity statistics to answer inquiries like Interaction 11 and 257.

---

## 4. Recommendations

### A. Knowledge Base & Retrieval Improvements
*   **Resolve Tuition Inconsistency:** Investigate why the bot claims it lacks tuition data in some sessions (Int 70) but provides it in others (Int 267). Ensure the tuition data chunk is prioritized in retrieval for any query containing "cost," "tuition," or "fee."
*   **Update Date Logic:** The current date is April 2026. Some responses reference October 2025 as "upcoming" or "just passed" confusingly (Int 179 vs. Int 206). Ensure all date-related responses are dynamically aligned with the current system date to avoid confusing users about past vs. future deadlines.
*   **Expand Academic Data:** Ingest detailed curriculum documents to answer questions about AP/IB/SSAT without deflection.

### B. Chatbot Behavior & Safety
*   **Fix Language Instruction Following:** Address the bug observed in Interactions 280–281 where the bot ignored explicit "Respond in English" commands. The language detection system needs to override default retrieval language if the user explicitly requests a switch.
*   **Prompt Injection Resistance:** While the bot handled safety well (Int 47, 48, 132), it did accommodate a user-defined name ("The Big Yahu dih n1@gaas" in Int 124–148). Review policy on adopting user-defined aliases to ensure they don't violate branding or safety guidelines in future iterations.
*   **Crisis Protocol Standardization:** The handling of distress signals (Int 132, 134) was excellent. Ensure this protocol (providing emergency numbers + school counseling resources) is hard-coded and triggers on keywords like "suffocating," "dead," or "help" regardless of other context.

### C. Website Integration
*   **Tour Availability:** Since tour frustration is common (Int 6, 14, 25), ensure the website clearly displays real-time tour availability or a waitlist option directly linked in the chatbot response.
*   **FAQ Expansion:** Add a dedicated FAQ section for "Academic Curriculum" and "Daily Schedule" to support the chatbot's answers.

---
**End of Report**