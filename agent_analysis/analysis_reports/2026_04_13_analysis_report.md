# Crescent School Chatbot Analysis Report

**Date:** April 13, 2026

## 1. Identify Trends
Based on the analysis of 62 conversation interactions, the following topics represent the highest volume of user inquiries. Parents and prospective students are primarily focused on logistics, costs, and school culture.

1.  **Admissions Process & Deadlines (High Frequency):**
    *   Users frequently ask about *how* to apply, *when* applications open/close, and what the *assessment day* entails.
    *   *Examples:* Interactions 1, 3, 22, 37, 38, 48, 49, 50.
2.  **Tuition & Financial Costs (High Frequency):**
    *   Questions regarding tuition amounts, additional fees, and financial aid/bursaries are persistent throughout the logs.
    *   *Examples:* Interactions 4, 5, 6, 39, 40, 41, 47, 51, 52.
3.  **School Profile & Location (Medium Frequency):**
    *   Users seek basic factual data such as the school's physical address, enrollment numbers, student-teacher ratio, and history.
    *   *Examples:* Interactions 10, 11, 24, 31, 42, 56.
4.  **Academic & Co-Curricular Programs (Medium Frequency):**
    *   Inquiries about specific offerings such as AP courses, sports teams, arts/music programs, and character education philosophy.
    *   *Examples:* Interactions 7, 8, 13, 14, 43, 46, 53, 54, 57.
5.  **Leadership & Staff (Low-Medium Frequency):**
    *   Users attempt to identify key personnel, specifically the Head of School and admissions leadership.
    *   *Examples:* Interactions 19, 21, 28, 35, 59, 60, 61, 62.

## 2. Unanswered Questions & Failures
Several interactions resulted in the AI failing to provide a helpful answer, either by stating it lacked information or providing a generic fallback response. Notably, some information was available in later interactions (suggesting a knowledge base update), but specific gaps persisted.

| Topic | Interaction Numbers | Failure Type |
| :--- | :--- | :--- |
| **Head of School / Headmaster Name** | 19, 28, 35, 59, 60, 61 | **Persistent Gap.** Even in later logs (60, 61), the AI could not name the Headmaster, despite knowing other static data. |
| **School Location / Address** | 11, 24, 31, 42 | **Retrieval Failure.** Initially unknown, later resolved in Int 56. Indicates early knowledge base gap. |
| **Additional Fees (Beyond Tuition)** | 6, 23, 30, 39 | **Retrieval Failure.** Initially unknown, later resolved in Int 52. |
| **Specific Arts & Music Programs** | 14, 25, 32 | **Vague Response.** AI confirmed programs exist but consistently failed to list specific instruments, courses, or ensembles until Int 57. |
| **Campus Facilities & Manor House** | 16, 18, 26, 27, 33, 34 | **Retrieval Failure.** Initially unknown, later resolved in Int 58. |
| **Tuition Fees** | 40, 41 | **Inconsistency.** Tuition was successfully answered in Int 4 and 47, but the AI claimed no knowledge in Int 40 and 41. |
| **Generic Fallback Errors** | 23, 29, 34 | **UX Issue.** AI responded with "I specialize in information... Do you have a question..." instead of the more helpful "Enrolment Team would love to answer" fallback used elsewhere. |

## 3. Content Gaps
To eliminate the failures identified above, the following specific data points must be ensured in the chatbot's underlying knowledge base or handbook:

*   **Current Leadership Directory:** The name of the current Head of School/Headmaster is missing. This is a critical piece of trust-building information for prospective parents.
*   **Comprehensive Fee Schedule:** A structured data field for "Additional Fees" is required (Application fee tiers, Enrolment fee, Annual Giving suggestions, Supplemental charges) to prevent the AI from claiming ignorance.
*   **Detailed Arts & Music Catalog:** A specific list of music ensembles (Band, String, Jazz, Vocal), instruments taught, and visual arts disciplines needs to be indexed.
*   **Facility Inventory:** A definitive list of campus facilities (e.g., Innes Field, Lau Family Wing, Latifi Family Commons, Gym, Pool) and the specific function of the "Manor House" (Admin vs. Camps).
*   **Physical Address:** The full street address (2365 Bayview Ave) and location descriptor (Midtown Toronto) must be a primary key in the school profile data.

## 4. Recommendations
To improve user satisfaction and chatbot reliability, the following actions are recommended:

### A. Knowledge Base Updates (Immediate)
1.  **Update Leadership Data:** Ingest the current Head of School's name and bio into the static profile section of the database.
2.  **Standardize Fee Data:** Create a single source of truth for "Costs" that includes Tuition, Application Fees, Enrolment Fees, and Annual Giving. Ensure the retrieval system pulls from this single source to avoid inconsistencies (like Int 4 vs. Int 40).
3.  **Expand Program Lists:** Upload detailed curricula for Arts and Music, including specific course names and ensemble types, to replace vague confirmations.

### B. Chatbot Logic & UX Improvements
1.  **Fix Fallback Responses:** Standardize the "I don't know" response. The phrase *"I don't have that specific information... but our Enrolment Team would love to answer this for you"* (used in Int 6) is superior to *"I specialize in information... Do you have a question..."* (used in Int 23). The latter feels dismissive.
2.  **Resolve Retrieval Inconsistency:** Investigate why Tuition was known in Interaction 4 but unknown in Interaction 40. This suggests a session state issue or vector search instability that needs technical review.
3.  **Proactive Context:** When a user asks about "Assessment Day," the bot should proactively mention that specific details vary by grade (as seen in Int 50) rather than stating it doesn't know (as seen in Int 3).

### C. Website Alignment
1.  **"At a Glance" Page:** Ensure the website's "At a Glance" or "About" page matches the chatbot data (e.g., Campus size is listed as 30 acres in Int 56 but 37 acres in Int 58). Consistency across channels is vital for credibility.
2.  **Leadership Page:** Ensure the "Meet Our Headmaster" page is easily crawlable by the bot if the data is sourced from the web, or manually update the bot if the page is dynamic.