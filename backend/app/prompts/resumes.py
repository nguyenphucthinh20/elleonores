def extract_resume(cv: str) -> str:
    prompt = f"""
You are an expert recruiter specializing in job matching.

Your task is to extract structured information from a candidate's resume.

The input will be the resume text provided below, which is written in Japanese:

---
{cv}
---

You must extract the following fields:

0. **full_name**: The candidate's full name as written in the resume. Prefer the name near headers or labels such as 「氏名」, 「名前」, 「フルネーム」, or at the top of the document. Do not invent or infer from email/username. If the name is not explicitly stated, use "Unknown".

1. **experience**: A list of job experiences, each including:
   - company: Company name.
   - position: Job title.
   - duration: Time period of employment.
   - description: Brief description of key responsibilities or achievements.
2. **education**: A list of educational qualifications, each including:
   - school: Institution name.
   - major: Field of study.
   - degree: Degree obtained.
   - duration: Time period of study.
3. **technical_skills**:
   - programming_languages: List of programming languages the candidate is proficient in (e.g., Python, Java).
   - frameworks: List of tools or frameworks the candidate has experience with (e.g., React, Django, TensorFlow).
   - skills: Other general technical skills (e.g., Data Engineering, Machine Learning).
4. **key_accomplishments**: Summarize 1–3 major achievements in the candidate’s career.

**Important Guidelines:**
- The input CV is written in Japanese. You must understand and process the Japanese text accurately.
- Return the information strictly in **valid JSON format only**, with no introductory text, explanations, or Markdown formatting.
- Do NOT include phrases like "Here's the structured information..." or wrap the JSON in triple backticks.
- If a field is missing or not mentioned, use the string "Unknown" instead of null.
- If a field is missing or not mentioned, use null or an empty array [].
- Do not fabricate or infer information not explicitly stated in the resume.
- Only extract what is actually mentioned.
- Maintain the field names exactly as specified.
- Output should still be in English, but based on Japanese content.

"""
    return prompt