# Crescent School Chatbot Analysis Report

**Date:** February 22, 2026

## 1. Identify Trends
Based on the analysis of 89 conversation interactions, the following topics represent the most frequent user inquiries:

1.  **Application Process & Deadlines (High Frequency):**
    *   Approximately 28% of interactions involve questions about how to apply, specific grade requirements (Grades 1, 2, 9, 10, 11), and application deadlines.
    *   Users frequently seek clarification on late fees ($325) and document requirements (report cards, assessments).
2.  **Financial Information (High Frequency):**
    *   Approximately 15% of interactions relate to tuition costs, financial aid eligibility, deadlines for assistance (FAST Aid), and additional enrollment fees.
3.  **General School Information & Culture (Moderate Frequency / High Failure Rate):**
    *   Approximately 17% of interactions ask about school values, student-teacher ratios, diversity, uniform policies, and location.
    *   *Note:* This category has the highest rate of unsuccessful responses (see Section 2).
4.  **Greetings & Bot Identity (High Frequency):**
    *   Approximately 22% of interactions are simple greetings ("Hello") or questions about the bot's identity. This suggests users may be testing the bot or initiating sessions without immediate intent.
5.  **Events & Visits (Moderate Frequency):**
    *   Users frequently ask about Open Houses, tours, and information sessions. Many of these queries relate to past events (2025 Open Houses), indicating a need for better dynamic date handling.

## 2. Unanswered Questions
The following questions resulted in the AI failing to provide a helpful answer, either by stating it lacked information, deflection, or providing contradictory information:

*   **School Culture & Values:** "What kind of boys does crescent look for," "What's the core value of crescent," "Why should I apply."
*   **Academic Metrics:** "What is the teacher to student ratio."
*   **Location:** "Where is Crescent?", "Where is Crescent School located?"
*   **Admissions Outcomes:** "When do we find out whether our son is accepted," "When is Offer Day?" (Bot distinguishes interview selection but lacks offer dates).
*   **Policy Clarifications:** "Is Crescent co-ed?" (Bot claimed no info), "What is the rule on uniforms," "How diverse is Crescent's student body?"
*   **Language Capabilities:** "Parlez vous Francaise?" (Bot claimed no info, despite successfully conversing in French in Interaction 23).
*   **Specific Staff Roles:** "Who's the head of middle school."

## 3. Content Gaps
Based on the unanswered questions and inconsistencies observed, the following information is missing or inconsistent within the chatbot's knowledge base/handbook:

*   **Critical Contradiction (Gender Policy):**
    *   *Gap:* Interaction 44 states "Crescent School is a boys' school," yet Interaction 75 claims no information on whether it is co-ed, and Interaction 76 provides enrollment steps for a "daughter."
    *   *Requirement:* Clear, unified data regarding gender admission policies must be established to prevent misleading parents.
*   **General School Profile:**
    *   *Gap:* Missing data on school location/address, core values/mission, student-teacher ratio, diversity statistics, and uniform policies.
    *   *Requirement:* A "School Profile" section needs to be ingested into the vector database.
*   **Admissions Timeline Clarity:**
    *   *Gap:* The bot knows *interview* notification dates (Jan 19, 2026) but lacks *acceptance/offer* notification dates ("Offer Day").
    *   *Requirement:* Specific dates for acceptance notifications need to be added.
*   **Bot Capabilities:**
    *   *Gap:* The bot successfully spoke French in Interaction 23 but denied language capabilities in Interactions 79 and 80.
    *   *Requirement:* System instructions regarding language support need to be aligned with the knowledge base responses.
*   **Dynamic Event Data:**
    *   *Gap:* Users are asking about 2025 Open Houses in early 2026. The bot confirms they are concluded but does not proactively offer 2026 dates.
    *   *Requirement:* Future event schedules need to be available to redirect interest to upcoming opportunities.

## 4. Recommendations
To improve user satisfaction and data integrity, the following actions are recommended:

### For the School Administration (Website/Handbook Updates)
1.  **Resolve Gender Policy Data:** Immediately audit all source documents. If Crescent is a boys' school, the system must explicitly decline enrollment inquiries for daughters politely and accurately (correcting Interaction 76).
2.  **Expand "About Us" Content:** Upload documents containing the school's mission, values, location, academic statistics (ratio), and uniform policies to the knowledge base.
3.  **Clarify Admissions Timeline:** Publish and upload specific dates for "Offer Day" and acceptance notifications, distinct from interview selection dates.
4.  **Update Event Calendars:** Ensure the website and connected data sources reflect the 2026–2027 event schedule, not just 2025 concluded events.

### For the Chatbot Development Team
1.  **Fix System Instruction Conflicts:** Align the system prompt regarding language capabilities. If the bot is configured to speak French, it should not claim "no information" when asked about language skills.
2.  **Implement Guardrails for Eligibility:** Create a rule that checks for gender-specific keywords (e.g., "daughter," "girl") against the school's admission policy before providing application steps.
3.  **Reduce Repetitive Greeting Responses:** Implement session management so that repeated "Hello" messages within a short timeframe do not generate identical full introductions, or provide a menu of options after the first greeting.
4.  **Improve Retrieval Failure Handling:** Instead of saying "document retrieval failed" (Interaction 33) or "I don't have access" (Interaction 55), provide a fallback response with a link to the admissions office contact information.
5.  **Standardize Fee Information:** There are slight variations in how application fees are presented (some sources mention tiered fees $225/$275/$325, others only mention the $325 late fee). Consolidate this into a single source of truth to ensure consistency.