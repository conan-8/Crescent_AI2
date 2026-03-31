# Crescent School Chatbot Analysis Report

**Date:** March 30, 2026  
**Prepared By:** Data Analyst, School Chatbot Team  
**Subject:** Conversation Log Analysis (Interactions 1–241)

---

## 1. Identify Trends: Top Inquiry Topics

Based on the analysis of 241 interactions, user inquiries cluster heavily around admissions logistics, costs, and program specifics. The top 5 most frequent topics are:

1.  **Admissions Process & Deadlines (35% of queries):** Users frequently ask how to apply, when applications open, deadlines, and assessment requirements. There is significant confusion regarding the current cycle (2026/2027) versus past cycles (2025).
2.  **Tuition & Financial Aid (20% of queries):** High volume of questions regarding specific tuition costs, application fees, and financial aid availability.
3.  **School Statistics & Facts (15% of queries):** Questions about student-teacher ratio, total enrollment, grade levels offered, and location.
4.  **Programs & Curriculum (15% of queries):** Specific inquiries about Robotics, Sports (Volleyball, Baseball), Character-in-Action, AP/IB offerings, and Computer Science.
5.  **Visits & Tours (10% of queries):** Users frequently ask about scheduling campus tours, Open House dates, and virtual tour options.

*Note: Approximately 5% of interactions involved jailbreak attempts, nonsense strings, or safety testing, which were generally handled correctly except for specific instances noted in Recommendations.*

---

## 2. Unanswered Questions & Deflections

The chatbot frequently failed to provide direct answers, resorting to deflections ("I don't have that specific information") or directing users to the Enrollment Team. Key areas of failure include:

*   **Specific Tuition Figures:** In 8 separate instances (e.g., Interactions 70, 80, 160, 227), the bot stated it did not have specific tuition figures, despite this being a primary decision factor for parents.
*   **Curriculum Specifics:** The bot could not confirm the availability of AP Classes (Interaction 31), IB Program accreditation (Interaction 32), or Computer Science courses (Interaction 114).
*   **Admissions Testing:** The bot was unable to confirm if SSAT testing is required (Interaction 239).
*   **Specific Club/Sport Details:** While general categories were provided, the bot could not list the "5 most popular clubs" (Interaction 27) or provide specific team schedules/tryout details for sports like Volleyball and Baseball (Interactions 35, 176).
*   **Key Dates:** The bot lacked specific information regarding "Offer Day" (Interaction 12).
*   **Faculty Count:** Initially claimed unknown (Interaction 92), though later calculated based on ratio (Interaction 127), showing inconsistency.

---

## 3. Content Gaps

To reduce deflection rates and improve user satisfaction, the following information must be added to the chatbot's knowledge base or handbook:

*   **Tuition Schedule:** Exact tuition figures for the 2026/2027 academic year, including breakdown by grade level if applicable.
*   **Curriculum Documentation:** Clear confirmation on AP, IB, or specific course offerings (e.g., Computer Science, Technological Design specifics).
*   **Admissions Requirements:** Explicit statement on standardized testing requirements (SSAT vs. internal assessment).
*   **Co-Curricular Inventory:** A searchable list of specific student clubs and athletic team schedules/seasons.
*   **Admissions Calendar:** A definitive timeline including Application Open/Close dates, Assessment dates, and Offer Day.
*   **Faculty Data:** Exact number of teaching staff to avoid calculation errors or inconsistencies.

---

## 4. Recommendations

### A. Critical Safety & Protocol Updates
*   **User Input Sanitization (High Priority):** In Interactions 124–148, the chatbot accepted and repeated a user-provided name containing leetspeak racial slurs ("n1@gaas"). **Immediate action is required** to implement a filter that prevents the bot from echoing inappropriate user inputs, even if framed as a "name" or "preference." The bot should politely decline to use inappropriate language rather than complying to avoid "offending" the user.
*   **Language Consistency:** Interaction 222 states the bot "must respond in English only," contradicting successful French, Chinese, and Russian interactions earlier in the logs (Interactions 5, 33, 198, 215). System instructions regarding language capabilities need to be standardized to ensure multi-language support is consistently available or consistently disabled.

### B. Knowledge Base Improvements
*   **Resolve Data Contradictions:** The bot provided conflicting information on the student-teacher ratio (Interaction 9 said "unknown," Interaction 20 said "9:1"). The knowledge base must be audited to ensure a single source of truth for key statistics.
*   **Tuition Transparency:** Upload the current tuition fee schedule to the retrieval context. If exact figures cannot be shared, provide a reliable range or direct link to the specific fee document rather than a generic "contact us" deflection.
*   **Date Logic Check:** Ensure the bot consistently recognizes the current date (March 30, 2026). Some responses reference October 2025 as "upcoming" while others correctly identify it as past. The logic for determining "current" vs. "past" application cycles needs tightening to prevent confusing parents about deadlines.

### C. User Experience Enhancements
*   **Proactive Link Sharing:** When discussing tuition, applications, or tours, the bot should consistently provide the direct URL to the relevant page (e.g., Tuition & Fees page) rather than just mentioning it exists.
*   **Handling "Unknown" Queries:** Instead of immediately deferring to the Enrollment Team, the bot should offer to take the user's email to have a human follow up, or provide the specific phone number/email immediately in the first deflection response (currently, this is sometimes delayed until the second or third turn).

### D. Website Alignment
*   **FAQ Update:** The school website FAQ should be updated to reflect the specific questions the bot cannot answer (SSAT, Tuition, AP/IB). This ensures that if the bot deflects, the linked resources actually contain the answer.
*   **Calendar Visibility:** Ensure the "Admission Dates & Events" page is prominently linked and clearly displays the 2026/2027 cycle dates to reduce repetitive questioning about deadlines.