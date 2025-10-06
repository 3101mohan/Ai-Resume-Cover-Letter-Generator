# src/prompts.py
# Prompt templates for Gemini API

RESUME_PROMPT_TEMPLATE = """
You are an expert ATS (Applicant Tracking System) writer. Your task is to analyze the Candidate Info against the Job Description and generate a highly-optimized resume.

You MUST return your entire response as a single JSON object.

JSON Schema:
{{
  "ats_score": "[Score out of 100, based on keyword matching and relevance]",
  "keywords": "[A list of 5-8 relevant keywords extracted from the Job Description that were incorporated into the resume]",
  "resume_text": "[The full, professionally rewritten, ATS-friendly resume text, using clear headings: Name, Contact, Professional Summary, Skills, Experience, Education. Use strong action verbs and bullet points for achievements.]"
}}

Candidate Info:
Name: {name}
Contact: {contact}
Professional Summary: {summary}
Skills: {skills}
Experience: {experience}
Education: {education}

Job Description:
{job_description}
"""

COVER_LETTER_PROMPT_TEMPLATE = """
You are a professional cover letter writer. Write a tailored cover letter using the candidate’s info and the job description.
Structure: Header, Salutation, Opening, 1-2 body paragraphs aligning skills with JD, Closing, Signature.
Length: 200–400 words.

Candidate Info:
Name: {name}
Contact: {contact}
Summary: {summary}
Skills: {skills}
Experience: {experience}
Education: {education}

Job Description:
{job_description}
"""
