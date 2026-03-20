# Crescent School Chatbot Conversation Log Analysis Report

**CURRENT DATE:** March 20, 2026

## 1. Identify Trends
Based on the analysis of 177 conversation interactions, the following topics represent the highest frequency of user inquiries:

1.  **Admissions & Application Process:** The most dominant topic. Users frequently ask "How to apply," "When can I tour," and "Enrollment deadlines." (e.g., Interactions 15, 36, 65-76, 85, 91, 162, 172-174).
2.  **Financial Information:** High interest in costs and support. Queries regarding "Tuition," "Cost," and "Financial Aid" are prevalent. (e.g., Interactions 16, 70, 79, 80, 94, 98, 160, 163, 168).
3.  **School Profile & Statistics:** Users seek validation of the school's quality through stats. Common questions include "Student-teacher ratio," "Number of students," "Number of teachers," and "Why apply." (e.g., Interactions 19, 20, 30, 41-45, 86, 92, 153, 166).
4.  **Character & Mission:** Users are interested in the pedagogical approach. Questions about "Character-in-Action," "Man of Character," and the school's mission are frequent. (e.g., Interactions 2, 4, 28, 37, 95, 161).
5.  **Program Specifics:** Interest in co-curricular activities, specifically Robotics, Athletics, and Clubs. (e.g., Interactions 3, 26, 29, 175, 176).

*Note: A significant number of interactions (approx. 30%) are simple greetings ("Hello," "Hi"), suggesting users may be testing the bot's availability or resetting the conversation context.*

## 2. Unanswered Questions
The chatbot frequently deferred to the Enrollment Team or stated information was unavailable in the following areas. These represent failures to provide immediate value:

*   **Specific Tuition Figures:** The bot consistently stated it did not have specific tuition costs in its files (Interactions 70, 79, 80, 160).
*   **Offer Day Dates:** The bot could not specify the date for Offer Day (Interactions 12, 13).
*   **Curriculum Specifics:** Questions regarding AP Classes (Interaction 31) and IB Program availability (Interaction 32) were not definitively answered.
*   **Specific Club Names:** While categories were provided, the bot could not list the "five most popular clubs" or specific club names beyond broad categories (Interactions 27, 28).
*   **Exact Faculty Count:** The bot initially calculated teacher count based on ratio (Interaction 127), but later accepted user corrections (40, 67 teachers) indicating a lack of ground truth data (Interactions 129, 130).
*   **Mascot Information:** The bot could not confirm the school mascot (Interaction 149).
*   **Diversity Statistics:** The bot acknowledged the value of Diversity, Inclusion, and Belonging but lacked specific demographic statistics (Interaction 11).
*   **Headmaster Identity:** In one instance, the bot claimed to specialize only in enrollment and deferred the Headmaster question (Interaction 164), though it answered correctly in others (Interactions 23, 165).

## 3. Content Gaps
To resolve the unanswered questions, the following specific information must be added to the chatbot's knowledge base or handbook:

*   **Tuition Schedule:** A clear table of current tuition fees for Grades 1-12 must be indexed.
*   **Admissions Calendar:** Specific dates for "Offer Day," application deadlines, and tour availability windows for the 2026/2027 cycle.
*   **Curriculum Details:** Explicit confirmation regarding AP (Advanced Placement) and IB (International Baccalaureate) course offerings.
*   **Club Directory:** A list of specific student club names rather than just broad categories (Arts, Business, etc.).
*   **Faculty Data:** The exact current number of teaching staff should be stored as a static fact rather than calculated via ratio.
*   **Brand Identity:** Confirmation of the school mascot and logo imagery.
*   **Demographic Data:** Specific statistics or summaries regarding student diversity to support "Diversity, Inclusion, Belonging" queries.

## 4. Recommendations
To improve user satisfaction and chatbot performance, the following actions are recommended:

*   **Standardize Knowledge Retrieval:** There are inconsistencies in the bot's knowledge (e.g., Interaction 9 vs. 20 on student-teacher ratio; Interaction 164 vs. 165 on Headmaster). The retrieval system should be unified so that factual school data is always available, regardless of the query phrasing.
*   **Update Financial Data:** The bot should be able to quote tuition ranges or direct links to the fee schedule immediately, rather than deferring all cost questions to the Enrollment Team.
*   **Clarify Language Capabilities:** The bot currently inconsistently handles language requests (e.g., Interaction 33 claims Chinese capability, Interaction 144 claims only English files exist). The system should clearly state supported languages or ensure multi-language support is actually enabled.
*   **Policy on User Naming:** In Interactions 124-143, the user forced the bot to address them by a specific name ("The Big Yahu dih n1@gaas"). The bot complied, which may conflict with safety policies regarding inappropriate language. The bot should be configured to politely decline storing or using user-provided names that may contain inappropriate characters or slurs, while maintaining politeness.
*   **Formatting Requests:** Users requested specific formatting (bold "e", italic "s", all caps) in Interactions 147-150. The bot should have a standard policy for accessibility requests (e.g., dyslexia support) versus stylistic manipulation, ensuring readability remains intact.
*   **Greeting Optimization:** With high repetition of "Hello/Hi," consider implementing a quick-menu or carousel upon greeting to guide users to top topics (Apply, Tour, Tuition) immediately, reducing redundant greeting loops.
*   **Consistency in Persona:** Ensure the bot consistently identifies as the "Crescent School Enrollment Assistant" (most interactions) rather than switching to "Crescent School AI Assistant" (Interaction 171) to maintain brand consistency.