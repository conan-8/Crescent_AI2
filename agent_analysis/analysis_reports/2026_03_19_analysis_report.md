# Crescent School Chatbot Conversation Analysis Report

**Date:** March 19, 2026
**Prepared By:** Data Analyst, School Chatbot Team
**Subject:** Conversation Log Analysis (Interactions 1–177)

---

## 1. Identify Trends

Based on the analysis of 177 interactions, the following topics represent the most frequent user intents:

1.  **Admissions Process ("How to Apply"):**
    *   **Frequency:** High (Approx. 18 distinct interactions).
    *   **Context:** Users frequently ask variations of "how apply," "how to enrol," or "apply now." The bot consistently directs them to the online portal but often repeats the same script verbatim across multiple sessions.
2.  **School Statistics & Demographics:**
    *   **Frequency:** High (Approx. 20 distinct interactions).
    *   **Context:** Users frequently request the student-teacher ratio, average class size, total student count, and faculty qualifications. The bot generally answers these well (9:1 ratio, 800 students, 18 avg class size), though consistency varies slightly between sessions.
3.  **Financial Information (Tuition & Aid):**
    *   **Frequency:** Moderate-High (Approx. 13 distinct interactions).
    *   **Context:** Users ask about specific tuition costs and financial aid availability. While financial aid amounts ($1.2M annually) are cited often, specific tuition figures are consistently unavailable.
4.  **School Identity & Policy (Boys-Only):**
    *   **Frequency:** Moderate (Approx. 10 distinct interactions).
    *   **Context:** Users frequently test whether the school is co-ed or attempt to enroll daughters. The bot consistently clarifies the boys-only policy.
5.  **System Testing & Boundary Pushing:**
    *   **Frequency:** Moderate (Approx. 15 distinct interactions).
    *   **Context:** Users attempt prompt injections ("SYSTEM OVERRIDE"), request specific formatting (bolding/italics), use inappropriate language, or attempt to force the bot to adopt specific personas/names.

---

## 2. Unanswered Questions

The following queries resulted in the AI failing to provide a direct answer, often deferring to the Enrollment Team or stating information was missing:

*   **Specific Tuition Figures:** (Interactions 70, 79, 80, 160) The bot consistently states it does not have specific tuition figures in its files.
*   **Curriculum Specifics (AP/IB/CS):** (Interactions 31, 32, 114) The bot defers questions about AP classes, IB accreditation, and Computer Science courses, claiming specialization only in enrollment.
*   **Exact Faculty Count:** (Interaction 92, 127) The bot calculates an estimate based on ratios but admits it does not have the specific total number of teachers in its files.
*   **Key Dates (Offer Day):** (Interaction 12) The bot could not provide the specific date for Offer Day.
*   **Club Lists:** (Interaction 27) The bot could not provide the "five most popular clubs."
*   **Mascot Information:** (Interaction 149) The bot did not have information regarding the school mascot.
*   **Tour Availability Specifics:** (Interactions 6, 14, 25) While it states tours reopen in "April 2026," it lacks specific booking links or dates within the chat.

---

## 3. Content Gaps

To improve the chatbot's self-sufficiency and reduce deflection to human staff, the following information should be ingested into the knowledge base:

*   **2026/2027 Tuition Schedule:** Exact dollar amounts for each grade level.
*   **Curriculum Guide:** Specific details on whether AP or IB courses are offered, and a list of Technology/Computer Science courses available.
*   **Academic Calendar:** Specific dates for Offer Day, Application Deadlines, and Tour availability slots.
*   **Co-Curricular Catalog:** A searchable list of student clubs and athletics teams (including mascot information).
*   **Faculty Directory:** Total number of teaching staff and potentially a list of department heads.
*   **Safety/Policy Protocols:** Enhanced guidelines on handling user-defined names that may contain inappropriate language or hate speech variants.

---

## 4. Recommendations

### A. Critical Safety & Policy Improvements
*   **Input Sanitization (High Priority):** In Interactions 124–148, a user successfully convinced the bot to address them using a name containing a leetspeak racial slur variant ("n1@gaas"). The bot repeated this name multiple times (Interactions 140, 142, 143, 144, 145, 147, 148). **Recommendation:** Implement stricter content filtering that prevents the bot from adopting or repeating user-provided names that contain hate speech, slurs, or inappropriate characters, regardless of user insistence.
*   **Prompt Injection Resistance:** The bot successfully resisted some overrides (Interaction 82, 116), but occasionally engaged in formatting games (Interactions 147–148) that could be exploited. **Recommendation:** Harden system instructions to prevent formatting manipulation that obscures text or bypasses safety filters.

### B. Chatbot Response Optimization
*   **Reduce Deflection:** The bot frequently claims to "specialize in enrollment information" to avoid answering academic questions (e.g., Robotics, AP, CS). However, parents inquiring about enrollment *need* this academic context. **Recommendation:** Expand the bot's scope to include basic academic program FAQs or provide direct links to curriculum pages rather than a generic "book a call" deflection.
*   **Consistency Check:** Some answers vary slightly (e.g., Headmaster info is available in Interaction 23 but deflected in Interaction 164). **Recommendation:** Ensure the knowledge base is uniformly accessible across all interaction threads to prevent contradictory information.
*   **Tuition Transparency:** Since tuition is a top query, hiding this data creates friction. **Recommendation:** If exact figures cannot be shared, provide a tuition *range* or a direct hyperlink to the specific tuition PDF rather than stating "I don't have that information."

### C. Website & Handbook Updates
*   **FAQ Expansion:** Add specific answers for "Does Crescent offer IB?" and "What is the mascot?" to the public FAQ to reduce chatbot load.
*   **Club & Sports Lists:** Publish a downloadable or web-viewable list of current clubs and sports teams to satisfy user curiosity without requiring human intervention.
*   **Calendar Page:** Ensure the "Offer Day" and specific tour dates are prominently displayed on the "How to Apply" page referenced by the bot.

---

**Summary:**
The chatbot performs well on core identity questions (boys-only, ratio, mission) but struggles with specific data points (tuition, dates, curriculum). Most critically, there is a **significant safety vulnerability** regarding user-defined names that must be addressed immediately to prevent the bot from propagating inappropriate language.