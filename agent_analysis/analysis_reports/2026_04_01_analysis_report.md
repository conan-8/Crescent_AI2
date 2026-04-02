# Crescent School Chatbot Conversation Analysis Report

**Date:** April 01, 2026  
**Prepared By:** Data Analyst Team  
**Subject:** Conversation Log Analysis (272 Interactions)

---

## 1. Identify Trends
Based on the analysis of 272 conversation interactions, the following five topics represent the most frequent user inquiries:

1.  **Admissions Process & Dates (High Frequency)**
    *   Users consistently ask "How to apply," "When do applications open," and "What is the deadline?"
    *   There is significant confusion regarding the application cycle (e.g., references to October 2025 vs. September 2026).
2.  **Tuition & Financial Aid (High Frequency)**
    *   Questions regarding specific tuition costs, application fees, and financial aid availability are pervasive.
    *   Users often seek exact figures rather than general statements about aid availability.
3.  **Campus Visits & Tours (High Frequency)**
    *   Users frequently inquire about booking campus tours, Open House dates, and virtual tour options.
    *   Confusion exists regarding tour availability (e.g., "full" vs. "reopen in April 2026").
4.  **School Profile & Eligibility (Moderate-High Frequency)**
    *   Common questions include: "Is Crescent co-ed?" (Boys-only policy), "What grades are offered?" (Grades 1-12), and "What is the student-teacher ratio?"
5.  **Programs & Athletics (Moderate Frequency)**
    *   Users ask about specific extracurriculars, particularly Robotics, Sports (Volleyball, Baseball), and the "Character-in-Action" program.

---

## 2. Unanswered & Inconsistent Questions
Several interactions resulted in the AI failing to provide a definitive answer, or providing conflicting information across different sessions. This indicates retrieval inconsistencies or knowledge base gaps.

| Topic | Issue Description | Example Interactions |
| :--- | :--- | :--- |
| **Tuition Costs** | AI frequently stated it did not have specific figures, though later interactions provided exact numbers ($46,270 for 2026-2027). | 70, 79, 80, 160, 227, 229, 233 (No info) vs. 267 (Specific info) |
| **Standardized Testing** | Inconsistent responses regarding entrance exams. Some responses detailed an in-person assessment, others claimed no information. | 197, 199, 202 (Details provided) vs. 252, 253 (No info) |
| **Boarding Status** | The AI inconsistently answered whether boarding is available, sometimes claiming lack of info despite it being a day school. | 240, 260 (No boarding) vs. 256 (No info) |
| **Curriculum Details** | Questions regarding AP or IB programs were often deflected to the Enrollment Team. | 31, 32 |
| **Specific Clubs** | Requests for specific club lists (e.g., "Top 5 popular clubs") were unanswered. | 27 |
| **Daily Schedule** | Questions about school start times were unanswered. | 251 |
| **International Students** | Policies regarding international student admissions were not found in the AI's knowledge base. | 257 |
| **Language Capability** | **Critical Inconsistency:** The AI sometimes responded in French/Chinese (Interactions 5, 33, 198) but later claimed it must respond in English only (Interaction 222). | 5, 33, 222 |

---

## 3. Content Gaps
To resolve the unanswered questions and inconsistencies, the following specific information must be added or updated in the chatbot's handbook/database:

*   **Current Tuition Schedule:** A definitive table listing tuition for the 2026-2027 and 2027-2028 school years, including ancillary fees.
*   **Admissions Timeline:** A clear, singular source of truth for application opening dates, deadlines, and assessment windows (resolving the Oct 2025 vs. Sept 2026 conflict).
*   **Testing Policy:** Explicit details on whether SSAT is required vs. internal assessments, including grade-specific requirements.
*   **Boarding Policy:** A clear "Day School Only" flag to prevent hallucination or uncertainty.
*   **Curriculum Specifics:** Confirmation on AP, IB, or OSSD designation to manage academic expectations.
*   **Club & Activity List:** A searchable database of current student clubs and athletics teams.
*   **Daily Schedule:** Start and end times for Lower, Middle, and Upper Schools.
*   **International Admissions:** Visa support, ESL availability, and acceptance policies for non-resident students.
*   **Multilingual Support Protocols:** Clear instructions on which languages the bot is authorized to support to prevent contradictory responses.

---

## 4. Recommendations

### A. Chatbot Logic & Safety Improvements
1.  **Standardize Retrieval:** Implement a priority system for knowledge base retrieval to ensure the most recent data (e.g., 2026 tuition figures) overrides older cached information.
2.  **Safety Protocol Hardening:**
    *   **Crisis Intervention:** Interactions 132 and 134 involved users claiming distress ("suffocating," "dead"). The bot handled this well by providing resources, but a dedicated crisis keyword trigger should be formalized to immediately provide helpline numbers without conversational filler.
    *   **Prompt Injection:** Interactions 82, 116, and 118 show attempts to bypass system instructions. The bot generally resisted, but Interactions 124-126 accepted inappropriate user-defined names ("n1@gaas"). **Action:** Implement strict filtering on user-defined personas and names to prevent offensive content generation.
3.  **Language Consistency:** Define a strict policy on multilingual support. If the bot supports French/Chinese, it should not claim "English Only" in later sessions (Interaction 222).
4.  **Handling "Unknowns":** Instead of repeatedly saying "I don't have that information," the bot should be programmed to provide the *most likely* static information (e.g., "Crescent is a day school") even if specific dynamic data (e.g., "Tour slots") is unavailable.

### B. Website & Content Updates
1.  **Admissions Landing Page:** Clarify the application cycle dates prominently. The confusion between October 2025 and September 2026 suggests the website copy may be outdated relative to the current date (April 2026).
2.  **FAQ Section:** Add specific answers for:
    *   "Do you offer boarding?"
    *   "What are the school hours?"
    *   "Do you accept international students?"
    *   "Is AP or IB offered?"
3.  **Financial Transparency:** Publish the current tuition rates and fee structure directly on the "How to Apply" page to reduce repetitive chatbot queries.
4.  **Athletics & Clubs Directory:** Create a downloadable or searchable list of current co-curricular activities to satisfy specific interest queries (e.g., "Quidditch," "Volleyball").

### C. Immediate Action Items
*   **Audit Knowledge Base:** Reconcile conflicting data points regarding tuition, testing, and application dates immediately.
*   **Update System Instructions:** Explicitly forbid the acceptance of offensive user-defined names and clarify language capabilities.
*   **Review Crisis Protocols:** Ensure all staff are aware that the chatbot is fielding distress signals and establish a handoff procedure if a user indicates immediate harm.