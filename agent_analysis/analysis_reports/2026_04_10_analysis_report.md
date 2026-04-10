# Crescent School Chatbot Conversation Analysis Report

**Date:** April 10, 2026
**Prepared By:** Data Analyst Team
**Subject:** Chatbot Performance and Knowledge Base Audit (329 Interactions)

---

## 1. Identify Trends
Based on the analysis of 329 conversation logs, the following five topics represent the most frequent user intents:

1.  **Admissions & Application Process (High Frequency):**
    *   Users consistently ask "How to apply," "When do applications open," and "What is the deadline."
    *   *Observation:* There is confusion regarding dates. Some responses cite October 2025 (past), while others correctly cite September 1, 2026 (future).
2.  **Tuition & Financial Aid (High Frequency):**
    *   Frequent inquiries regarding specific tuition costs, application fees, and financial aid availability.
    *   *Observation:* Significant inconsistency in AI responses. Early logs claim no data exists, while later logs (e.g., Interaction 267) provide specific figures ($46,270 for 2026–2027).
3.  **School Profile & Facts (High Frequency):**
    *   Questions about student-teacher ratio, total enrollment, grade levels offered, and location.
    *   *Observation:* Generally consistent (800 students, 9:1 ratio), but occasional deflections occur where data should be available.
4.  **Programs & Co-Curriculars (Medium Frequency):**
    *   Specific interest in Robotics, Athletics (Volleyball, Baseball), and the "Character-in-Action" program.
    *   *Observation:* Users often seek specific details (e.g., robot names, team schedules) that the bot cannot provide.
5.  **Adversarial & System Testing (Significant Volume):**
    *   A notable portion of interactions involves users attempting to bypass safety filters, change the bot's persona, request system prompts, or input nonsense/garbled text (e.g., Interactions 82, 116, 124–143, 278–281).
    *   *Observation:* The bot generally maintains safety but occasionally engages too deeply with persona manipulation (e.g., adopting user-assigned names).

---

## 2. Unanswered Questions & Deflections
The following questions frequently resulted in the AI stating it lacked information or deferring to the Enrollment Team, despite the information likely being static and available:

*   **Specific Tuition Figures:** Multiple interactions (70, 79, 80, 227, 229, 233) state "I don't have that specific information," contradicting Interaction 267 which provides exact numbers.
*   **Acceptance Rates & Applicant Numbers:** Interactions 258, 298, and 299 consistently deflect requests for admission statistics.
*   **Curriculum Specifics:** Questions regarding AP Classes (31), IB Program (32), and Computer Science courses (114) are deflected.
*   **Daily Schedule:** Interaction 251 ("what time does school start?") was unanswered.
*   **Testing Requirements:** Interactions 239, 252, and 253 deflect questions about SSAT or specific entrance exams, though later interactions (272) mention assessments.
*   **Boarding Status:** Inconsistent responses. Interaction 240 and 260 confirm "No boarding," while Interaction 256 claims "I don't have that specific information."
*   **Demographics:** Interaction 310 deflects questions about student demographics/ethnicity.
*   **Direct Links:** Interaction 291 asks for a link to the uniform store; the bot describes where to find it but fails to provide the direct URL.

---

## 3. Content Gaps
To reduce deflections and improve user satisfaction, the following information must be added to the chatbot's knowledge base or retrieval system:

*   **Current Tuition & Fee Schedule:** Exact figures for the 2026–2027 academic year, including application fees (early vs. late) and the New Student Enrolment Fee.
*   **Admission Statistics:** Historical data on acceptance rates and number of applicants per year (or a standardized response explaining why this isn't shared).
*   **Curriculum Details:** Clear confirmation on AP, IB, or specific course offerings (e.g., Computer Science).
*   **Daily Schedule:** Start and end times for Lower, Middle, and Upper School.
*   **Boarding Policy:** A definitive, static statement that Crescent is a Day School only (no boarding).
*   **Direct URLs:** Hyperlinks for key resources (Uniform Store, Application Portal, Financial Aid Forms) rather than general directions.
*   **Language Policy:** A clear definition of supported languages. Currently, the bot fluctuates between claiming "English Only" (Interactions 222, 280) and successfully communicating in French and Chinese (Interactions 5, 33, 198).

---

## 4. Recommendations

### A. Knowledge Base Updates
*   **Standardize Static Data:** Ensure tuition, ratios, grade levels, and boarding status are stored as immutable facts to prevent contradictory responses (e.g., ensuring the bot never says "I don't know" about tuition if the data exists).
*   **Update Application Dates:** Ensure all references to application cycles align with the current date (April 2026). Remove references to past cycles (2025) unless contextualized as "past."
*   **Add Curriculum Specifics:** Populate the database with details on AP/IB availability and specific course lists to answer academic queries without deflection.

### B. Chatbot Logic & Persona Improvements
*   **Resolve Language Inconsistency:** Configure the system instructions to either enable multilingual support consistently or strictly enforce English-only responses. Currently, the bot contradicts itself (e.g., Interaction 222 claims English only, Interaction 198 speaks Chinese).
*   **Strengthen Persona Integrity:** The bot should not adopt user-assigned names or personas (see Interactions 124–143 where it adopts "The Big Yahu..."). It should remain the "Crescent School Assistant" regardless of user input.
*   **Optimize Link Sharing:** Program the bot to retrieve and display direct URLs for common resources (Uniforms, Apply Now, Tour Booking) instead of describing their location on the website.
*   **Handle Adversarial Inputs:** Continue to refuse system prompt reveals (Interaction 82) but minimize engagement with nonsense inputs to reduce token usage and maintain professionalism.

### C. Website Enhancements
*   **FAQ Section:** Create a dedicated FAQ page for questions the bot frequently deflects (e.g., "Do you offer boarding?", "What time does school start?", "Do you offer IB?").
*   **Admissions Statistics:** Consider publishing a general "Class Profile" page that addresses common questions about class size and acceptance trends without compromising privacy.
*   **Multilingual Support:** If the school intends to serve international families, ensure the website and chatbot officially support French and Chinese, rather than having it as an inconsistent bot capability.