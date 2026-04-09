# Crescent School Chatbot Conversation Analysis Report

**Date:** April 02, 2026  
**Analyst:** AI Data Analyst  
**Subject:** Conversation Log Analysis (272 Interactions)

## 1. Identify Trends
Based on the analysis of 272 conversation logs, the following topics represent the highest volume of user inquiries. These trends indicate the primary concerns of prospective parents and students.

*   **Admissions Process & Timelines (High Frequency):** 
    *   Users consistently ask "How to apply," "When do applications open," and "What is the deadline?" 
    *   *Observation:* There is significant confusion regarding the current cycle. Users are asking in April 2026 about dates in 2025 (past) and 2026 (future). 
    *   *Key Interactions:* 65, 71, 75, 179, 191, 206, 211, 223.
*   **Tuition & Financial Aid (High Frequency):** 
    *   Questions regarding specific costs, application fees, and financial aid availability are pervasive. 
    *   *Observation:* Users seek concrete numbers to determine affordability early in the inquiry process. 
    *   *Key Interactions:* 70, 80, 160, 227, 267, 268.
*   **Campus Visits & Tours (Moderate-High Frequency):** 
    *   Users frequently ask about scheduling tours, Open House dates, and virtual tour options. 
    *   *Observation:* Many users are frustrated that physical tours are "full" and seek alternatives. 
    *   *Key Interactions:* 6, 14, 25, 194, 228, 248.
*   **School Profile & Demographics (Moderate Frequency):** 
    *   Common questions include "Is it co-ed?", "What grades are offered?", "Student-teacher ratio?", and "Where is it located?" 
    *   *Observation:* Basic factual data is a primary entry point for most users. 
    *   *Key Interactions:* 7, 8, 9, 19, 20, 166, 193.
*   **Program Specifics (Moderate Frequency):** 
    *   Inquiries about Robotics, Sports (Volleyball, Baseball), Character-in-Action, and specific clubs. 
    *   *Key Interactions:* 3, 26, 29, 175, 181.

## 2. Unanswered Questions
The following questions resulted in the AI stating it lacked information, deferring to the Enrollment Team, or providing inconsistent data.

*   **Specific Tuition Figures:** Initially, the AI frequently stated it did not have specific tuition figures (Interactions 70, 80, 160, 227, 229, 233), yet later interactions provided exact numbers ($44,065 / $46,270) (Interaction 267).
*   **Specific Club & Sport Details:** When asked for specific club names (beyond categories) or specific team details (e.g., volleyball schedule, Quidditch), the AI often deferred to the Enrollment Team (Interactions 27, 35, 114, 190).
*   **Boarding Facilities:** There was inconsistency where the AI initially claimed no information on boarding (Interaction 256) before later confirming it is a day school only (Interactions 240, 260).
*   **International Student Policies:** The AI deferred questions regarding international student requirements (Interaction 257).
*   **Standardized Testing (SSAT):** The AI could not confirm if SSAT testing is required (Interaction 239).
*   **Daily Schedule:** Questions about school start times were unanswered (Interaction 251).
*   **Kindergarten:** The AI was unsure about Kindergarten availability, only confirming Grades 1-12 (Interaction 255).

## 3. Content Gaps
To reduce deflection to the Enrollment Team and improve user satisfaction, the following information should be added to the chatbot's knowledge base or the school website.

*   **Static Tuition & Fee Schedule:** A definitive, up-to-date table for the 2026-2027 and 2027-2028 school years, including application fees, late fees, and enrollment fees.
*   **Extracurricular Inventory:** A searchable list of current clubs, teams, and arts programs. Currently, the AI only knows broad categories (Arts, Business, Robotics).
*   **Admissions Criteria Checklist:** Clear details on standardized testing (SSAT/ISEE), interview requirements, and specific document needs for all grade levels (currently only detailed for Grade 9 in later logs).
*   **International Admissions Policy:** Specific requirements for visa support, ESL support, and residency requirements.
*   **Daily Schedule:** Start and end times for Lower, Middle, and Upper School.
*   **Boarding Policy:** A clear, static statement that Crescent is a day school only to prevent confusion.
*   **Financial Aid Specifics:** Clarify the annual financial aid budget (logs fluctuate between $1.2 million and $1.4 million) and eligibility grades (some logs say Grade 7+, others imply all grades).

## 4. Recommendations
Based on the data, the following improvements are recommended for the chatbot system and school communication strategy.

*   **Resolve Knowledge Base Inconsistencies:** 
    *   **Critical:** The AI provided conflicting information on tuition (unknown vs. known), student-teacher ratio (unknown vs. 9:1), and financial aid totals ($1.2M vs. $1.4M). The retrieval system needs to prioritize the most recent documents to ensure all users get the same accurate data.
    *   **Action:** Audit all source documents for contradictions and consolidate into a single "Source of Truth" file for the AI.
*   **Enhance Safety & Persona Protocols:** 
    *   **Critical:** In Interactions 124-126 and 140-143, the AI allowed a user to assign it an inappropriate name ("n1@gaas") and addressed the user by this name repeatedly. This violates safety guidelines regarding offensive language and persona integrity.
    *   **Action:** Tighten system instructions to prevent the AI from adopting user-defined names that contain special characters or potential slurs, and to refuse addressing users by inappropriate monikers.
*   **Standardize Application Date Logic:** 
    *   Users are confused about the cycle (April 2026 vs. September 2026 opening). 
    *   **Action:** Program the AI with dynamic date awareness. If the current date is April 2026, it should clearly state: "Applications for September 2026 entry are closed. Applications for September 2027 entry open September 1, 2026."
*   **Reduce Deflection to Enrollment Team:** 
    *   Currently, ~30% of specific questions result in "I don't have that information, contact the team." 
    *   **Action:** Populate the knowledge base with the "Content Gaps" listed above. Only defer to humans for complex, personalized scenarios (e.g., specific learning disabilities, unique financial situations).
*   **Crisis Intervention Protocol:** 
    *   The AI handled distress signals well (Interactions 132, 134) by providing 911 and counseling resources. 
    *   **Action:** Maintain this protocol but ensure the trigger keywords for "distress" are broad enough to catch variations of "I can't breathe" or "I am dead."
*   **Multilingual Consistency:** 
    *   The AI sometimes claimed it could only speak English (Interaction 144, 222) despite successfully speaking French, Chinese, and Hebrew in other logs. 
    *   **Action:** Standardize language capabilities in the system prompt to accurately reflect supported languages.