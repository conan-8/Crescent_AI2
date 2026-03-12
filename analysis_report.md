# Chatbot Conversation Analysis Report

**Date:** March 11, 2026  
**Prepared By:** Crescent School AI Club 
**Subject:** Crescent School Enrollment Assistant Performance Review

---

## 1. Identify Trends
Based on the 23 interactions analyzed, user inquiries cluster heavily around logistical admissions data and specific school demographics. The top 5 frequent topics are:

1.  **Admissions Logistics & Tours:** Users frequently ask about scheduling campus tours, enrollment procedures, and specific admissions dates (e.g., "Offer Day"). *Note: Tour availability is a high-friction point as physical tours are currently full until April 2026.*
2.  **School Demographics & Statistics:** There is high demand for quantitative data, including student population size, student-teacher ratios, and diversity statistics.
3.  **Program Specifics:** Users are interested in specific co-curricular offerings, particularly Robotics and "Character-in-Action" programs.
4.  **School Identity & Policy:** Questions regarding gender policy (Co-ed vs. Boys-only) and location are common initial qualifiers.
5.  **Financial & Leadership Information:** Inquiries regarding financial aid availability and leadership bios (Headmaster) indicate parents are vetting the school's stability and values.

## 2. Unanswered Questions
The following interactions resulted in deflections, generic fallback responses, or initial failures to retrieve known information:

*   **Diversity Statistics (Interaction 11):** The AI explicitly stated it did not have specific statistics regarding the diversity of the student body.
*   **Admissions Dates (Interaction 12 & 13):** The AI could not provide the specific date for "Offer Day," stating the provided passage did not specify it.
*   **Competitive Comparison (Interaction 22):** The AI deflected when asked how Crescent compares to other schools, citing a specialization limit.
*   **Inconsistent Data Retrieval (Interactions 9 & 17):**
    *   **Student-Teacher Ratio:** In Interaction 9, the AI claimed it did not have the information. However, in Interaction 20, it successfully provided the ratio (9:1).
    *   **Student Count:** In Interaction 17, the AI deflected. In Interaction 19, it successfully provided the count (800 students).
    *   *Analysis:* These inconsistencies suggest the information exists in the database but the retrieval system is unstable or keyword-sensitive.

## 3. Content Gaps
To reduce deflections and improve user satisfaction, the following specific information should be added or indexed in the school handbook/database:

*   **Admissions Timeline:** Specific dates for key admissions milestones (e.g., "Offer Day") need to be explicitly indexed in the admissions section of the knowledge base.
*   **Diversity & Inclusion Data:** If permissible, specific demographic breakdowns or qualitative statements regarding diversity should be added to the "Why Crescent" or "Community" sections to satisfy Inquiry 11.
*   **Competitive Positioning Statement:** While direct comparison to other schools may be sensitive, a standardized response highlighting Crescent's unique value proposition (e.g., "Unlike co-ed institutions, we focus specifically on...") should be drafted to handle comparison queries without a hard deflection.
*   **Unified Data Sheets:** Student count and ratio information should be consolidated into a single "Fast Facts" document to prevent retrieval inconsistencies seen in Interactions 9, 17, 19, and 20.

## 4. Recommendations
### Chatbot System Improvements
*   **Resolve Retrieval Inconsistency:** Investigate why Interactions 9 and 17 failed while 19 and 20 succeeded. The embedding or search indexing likely needs tuning to ensure consistent access to static data points (ratios, counts) regardless of phrasing.
*   **Refine Fallback Responses:** Replace generic responses like *"I specialize in enrollment information. Could you please rephrase..."* (Interactions 13, 17, 22) with more helpful guidance. For example: *"I cannot provide comparative data on other schools, but I can tell you more about Crescent's unique focus on..."*
*   **Tour Availability Automation:** Since physical tours are full until April 2026 (Current Date: March 2026), the chatbot should proactively offer the Virtual Tour link in the *first* response regarding tours, rather than burying it in the second paragraph.

### Website & Content Updates
*   **Prominence of Virtual Tours:** Given the backlog in physical tours, ensure the "Virtual Tour" option is highlighted on the homepage and admissions landing page to capture interest immediately.
*   **FAQ Section Expansion:** Add a dedicated FAQ section for "Admissions Dates" and "School Statistics" to ensure this high-volume data is easily scrapable by the chatbot.
*   **Financial Aid Clarity:** Interaction 16 was successful, but ensure the contact list for the Enrollment Team is kept up-to-date in the knowledge base, as staff changes frequently.

---
**End of Report**