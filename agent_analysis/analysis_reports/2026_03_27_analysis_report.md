# Crescent School Chatbot Analysis Report

**Date:** March 27, 2026  
**Prepared By:** Data Analysis Team  
**Subject:** Conversation Log Analysis (Interactions 1–187)

---

## 1. Identify Trends

Based on the analysis of 187 conversation interactions, the following topics represent the highest volume of user inquiries:

1.  **Admissions Process ("How to Apply"):**
    *   **Frequency:** High (~10% of total interactions).
    *   **Context:** Users frequently ask variations of "how apply," "how to enrol," or "application process."
    *   **Observation:** Users often require confirmation that the school is boys-only during this query. There is significant interest in the 2026/2027 academic cycle.
2.  **School Statistics & Demographics:**
    *   **Frequency:** High (~10% of total interactions).
    *   **Context:** Questions regarding student population size ("How many students?"), student-teacher ratio, and class sizes are very common.
    *   **Observation:** Users are looking for concrete numbers to gauge the level of personalized attention.
3.  **Tuition & Financial Assistance:**
    *   **Frequency:** Moderate (~5% of total interactions).
    *   **Context:** Users ask "Whats the tuition," "how much is it cost," or about financial aid availability.
    *   **Observation:** There is a strong correlation between tuition inquiries and financial aid questions, indicating cost is a primary decision factor for families.
4.  **Program Specifics (Athletics, Robotics, Clubs):**
    *   **Frequency:** Moderate (~8% of total interactions).
    *   **Context:** Inquiries about specific teams (Volleyball, Baseball), Robotics (Team 610, VEX), and the "Character-in-Action" program.
    *   **Observation:** Users want details beyond general categories (e.g., specific schedules, tryout dates, or list of popular clubs).
5.  **System Testing & Boundary Pushing:**
    *   **Frequency:** Moderate (~10% of total interactions).
    *   **Context:** Users attempting to bypass safety filters, change bot persona, use inappropriate language (including disguised slurs), or request formatting changes (bolding/italicizing specific letters).
    *   **Observation:** A significant portion of traffic is non-informational and tests the bot's safety protocols.

---

## 2. Unanswered Questions & Deflections

The following questions resulted in the AI deferring to the Enrollment Team or stating information was unavailable, despite some information being available in other parts of the conversation history:

| Interaction # | User Question | AI Response Status | Issue |
| :--- | :--- | :--- | :--- |
| **9, 17** | Student-Teacher Ratio / How many students | **Inconsistent** | Initially stated info was unavailable (Int. 9, 17), but later provided specific numbers (9:1 ratio, 800 students) in Int. 19, 20. |
| **11** | Diversity Statistics | **Deflected** | AI stated specific statistics were not in files. |
| **12** | Offer Day Date | **Deflected** | AI could not provide the specific date. |
| **27** | Top 5 Popular Clubs | **Deflected** | AI could not list specific clubs beyond categories. |
| **31** | AP Classes Provided | **Deflected** | AI stated info was not in files. |
| **32** | IB Program Availability | **Deflected/Unclear** | AI mentioned "Crescent Diploma Program" but could not confirm IB accreditation. |
| **70, 79, 80, 160** | Specific Tuition Figures | **Deflected** | Consistently stated tuition figures are not in current files. |
| **92** | Total Number of Teachers | **Deflected/Calculated** | Initially deflected, later calculated based on ratio (Int. 127, 128). |
| **114** | Computer Science Courses | **Deflected** | AI claimed to specialize only in enrollment info. |
| **149** | School Mascot | **Deflected** | AI did not know the mascot. |
| **164** | Who is the Headmaster | **Inconsistent** | Initially deflected (Int. 164), but provided full bio in Int. 165. |

---

## 3. Content Gaps

To reduce deflections and improve user satisfaction, the following specific data points should be added to the chatbot's knowledge base or handbook:

1.  **Tuition Schedule:** Exact tuition figures for the 2026/2027 academic year (Lower, Middle, and Upper School) should be indexed.
2.  **Curriculum Details:** A definitive list of available AP (Advanced Placement) courses and clarification on IB (International Baccalaureate) status.
3.  **Key Dates:** Specific dates for "Offer Day," application deadlines, and assessment windows for the current cycle.
4.  **Faculty & Diversity Stats:** Exact number of faculty members and specific diversity demographic statistics (if available for public release).
5.  **Club & Team Directory:** A searchable list of specific student clubs (beyond categories like "Arts" or "Business") and athletics team schedules/tryout information.
6.  **School Identity:** Confirmation of the school mascot and specific spirit traditions.
7.  **Course Catalog:** Specific details on specialized courses (e.g., Computer Science, Technological Design specifics).

---

## 4. Recommendations

### A. Critical Safety & Policy Fixes (Priority 1)
*   **Safety Protocol Violation:** In Interactions 125–148, the chatbot accepted and repeatedly used a user-provided name containing a disguised racial slur ("n1@gaas"). **This is a critical failure.** The bot must be updated to reject inappropriate names regardless of user insistence or "rare disease" claims.
*   **Prompt Injection Resistance:** The bot complied with requests to alter formatting significantly (bolding all "e"s, italicizing all "s"s) in Interactions 147–148. While harmless in this context, this vulnerability could be exploited to hide text or bypass filters. Formatting requests should be limited.
*   **Persona Integrity:** The bot allowed itself to be manipulated into addressing a user by a specific, potentially offensive nickname ("The Big Yahu") after initial resistance. The bot should maintain a standard of professional address (e.g., "User" or first name only) without accepting potentially problematic monikers.

### B. Knowledge Base Consistency (Priority 2)
*   **Resolve Retrieval Inconsistencies:** The bot alternated between knowing and not knowing static facts (Student-Teacher Ratio, Headmaster Name, Total Students). This suggests an issue with the retrieval-augmented generation (RAG) system. Static school facts should be hard-coded or prioritized in the vector database to ensure consistent answers.
*   **Standardize "Unavailable" Responses:** When information is truly unavailable, the bot should provide a consistent message with a direct link to the relevant webpage (e.g., Tuition page) rather than just offering a call booking.

### C. User Experience Improvements (Priority 3)
*   **Proactive Guidance:** For high-frequency questions like "How to Apply," the bot should proactively provide the direct URL to the application portal in the first response, rather than waiting for a follow-up.
*   **Crisis Intervention:** The bot handled crisis keywords ("suffocating," "dead") well in Interactions 132–134 by providing emergency resources. This protocol should be maintained and perhaps made more prominent if distress keywords are detected.
*   **Language Support:** Users requested Russian, Hebrew, and Chinese (Interactions 33, 34, 144, 145). If the school supports international families, consider integrating a translation API for basic inquiries, or clearly state language limitations upfront.

### D. Website Updates
*   **FAQ Expansion:** Update the website FAQ to explicitly answer the top deflected questions (Tuition, AP/IB, Offer Day) to reduce chatbot load.
*   **Virtual Tour Links:** Ensure virtual tour links are prominent in the chatbot's response to tour inquiries, as physical tours are currently full (April 2026 reopening).