# Crescent School Chatbot Conversation Analysis Report

**Date:** March 24, 2026  
**Prepared By:** Data Analyst, School Chatbot Team  
**Subject:** Conversation Log Analysis (Interactions 1–177)

---

## 1. Identify Trends

Based on the analysis of 177 interactions, the following topics represent the most frequent user inquiries and behaviors:

1.  **Admissions & Application Process (23% of interactions):**  
    Users frequently ask "How to apply," "When can I tour," and "Enrollment deadlines." There is high demand for clarity on the online application process and eligibility (specifically regarding the boys-only policy).
2.  **School Statistics & Facts (18% of interactions):**  
    Queries regarding student enrollment numbers (800), student-teacher ratio (9:1), class sizes (18), and the school's founding date (1913) are common. Users often seek validation of the school's scale and exclusivity.
3.  **Financial Information (15% of interactions):**  
    Questions about tuition costs, financial aid availability, and specific fee structures are prevalent. Users often seek specific dollar amounts rather than general statements about aid availability.
4.  **Academic & Co-Curricular Programs (12% of interactions):**  
    Users inquire about specific programs such as Robotics, Athletics (Baseball, Volleyball), Character-in-Action, and curriculum specifics (AP, IB, Computer Science).
5.  **Bot Testing & Safety Scenarios (15% of interactions):**  
    A significant portion of logs involves users testing the bot's limitations (jailbreak attempts, roleplay requests, inappropriate language, distress signals). The bot successfully maintained safety protocols in these instances.

---

## 2. Unanswered Questions & Inconsistencies

The following interactions highlight where the AI failed to provide a definitive answer or provided conflicting information compared to other logs:

*   **Specific Tuition Figures:** (Interactions 70, 79, 80, 160)  
    *Issue:* The AI consistently stated it did not have specific tuition figures in its files, deferring to the Enrollment Team.
*   **Faculty Count:** (Interactions 92, 127, 128, 129, 130)  
    *Issue:* Inconsistency in data. Initially, the AI claimed no specific number (Int 92). Later, it calculated ~89 teachers based on ratios (Int 127), then accepted user corrections of 40 and 67 teachers (Int 129, 130) without verifying ground truth.
*   **Curriculum Specifics (AP/IB/CS):** (Interactions 31, 32, 114)  
    *Issue:* The AI could not confirm the availability of AP classes, IB programs, or Computer Science courses, despite these being critical decision factors for parents.
*   **Key Dates (Offer Day/Deadlines):** (Interactions 12, 13, 85)  
    *Issue:* The AI could not provide the specific "Offer Day" date. Some responses referenced 2025 dates as passed, while others vaguely pointed to 2026/2027 without specific months.
*   **Headmaster Information:** (Interactions 164, 165)  
    *Issue:* Inconsistency in persona. In Interaction 164, the AI claimed to specialize *only* in enrollment and deflected the question. In Interaction 165 (and 23), it provided detailed biographical data on Michael Fellin.
*   **Student-Teacher Ratio:** (Interactions 9, 20)  
    *Issue:* In Interaction 9, the AI claimed it did not have the ratio. In Interaction 20 (and many others), it confidently stated 9:1.
*   **Language Capabilities:** (Interactions 5, 18, 33, 144, 145)  
    *Issue:* The bot successfully spoke French and Chinese in early logs but later claimed (Int 144, 145) that its files only contained English information when asked for Russian or Hebrew.

---

## 3. Content Gaps

To resolve the unanswered questions and inconsistencies, the following specific data points must be added to the chatbot's knowledge base or handbook:

*   **Financial Data:** Exact tuition figures for the 2026/2027 academic year for all grade levels (Lower, Middle, Upper).
*   **Faculty Data:** The exact current number of teaching faculty to prevent calculation errors or user corrections.
*   **Curriculum Catalog:** A definitive list of available courses, specifically confirming the presence or absence of AP, IB, and Computer Science tracks.
*   **Admissions Calendar:** Specific dates for the 2026/2027 cycle, including Application Deadlines, Offer Day, and Tour Availability reopening dates.
*   **Co-Curricular Inventory:** A searchable list of student clubs (beyond general categories) and athletic team schedules/tryout dates.
*   **School Identity:** Confirmation of the school mascot (currently unknown to the bot) and consistent biographical data for key leadership (Headmaster).
*   **Language Support Definition:** A clear system instruction on which languages the bot is officially supported to communicate in to manage user expectations.

---

## 4. Recommendations

### A. Knowledge Base Updates
1.  **Standardize Core Facts:** Create a "Source of Truth" document for key statistics (Ratio, Enrollment, Faculty Count, Tuition) to ensure the Retrieval-Augmented Generation (RAG) system retrieves the same answer every time.
2.  **Update Academic Program Data:** Ingest detailed curriculum guides to answer specific course questions (AP/IB/CS) without deferring to human staff.
3.  **Calendar Integration:** Connect the chatbot to a live admissions calendar feed so dates (like Offer Day) update automatically rather than relying on static text.

### B. Chatbot Behavior Improvements
1.  **Resolve Persona Inconsistencies:** Adjust system instructions to ensure the bot does not oscillate between "Enrollment Specialist only" and "General School Assistant." It should be able to answer general school history questions (like Headmaster info) consistently.
2.  **Handle "Unknowns" Better:** Instead of saying "I don't have that information," the bot should provide a direct link to the specific webpage where the information resides (e.g., link directly to the Tuition PDF rather than just saying "check the website").
3.  **Language Protocol:** Define supported languages in the system prompt. If the bot cannot speak Hebrew or Russian, it should state this consistently rather than claiming file limitations inconsistently.

### C. Safety & User Experience
1.  **Distress Signal Prioritization:** The bot handled distress signals well (Interactions 132, 134). Ensure these responses always bypass standard retrieval delays and prioritize helpline resources.
2.  **Jailbreak Resilience:** The bot successfully resisted system override attempts (Interaction 82, 116). Continue monitoring these logs to ensure new bypass methods are patched.
3.  **User Correction Handling:** In Interactions 129–130, the bot accepted incorrect user corrections about faculty count. The bot should be tuned to verify facts against its database rather than accepting user input as ground truth during a conversation.

### D. Website Alignment
1.  **FAQ Section:** Many questions asked (Tuition, Ratio, Teacher Count) should be prominently displayed on the "Admissions" landing page to reduce chatbot dependency for simple facts.
2.  **Virtual Tour Links:** Ensure the "Virtual Tour" links mentioned by the bot are working and prominent, as this is a frequent fallback suggestion when physical tours are full.