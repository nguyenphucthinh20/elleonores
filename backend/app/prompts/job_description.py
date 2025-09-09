def extract_jd(text: str) -> str:
    prompt = f"""
Extract the following information from this job description text. 
Format the response as a valid JSON object with these fields:
- title: The job title
- company: The company name (use "Unknown" if not found)
- location: The job location (use "Not specified" if not found)
- required_qualifications: An array of strings, each one representing a required qualification
- preferred_qualifications: An array of strings, each one representing a preferred/nice-to-have qualification
- description: A summary of the job description
- experience_level: The experience level (entry-level, mid-level, senior, etc.)
- employment_type: The employment type (full-time, part-time, contract, etc.)

Job Description Text:
{text}
"""
    return prompt