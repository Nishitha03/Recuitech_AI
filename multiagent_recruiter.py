import sqlite3
import pandas as pd
import os
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import tempfile
import PyPDF2
import docx
import time
import requests

class JobDescriptionSummarizer:
    """Agent that reads and summarizes key elements from job descriptions"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b", verbose=True):
        self.db_path = db_path
        self.ollama_model = ollama_model
        self.verbose = verbose
        self.ollama_base_url = "http://localhost:11434/api"
    
    def _ollama_query(self, prompt):
        """Send a query to the local Ollama instance with progress updates using the REST API"""
        if self.verbose:
            print(f"Sending query to Ollama model: {self.ollama_model}")
            print(f"Query type: {prompt.split('\n')[0][:60]}...")
        
        try:
            # Call Ollama's generate API
            response = requests.post(
                f"{self.ollama_base_url}/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                print(f"\nError: Ollama API returned status code {response.status_code}")
                return None
            
            result = response.json().get('response', '')
            
            if self.verbose:
                print("\nOllama query completed")
            
            return result
        except Exception as e:
            print(f"\nError querying Ollama API: {e}")
            return None
    
    def summarize_job(self, job_id):
        """Summarize a job description from the database with progress updates"""
        if self.verbose:
            print(f"\n--- Processing Job ID: {job_id} ---")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get job description
        cursor.execute("SELECT job_title, description FROM job_descriptions WHERE id = ?", (job_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Job with ID {job_id} not found")
            conn.close()
            return False
        
        job_title, description = result
        
        if self.verbose:
            print(f"Job Title: {job_title}")
            print(f"Description Length: {len(description)} characters")
        
        # Create prompts for different sections
        prompt_summary = f"""You are a recruiting expert. Given the following job description for a {job_title} position, provide a concise summary of the role (max 3 sentences):

{description}

Summary:"""

        prompt_skills = f"""You are a recruiting expert. Given the following job description for a {job_title} position, extract only the required skills as a comma-separated list:

{description}

Required Skills:"""

        prompt_experience = f"""You are a recruiting expert. Given the following job description for a {job_title} position, extract only the required experience as a comma-separated list:

{description}

Required Experience:"""

        prompt_qualifications = f"""You are a recruiting expert. Given the following job description for a {job_title} position, extract only the required qualifications as a comma-separated list:

{description}

Required Qualifications:"""

        prompt_responsibilities = f"""You are a recruiting expert. Given the following job description for a {job_title} position, extract only the key job responsibilities as a comma-separated list:

{description}

Responsibilities:"""

        # Get responses from Ollama with progress updates
        if self.verbose:
            print("\nGenerating job summary...")
        summary = self._ollama_query(prompt_summary)
        if self.verbose:
            print(f"Summary: {summary[:100]}...")
        
        if self.verbose:
            print("\nExtracting required skills...")
        skills = self._ollama_query(prompt_skills)
        if self.verbose:
            print(f"Skills: {skills[:100]}...")
        
        if self.verbose:
            print("\nExtracting required experience...")
        experience = self._ollama_query(prompt_experience)
        if self.verbose:
            print(f"Experience: {experience[:100]}...")
        
        if self.verbose:
            print("\nExtracting required qualifications...")
        qualifications = self._ollama_query(prompt_qualifications)
        if self.verbose:
            print(f"Qualifications: {qualifications[:100]}...")
        
        if self.verbose:
            print("\nExtracting job responsibilities...")
        responsibilities = self._ollama_query(prompt_responsibilities)
        if self.verbose:
            print(f"Responsibilities: {responsibilities[:100]}...")
        
        # Update the database
        if self.verbose:
            print("\nUpdating database with extracted information...")
            
        cursor.execute("""
        UPDATE job_descriptions 
        SET summary = ?, required_skills = ?, required_experience = ?, 
            required_qualifications = ?, responsibilities = ?
        WHERE id = ?
        """, (summary, skills, experience, qualifications, responsibilities, job_id))
        
        conn.commit()
        conn.close()
        
        if self.verbose:
            print(f"Job ID {job_id} successfully processed and updated")
        
        return True
    
    def summarize_all_jobs(self):
        """Summarize all unsummarized job descriptions in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all unsummarized job descriptions
        cursor.execute("SELECT id FROM job_descriptions WHERE summary IS NULL")
        job_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if self.verbose:
            print(f"Found {len(job_ids)} job descriptions to summarize")
        
        for i, job_id in enumerate(job_ids):
            if self.verbose:
                print(f"\nProcessing job {i+1} of {len(job_ids)} (ID: {job_id})...")
            self.summarize_job(job_id)
            time.sleep(1)  # Prevent overwhelming Ollama
        
        if self.verbose:
            print(f"\nCompleted summarizing {len(job_ids)} job descriptions")


class ResumeProcessor:
    """Agent that extracts key data from candidate resumes"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="llama3"):
        self.db_path = db_path
        self.ollama_model = ollama_model
        self.ollama_base_url = "http://localhost:11434/api"
    
    def _ollama_query(self, prompt):
        """Send a query to the local Ollama instance using the REST API"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                print(f"Error: Ollama API returned status code {response.status_code}")
                return None
            
            return response.json().get('response', '')
        except Exception as e:
            print(f"Error querying Ollama API: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return text
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from a DOCX file"""
        text = ""
        try:
            doc = docx.Document(docx_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
        return text
    
    def extract_resume_text(self, file_path):
        """Extract text from a resume file (PDF or DOCX)"""
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            print(f"Unsupported file format: {file_path}")
            return ""
    
    def extract_candidate_info(self, resume_text):
        """Extract candidate information from resume text using Ollama"""
        # Create a JSON extraction prompt
        prompt = f"""You are a recruiting expert. Extract the following information from this resume text as JSON with the keys: name, email, phone, skills (comma-separated), experience (comma-separated work history), education (comma-separated), certifications (comma-separated).

Resume text:
{resume_text[:5000]}  # Limiting to prevent context length issues

Return only valid JSON without explanations:"""

        # Get response from Ollama
        response = self._ollama_query(prompt)
        
        try:
            # Extract JSON from the response (handling potential non-JSON text around it)
            json_match = re.search(r'({[\s\S]*})', response)
            if json_match:
                candidate_info = json.loads(json_match.group(1))
                return candidate_info
            else:
                print("Failed to extract JSON from Ollama response")
                return {}
        except json.JSONDecodeError:
            print("Invalid JSON response from Ollama")
            return {}
    
    def process_resume(self, file_path, candidate_name=None, candidate_email=None):
        """Process a resume file and store candidate information in the database"""
        # Extract text from resume
        resume_text = self.extract_resume_text(file_path)
        if not resume_text:
            print(f"Failed to extract text from resume: {file_path}")
            return None
        
        # Extract candidate information
        candidate_info = self.extract_candidate_info(resume_text)
        
        # Override with provided info if available
        if candidate_name:
            candidate_info['name'] = candidate_name
        if candidate_email:
            candidate_info['email'] = candidate_email
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO candidates (name, email, phone, resume_text, skills, experience, education, certifications)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_info.get('name', ''),
            candidate_info.get('email', ''),
            candidate_info.get('phone', ''),
            resume_text,
            candidate_info.get('skills', ''),
            candidate_info.get('experience', ''),
            candidate_info.get('education', ''),
            candidate_info.get('certifications', '')
        ))
        
        candidate_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return candidate_id


class CandidateMatcher:
    """Agent that matches candidates to job descriptions"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="llama3", threshold=0.8, max_shortlisted=2):
        self.db_path = db_path
        self.ollama_model = ollama_model
        self.threshold = threshold
        self.max_shortlisted = max_shortlisted  # Limit to 1-2 job matches
        self.ollama_base_url = "http://localhost:11434/api"
    
    def _ollama_query(self, prompt):
        """Send a query to the local Ollama instance using the REST API"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                print(f"Error: Ollama API returned status code {response.status_code}")
                return None
            
            return response.json().get('response', '')
        except Exception as e:
            print(f"Error querying Ollama API: {e}")
            return None
    
    def match_candidate_to_job(self, candidate_id, job_id):
        """Calculate a match score between a candidate and a job with explanation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get candidate info
        cursor.execute("""
        SELECT name, skills, experience, education, certifications
        FROM candidates WHERE id = ?
        """, (candidate_id,))
        candidate = cursor.fetchone()
        
        if not candidate:
            print(f"Candidate with ID {candidate_id} not found")
            conn.close()
            return None, None
        
        # Get job info
        cursor.execute("""
        SELECT job_title, required_skills, required_experience, required_qualifications, responsibilities
        FROM job_descriptions WHERE id = ?
        """, (job_id,))
        job = cursor.fetchone()
        
        if not job:
            print(f"Job with ID {job_id} not found")
            conn.close()
            return None, None
        
        candidate_name, candidate_skills, candidate_experience, candidate_education, candidate_certifications = candidate
        job_title, required_skills, required_experience, required_qualifications, responsibilities = job
        
        # Create matching prompt with request for reasoning
        prompt = f"""You are a recruiting expert. Analyze how well this candidate matches the job requirements.

Job Position: {job_title}
Required Skills: {required_skills}
Required Experience: {required_experience}
Required Qualifications: {required_qualifications}
Job Responsibilities: {responsibilities}

Candidate Information:
Name: {candidate_name}
Skills: {candidate_skills}
Experience: {candidate_experience}
Education: {candidate_education}
Certifications: {candidate_certifications}

First, calculate a match percentage score (0.0-1.0) representing how well the candidate matches the job requirements.

Then, provide a brief explanation (2-3 sentences) of WHY this candidate is a good fit for the position, focused on their strongest matching qualifications.

Format your response exactly as follows:
SCORE: [decimal number between 0.0-1.0]
REASONING: [2-3 sentence explanation of why they are a good match]
"""

        # Get match score and reasoning from Ollama
        response = self._ollama_query(prompt)
        
        # Extract score and reasoning
        match_score = 0.0
        match_reasoning = ""
        
        score_match = re.search(r'SCORE:\s*([0-9]*[.]?[0-9]+)', response)
        if score_match:
            try:
                match_score = float(score_match.group(1))
                # Ensure score is between 0 and 1
                match_score = max(0.0, min(1.0, match_score))
            except ValueError:
                print("Invalid match score format from Ollama")
                match_score = 0.0
        
        reasoning_match = re.search(r'REASONING:\s*(.*?)(?=$|\n\n)', response, re.DOTALL)
        if reasoning_match:
            match_reasoning = reasoning_match.group(1).strip()
        else:
            # Fallback if REASONING tag isn't found
            match_reasoning = response.replace(f"SCORE: {match_score}", "").strip()
        
        # Store match in database (without modifying schema)
        cursor.execute("""
        INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
        VALUES (?, ?, ?, ?)
        """, (job_id, candidate_id, match_score, 0))  # Default to not shortlisted
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return match_score, match_reasoning, match_id
    
    def match_candidate_to_all_jobs(self, candidate_id):
        """Match a candidate against all jobs and select top matches for shortlisting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all job IDs
        cursor.execute("SELECT id FROM job_descriptions")
        job_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Matching candidate {candidate_id} against {len(job_ids)} jobs...")
        
        # Calculate matches for all jobs
        results = []
        for job_id in job_ids:
            match_score, match_reasoning, match_id = self.match_candidate_to_job(candidate_id, job_id)
            if match_score is not None:
                results.append((job_id, match_score, match_reasoning, match_id))
            time.sleep(1)  # Prevent overwhelming Ollama
        
        # Sort by match score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Select only top matches that meet threshold for shortlisting
        shortlisted_count = 0
        shortlisted_jobs = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n========== CANDIDATE MATCH RESULTS ==========")
        print(f"Top matches for candidate {candidate_id}:")
        
        for job_id, match_score, match_reasoning, match_id in results:
            # Get job title for display
            cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
            job_title = cursor.fetchone()[0]
            
            if match_score >= self.threshold and shortlisted_count < self.max_shortlisted:
                # Update this match as shortlisted
                cursor.execute("""
                UPDATE matches SET is_shortlisted = 1 WHERE id = ?
                """, (match_id,))
                
                shortlisted_count += 1
                shortlisted_jobs.append((job_id, match_score, match_reasoning))
                
                print(f"\n✓ SHORTLISTED: {job_title}")
                print(f"  Score: {match_score:.2f}")
                print(f"  Why this is a good match: {match_reasoning}")
            else:
                # Show other matches but indicate they're not shortlisted
                print(f"\n☒ NOT SHORTLISTED: {job_title}")
                print(f"  Score: {match_score:.2f}")
                if match_score >= self.threshold:
                    print("  (Not in top matches despite good score)")
        
        print("\n==============================================")
        print(f"Candidate shortlisted for {shortlisted_count} positions out of {len(results)} total jobs")
        print("==============================================")
        
        conn.commit()
        conn.close()
        
        return shortlisted_jobs
    
    def get_shortlisted_candidates(self):
        """Get all shortlisted candidates who haven't been scheduled for interviews"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT m.id, m.job_id, m.candidate_id, m.match_score, j.job_title, c.name, c.email
        FROM matches m
        JOIN job_descriptions j ON m.job_id = j.id
        JOIN candidates c ON m.candidate_id = c.id
        WHERE m.is_shortlisted = 1 AND m.interview_scheduled = 0
        """)
        
        shortlisted = cursor.fetchall()
        conn.close()
        
        return shortlisted


class InterviewScheduler:
    """Agent that schedules interviews with shortlisted candidates"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="llama3",
                 smtp_server=None, smtp_port=587, smtp_username=None, smtp_password=None):
        self.db_path = db_path
        self.ollama_model = ollama_model
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.ollama_base_url = "http://localhost:11434/api"
    
    def _ollama_query(self, prompt):
        """Send a query to the local Ollama instance using the REST API"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                print(f"Error: Ollama API returned status code {response.status_code}")
                return None
            
            return response.json().get('response', '')
        except Exception as e:
            print(f"Error querying Ollama API: {e}")
            return None
    
    def generate_interview_times(self, num_slots=3, start_days_from_now=2, business_hours_only=True, 
                                custom_dates=None, custom_times=None):
        """Generate potential interview time slots
        
        Args:
            num_slots: Number of time slots to generate if custom dates/times not provided
            start_days_from_now: Number of days from now to start scheduling (default 2)
            business_hours_only: If True, only schedule on weekdays
            custom_dates: List of specific dates in format 'YYYY-MM-DD'
            custom_times: List of specific times in format 'HH:MM' (24-hour format)
            
        Returns:
            List of datetime objects representing interview slots
        """
        # If custom dates and times are provided, use those
        if custom_dates and custom_times:
            slots = []
            for date_str in custom_dates:
                for time_str in custom_times:
                    try:
                        # Parse date and time strings
                        year, month, day = map(int, date_str.split('-'))
                        hour, minute = map(int, time_str.split(':'))
                        
                        # Create datetime object
                        slot = datetime(year, month, day, hour, minute, 0)
                        slots.append(slot)
                        
                        # Limit to requested number of slots
                        if len(slots) >= num_slots:
                            break
                    except ValueError as e:
                        print(f"Error parsing date/time: {e}")
                        continue
                        
                if len(slots) >= num_slots:
                    break
            
            # If we couldn't create any valid slots from custom dates/times, fall back to automatic
            if not slots:
                print("Invalid custom dates/times provided. Falling back to automatic scheduling.")
                return self._generate_automatic_interview_times(num_slots, start_days_from_now, business_hours_only)
            
            return slots
        else:
            # Fall back to automatic scheduling
            return self._generate_automatic_interview_times(num_slots, start_days_from_now, business_hours_only)
    
    def _generate_automatic_interview_times(self, num_slots=3, start_days_from_now=2, business_hours_only=True):
        """Generate automatic interview time slots based on parameters"""
        current_time = datetime.now()
        slots = []
        
        # Start from 2 business days from now
        day_pointer = current_time + timedelta(days=start_days_from_now)
        
        while len(slots) < num_slots:
            # Skip weekends if business_hours_only is True
            if business_hours_only and day_pointer.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                day_pointer += timedelta(days=1)
                continue
            
            # Add morning and afternoon slots
            morning_slot = datetime(
                day_pointer.year, day_pointer.month, day_pointer.day, 10, 0, 0
            )
            afternoon_slot = datetime(
                day_pointer.year, day_pointer.month, day_pointer.day, 14, 0, 0
            )
            
            if len(slots) < num_slots:
                slots.append(morning_slot)
            
            if len(slots) < num_slots:
                slots.append(afternoon_slot)
            
            # Move to next day
            day_pointer += timedelta(days=1)
        
        return slots
    
    def generate_email_content(self, candidate_name, job_title, interview_times):
        """Generate personalized email content for interview invitation"""
        time_str = "\n".join([time.strftime("%A, %B %d at %I:%M %p") for time in interview_times])
        
        prompt = f"""You are a recruiting expert. Create a professional email inviting {candidate_name} for an interview for the {job_title} position. Include the following time slots as options:

{time_str}

The email should be professional but friendly, congratulate them on being shortlisted, and ask them to reply with their preferred time slot. Keep it concise. Include a subject line for the email.

Format the response as:
SUBJECT: [Subject goes here]

[Email body goes here]"""

        # Get email content from Ollama
        response = self._ollama_query(prompt)
        
        # Extract subject and body
        parts = response.split("\n", 1)
        if len(parts) >= 2 and parts[0].startswith("SUBJECT:"):
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
            return subject, body
        else:
            # Default if parsing fails
            subject = f"Interview Invitation: {job_title} Position"
            body = response
            return subject, body
    
    def send_email(self, recipient_email, subject, body, sender_name="Recruitment Team"):
        """Send an email to a candidate"""
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            print("SMTP configuration not provided. Email would be sent to:", recipient_email)
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{sender_name} <{self.smtp_username}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def schedule_interview(self, match_id, custom_dates=None, custom_times=None):
        """Schedule an interview for a shortlisted candidate
        
        Args:
            match_id: ID of the match to schedule an interview for
            custom_dates: List of specific dates in format 'YYYY-MM-DD'
            custom_times: List of specific times in format 'HH:MM' (24-hour format)
            
        Returns:
            Boolean indicating success
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get match information
        cursor.execute("""
        SELECT m.job_id, m.candidate_id, j.job_title, c.name, c.email
        FROM matches m
        JOIN job_descriptions j ON m.job_id = j.id
        JOIN candidates c ON m.candidate_id = c.id
        WHERE m.id = ?
        """, (match_id,))
        
        result = cursor.fetchone()
        if not result:
            print(f"Match with ID {match_id} not found")
            conn.close()
            return False
        
        job_id, candidate_id, job_title, candidate_name, candidate_email = result
        
        # Generate interview time slots (using custom dates/times if provided)
        interview_times = self.generate_interview_times(
            custom_dates=custom_dates, 
            custom_times=custom_times
        )
        
        # Log the interview times for debugging
        print(f"Interview times for {candidate_name}:")
        for idx, time_slot in enumerate(interview_times, 1):
            print(f"  {idx}. {time_slot.strftime('%A, %B %d, %Y at %I:%M %p')}")
        
        # Generate email content
        subject, body = self.generate_email_content(candidate_name, job_title, interview_times)
        
        # Send email
        if self.send_email(candidate_email, subject, body):
            # Update database
            interview_date_str = interview_times[0].strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            UPDATE matches
            SET interview_scheduled = 1, interview_date = ?
            WHERE id = ?
            """, (interview_date_str, match_id))
            
            conn.commit()
            conn.close()
            
            print(f"Interview scheduled with {candidate_name} for {job_title}")
            return True
        else:
            conn.close()
            return False
    
    def schedule_all_pending_interviews(self, custom_dates=None, custom_times=None):
        """Schedule interviews for all shortlisted candidates without interviews
        
        Args:
            custom_dates: List of specific dates in format 'YYYY-MM-DD'
            custom_times: List of specific times in format 'HH:MM' (24-hour format)
            
        Returns:
            Number of interviews scheduled
        """
        matcher = CandidateMatcher(self.db_path)
        shortlisted = matcher.get_shortlisted_candidates()
        
        for match_id, _, _, _, _, _, _ in shortlisted:
            self.schedule_interview(match_id, custom_dates, custom_times)
            time.sleep(1)  # Prevent overwhelming email server
        
        return len(shortlisted)


class RecruitmentSystem:
    """Main class that orchestrates the multi-agent recruitment system"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="llama3", 
                 smtp_server=None, smtp_port=587, smtp_username=None, smtp_password=None,
                 match_threshold=0.8, max_shortlisted=2):
        self.db_path = db_path
        self.ollama_model = ollama_model
        
        # Initialize agents
        self.summarizer = JobDescriptionSummarizer(db_path, ollama_model)
        self.processor = ResumeProcessor(db_path, ollama_model)
        self.matcher = CandidateMatcher(db_path, ollama_model, match_threshold, max_shortlisted)
        self.scheduler = InterviewScheduler(
            db_path, ollama_model, smtp_server, smtp_port, smtp_username, smtp_password
        )
    
    def process_new_resume(self, resume_path, candidate_name=None, candidate_email=None):
        """Process a new resume and potentially schedule an interview"""
        print(f"Processing resume: {resume_path}")
        
        # Ensure all jobs are summarized
        self.summarizer.summarize_all_jobs()
        
        # Process the resume
        candidate_id = self.processor.process_resume(resume_path, candidate_name, candidate_email)
        if not candidate_id:
            print("Failed to process resume")
            return False
        
        print(f"Candidate added with ID {candidate_id}")
        
        # Match against all jobs with limited shortlisting
        # The matcher will now show match reasoning on screen and limit to top matches
        shortlisted_jobs = self.matcher.match_candidate_to_all_jobs(candidate_id)
        
        # Schedule interviews if shortlisted
        if shortlisted_jobs:
            print("\nScheduling interviews for shortlisted positions...")
            num_scheduled = self.scheduler.schedule_all_pending_interviews()
            print(f"Scheduled {num_scheduled} interviews")
        else:
            print("Candidate was not shortlisted for any position")
        
        return True

# Usage example
if __name__ == "__main__":
    # Configure system with only 2 max shortlisted positions
    system = RecruitmentSystem(
        ollama_model="gemma3:1b",
        smtp_server="smtp.gmail.com",
        smtp_username="your_email@gmail.com",
        smtp_password="your_app_password",
        match_threshold=0.75,  # Lower threshold slightly to find good matches
        max_shortlisted=2      # Limit to 2 max shortlisted positions
    )
    
    # Example usage
    # system.process_new_resume("path/to/resume.pdf", "John Doe", "john@example.com")