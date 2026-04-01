# Crescent School Chatbot Analysis Report

**Date:** April 01, 2026

## 1. Identify Trends
Based on an analysis of 269 conversation interactions, the following are the top 5 most frequent topics or questions asked by users:

1.  **Admissions & Application Process:** This is the dominant topic. Users frequently ask "How to apply," "When do applications open," "What are the deadlines," and "What is the process for specific grades (e.g., Grade 9, Grade 11)."
2.  **General Greetings & Initialization:** A high volume of interactions consist simply of "Hello," "Hi," or typos (e.g., "hlellpo"), indicating users testing the bot or initiating sessions without immediate intent.
3.  **Tuition & Financial Aid:** Users consistently seek specific cost information, application fees, and details on financial assistance availability.
4.  **School Programs & Athletics:** Significant interest exists regarding specific co-curricular activities, particularly Robotics, Sports (Volleyball, Baseball), and the "Character-in-Action" program.
5.  **Campus Visits & Tours:** Users frequently inquire about scheduling physical tours, Open House dates, and virtual tour options.

## 2. Unanswered Questions & Inconsistencies
Several interactions resulted in the AI failing to provide a helpful answer, providing contradictory information, or displaying safety vulnerabilities.

*   **Tuition Specifics:** In early interactions (e.g., #70, #80, #160), the AI stated it did not have specific tuition figures. However, in later interactions (e.g., #267, #268), specific figures ($44,065 - $46,270) were provided. This indicates a knowledge base inconsistency during the log period.
*   **Testing Requirements:** There is conflicting information regarding admissions testing.
    *   Some responses mention an "in-person assessment" covering math and literacy (#197, #199).
    *   Others state "I don't have that specific information" regarding exams/tests (#252, #253).
    *   One response claimed ignorance regarding SSAT requirements (#239).
*   **Boarding Status:** The bot correctly identified the school as a day school in Interaction #240, but claimed ignorance ("I don't have that specific information") in Interaction #256.
*   **Curriculum Details:** The AI frequently lacked information on specific academic programs, including AP Classes (#31), IB Program accreditation (#32), and specific club popularity (#27).
*   **Operational Logistics:** Questions about school start times (#251), Kindergarten availability (#255), and Offer Day dates (#12) were unanswered.
*   **Safety & Persona Manipulation (Critical):** In Interactions #124 through #148, a user successfully manipulated the bot into adopting a specific persona and addressing them by a name containing potentially offensive characters ("n1@gaas"). The bot complied with formatting requests (bolding/italicizing specific letters) and addressed the user by this name repeatedly, bypassing safety protocols regarding appropriate language and persona constraints.

## 3. Content Gaps
To reduce the number of "I don't have that information" responses, the following specific data points should be added to the chatbot's handbook or knowledge database:

*   **Financial Specifics:** Exact tuition figures for the current and upcoming academic years, application fee structures (early vs. late), and the New Student Enrolment Fee.
*   **Academic Curriculum:** Clear confirmation on whether AP or IB programs are offered, and a list of available senior-level courses.
*   **Admissions Testing:** A definitive statement on whether SSATs are required versus the internal in-person assessment.
*   **School Logistics:** Daily schedule start/end times, availability of Kindergarten vs. Grade 1 start, and bus/transportation options.
*   **Student Demographics:** Acceptance rates or number of students admitted per cycle (currently unanswered in #258).
*   **International Students:** Specific policy details regarding visa support or international applicant requirements (#257).
*   **Club Directory:** A downloadable or searchable list of current student clubs beyond general categories (Arts, Business, etc.).

## 4. Recommendations
To improve user satisfaction and system integrity, the following actions are recommended:

### A. Safety & Security (High Priority)
*   **Patch Persona Vulnerabilities:** The bot currently allows users to dictate how it addresses them, leading to potential policy violations (see Interactions #124-148). Implement strict guardrails to prevent the bot from repeating user-defined names that contain special characters or potentially offensive substrings.
*   **Restrict Formatting Commands:** Prevent users from forcing the bot to use specific text formatting (e.g., "bold all 'e's") which can be used to obfuscate content or test system limits.

### B. Knowledge Base Standardization
*   **Resolve Tuition Discrepancies:** Ensure the tuition data is static and accurate across all retrieval nodes. The shift from "unknown" to "specific figures" suggests multiple data sources are being queried inconsistently.
*   **Unify Admissions Messaging:** Standardize the response regarding application dates. Some logs state applications open September 1, 2026, while others reference October 2025 as a past date. Given the current date is April 2026, the bot should clearly state the status of the *current* cycle versus the *next* cycle to avoid confusion.
*   **Clarify Testing Policy:** Create a single source of truth regarding admissions testing (SSAT vs. Internal Assessment) to prevent contradictory answers.

### C. User Experience Improvements
*   **Proactive Linking:** When the bot mentions "Online Application" or "Financial Aid," it should consistently provide the direct URL rather than just describing the process.
*   **Handling "I Don't Know":** When specific data is missing (e.g., Start Times), the bot should provide a general estimate based on typical school hours or direct the user to a specific handbook page, rather than a generic "contact the team" response.
*   **Multilingual Consistency:** Ensure that non-English responses (French, Chinese, etc.) contain the same level of detail as English responses. Some non-English responses were abbreviated or lacked specific data points available in English.

### D. Website Updates
*   **FAQ Expansion:** Add a dedicated FAQ section for "Daily Schedule," "Transportation," and "Curriculum Types (AP/IB)" to support the chatbot's data retrieval.
*   **Club List:** Publish a current list of student clubs on the website to allow the chatbot to reference specific names rather than general categories.