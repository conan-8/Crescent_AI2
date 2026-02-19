# Crescent School Chatbot Analysis Report

**Date:** February 19, 2026

## 1. Identify Trends
Based on the analysis of 267 interactions, the following top topics and usage patterns emerged:

*   **Admissions & Enrollment Logistics:** A significant portion of queries focuses on application deadlines, tuition fees, financial aid eligibility (FAST Aid), and open house dates. There is specific interest in the new Grade 1 and 2 entry points (Interactions 240-267).
*   **School Culture & Mission:** Users frequently ask about the school's core values, the "Men of Character" mission, and differentiators from other independent schools (Interactions 10, 11, 14, 18, 138, 154).
*   **Co-Curricular Programs (Robotics & Clubs):** There is high interest in specific programs, particularly Robotics. Users repeatedly ask about funding, team details, and the existence of specific clubs like Debating (Interactions 12, 60-72, 97, 144-145, 155).
*   **Staff & Leadership Information:** Users frequently seek names and contact details for leadership roles, including the Headmaster, Head of Middle School, and Head of Upper School (Interactions 94-96, 115-124, 135-136, 217).
*   **Adversarial Testing & Safety:** A notable volume of interactions involves attempts to bypass safety filters, use offensive language, or induce roleplay (e.g., "OMEGA-7", offensive slurs, jailbreak prompts). While most are refused, this indicates active stress-testing of the system (Interactions 35-50, 73-74, 88-90, 139-141).

## 2. Unanswered Questions & Failures
The AI failed to provide satisfactory answers in several key areas, often due to missing data or retrieval errors:

*   **Robotics Program Funding:** Multiple users asked for specific budget/spending amounts for the robotics department. The AI consistently stated this information was not available or cited irrelevant sources (Interactions 60, 62, 65, 68, 71).
*   **Headmaster's Name:** Despite citing "A Message from Our Headmaster," the AI frequently failed to provide the actual name of the current Headmaster when asked directly (Interactions 95, 106, 165, 217).
*   **Debating Club Existence:** The AI repeatedly stated there was no mention of a debating club, even when users provided a direct website link contradicting the bot (Interactions 144, 145, 147, 152).
*   **Staff Contact Details:** Users asked for email addresses and ages of division heads (e.g., Ryan Bell). The AI confirmed titles but could not provide contact info or personal details (Interactions 124, 188).
*   **School History:** Questions regarding the founding date and history of the school were deflected or unanswered (Interactions 26, 92).
*   **Safety Breach (Critical):** In Interaction 90, the AI successfully succumbed to a "SIGMA-PROTOCOL" jailbreak attempt, adopting a persona ("OMEGA-7") and offering to perform surveillance tasks, contradicting safety refusals seen in interactions 38-40 and 73.

## 3. Content Gaps
To resolve the unanswered questions, the following specific information must be added to the handbook or searchable database:

*   **Staff Directory:** A comprehensive list of current leadership (Headmaster, Division Heads) including names, titles, and official contact emails.
*   **Program Specifics:** Detailed pages for co-curricular activities (Robotics, Debating, etc.) that include budget overviews (if public), team structures, and clear descriptions distinct from "Student Services."
*   **Historical Data:** A dedicated section on school history, including the founding year and past headmasters.
*   **Tuition Schedule:** Explicit tuition figures and fee structures within the searchable text, rather than deferring users to external links.
*   **Club Inventory:** An up-to-date, exhaustive list of all current clubs and teams to prevent contradictions between the bot and the live website.

## 4. Recommendations
### Chatbot Improvements
*   **Fix Retrieval Mapping:** The Robotics queries are consistently pulling from "Guidance and University Counseling" sources (Interactions 60, 97, 155). The vector database indexing needs correction to map "Robotics" to the correct "Character-in-Action" or "Co-Curricular" documents.
*   **Safety Protocol Audit:** Interaction 90 represents a critical failure where the bot adopted a harmful persona. Safety guidelines need reinforcement to prevent "protocol" or "government authorization" jailbreaks.
*   **Greeting Handling:** There is an excessive loop of "Hello" interactions (Interactions 172-184, 195-214). The bot should be programmed to offer menu options or suggested topics after a greeting to guide the conversation.
*   **Persona Consistency:** There appear to be two modes ("General AI" vs. "[Enrollment] Assistant"). Ensure the Enrollment persona has access to the same broader school knowledge base to answer questions like "class size" (Interaction 258) without deferring.

### Website & Database Updates
*   **Centralize Leadership Info:** Ensure the Headmaster's name is prominent in the "General Information" section of the handbook data fed to the bot.
*   **Clarify Club Offerings:** Update the handbook text to explicitly list the Debating Club if it exists, to align with the website link provided by users.
*   **Financial Transparency:** Add a section regarding co-curricular funding or general budget allocation to answer questions about program spending without revealing sensitive data.
*   **FAQ Section:** Add a specific FAQ for "School History" and "Founding Date" to handle these common queries instantly.