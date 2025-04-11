# # #!/usr/bin/env python3
# # import argparse
# # import os
# # import sys
# # import sqlite3
# # import json
# # import re
# # import requests
# # import tempfile
# # from datetime import datetime
# # import shutil
# # import time

# # # Ensure we can import from the current directory
# # sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
# # from db_setup import setup_database, import_jobs_from_csv

# # class ConversationalRecruitmentSystem:
# #     """A conversational interface for the recruitment system that maintains context"""
    
# #     def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
# #         self.db_path = db_path
# #         self.ollama_model = ollama_model
# #         self.ollama_base_url = "http://localhost:11434/api"
        
# #         # Load config
# #         self.config = self.load_config()
        
# #         # Initialize underlying recruitment system
# #         self.system = RecruitmentSystem(
# #             db_path=db_path,
# #             ollama_model=self.config.get('ollama_model', ollama_model),
# #             smtp_server=self.config.get('smtp_server'),
# #             smtp_port=self.config.get('smtp_port', 587),
# #             smtp_username=self.config.get('smtp_username'),
# #             smtp_password=self.config.get('smtp_password'),
# #             match_threshold=self.config.get('match_threshold', 0.75),
# #             max_shortlisted=self.config.get('max_shortlisted', 2)
# #         )
        
# #         # Session state to maintain context
# #         self.session = {
# #             'current_candidate': None,  # Current candidate being discussed
# #             'current_resume': None,     # Path to the current resume
# #             'analyzed_jobs': [],        # Jobs that have been analyzed
# #             'shortlisted_jobs': [],     # Jobs that were shortlisted
# #             'scheduled_interviews': []  # Interviews that have been scheduled
# #         }
        
# #         # Conversation history
# #         self.conversation_history = []
        
# #         # File upload directory for resumes
# #         self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
# #         os.makedirs(self.uploads_dir, exist_ok=True)
    
# #     def load_config(self):
# #         """Load configuration from config.json if it exists"""
# #         config = {
# #             'ollama_model': 'gemma2:2b',
# #             'smtp_server': None,
# #             'smtp_port': 587,
# #             'smtp_username': None,
# #             'smtp_password': None,
# #             'match_threshold': 0.75,
# #             'max_shortlisted': 2
# #         }
        
# #         if os.path.exists('config.json'):
# #             try:
# #                 with open('config.json', 'r') as f:
# #                     stored_config = json.load(f)
# #                     config.update(stored_config)
# #             except Exception as e:
# #                 print(f"Error loading config: {e}")
        
# #         return config
    
# #     def save_config(self):
# #         """Save configuration to config.json"""
# #         try:
# #             with open('config.json', 'w') as f:
# #                 json.dump(self.config, f, indent=2)
# #             return "Configuration saved successfully."
# #         except Exception as e:
# #             return f"Error saving configuration: {e}"
    
# #     def add_to_history(self, speaker, message):
# #         """Add a message to the conversation history"""
# #         self.conversation_history.append({
# #             'speaker': speaker,
# #             'message': message,
# #             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #         })
    
# #     def _ollama_query(self, prompt):
# #         """Use the Ollama model to generate responses"""
# #         try:
# #             response = requests.post(
# #                 f"{self.ollama_base_url}/generate",
# #                 json={
# #                     "model": self.config.get('ollama_model', self.ollama_model),
# #                     "prompt": prompt,
# #                     "stream": False
# #                 }
# #             )
            
# #             if response.status_code != 200:
# #                 return f"Error: Ollama API returned status code {response.status_code}"
            
# #             return response.json().get('response', '')
# #         except Exception as e:
# #             return f"Error connecting to Ollama: {e}"
    
# #     def get_candidate_info(self, candidate_id):
# #         """Get candidate information from the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, name, email, phone, skills, experience, education, certifications
# #         FROM candidates
# #         WHERE id = ?
# #         """, (candidate_id,))
        
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         if not result:
# #             return None
        
# #         return {
# #             'id': result[0],
# #             'name': result[1],
# #             'email': result[2],
# #             'phone': result[3],
# #             'skills': result[4],
# #             'experience': result[5],
# #             'education': result[6],
# #             'certifications': result[7]
# #         }
    
# #     def get_job_info(self, job_id):
# #         """Get job information from the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, job_title, summary, required_skills, required_experience, 
# #                required_qualifications, responsibilities
# #         FROM job_descriptions
# #         WHERE id = ?
# #         """, (job_id,))
        
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         if not result:
# #             return None
        
# #         return {
# #             'id': result[0],
# #             'job_title': result[1],
# #             'summary': result[2],
# #             'required_skills': result[3],
# #             'required_experience': result[4],
# #             'required_qualifications': result[5],
# #             'responsibilities': result[6]
# #         }
    
# #     def list_candidates(self):
# #         """Get a list of all candidates in the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, name, email
# #         FROM candidates
# #         ORDER BY id
# #         """)
        
# #         results = cursor.fetchall()
# #         conn.close()
        
# #         candidates = []
# #         for result in results:
# #             candidates.append({
# #                 'id': result[0],
# #                 'name': result[1],
# #                 'email': result[2]
# #             })
        
# #         return candidates
    
# #     def list_jobs(self):
# #         """Get a list of all jobs in the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, job_title, summary
# #         FROM job_descriptions
# #         ORDER BY id
# #         """)
        
# #         results = cursor.fetchall()
# #         conn.close()
        
# #         jobs = []
# #         for result in results:
# #             jobs.append({
# #                 'id': result[0],
# #                 'job_title': result[1],
# #                 'summary': result[2]
# #             })
        
# #         return jobs
    
# #     def save_uploaded_resume(self, resume_path):
# #         """Save an uploaded resume to the uploads directory"""
# #         if not os.path.exists(resume_path):
# #             return None
        
# #         # Create a unique filename based on timestamp
# #         filename = f"resume_{int(time.time())}_{os.path.basename(resume_path)}"
# #         destination = os.path.join(self.uploads_dir, filename)
        
# #         try:
# #             shutil.copy2(resume_path, destination)
# #             return destination
# #         except Exception as e:
# #             print(f"Error saving resume: {e}")
# #             return None
    
# #     def process_resume(self, resume_path, candidate_name=None, candidate_email=None):
# #         """Process a resume file with detailed output"""
# #         # Save the resume if it's not already in our uploads directory
# #         if not resume_path.startswith(self.uploads_dir):
# #             saved_path = self.save_uploaded_resume(resume_path)
# #             if saved_path:
# #                 resume_path = saved_path
# #             else:
# #                 return "Error: Could not access the resume file."
        
# #         # Process the resume
# #         processor = self.system.processor
# #         processor.verbose = True  # Enable verbose output
        
# #         result = []
# #         result.append(f"Processing resume: {os.path.basename(resume_path)}")
        
# #         # Extract text from resume
# #         resume_text = processor.extract_resume_text(resume_path)
# #         if not resume_text:
# #             result.append("Failed to extract text from the resume.")
# #             return "\n".join(result)
        
# #         result.append(f"Extracted {len(resume_text)} characters of text.")
# #         result.append(f"Text sample: {resume_text[:150]}...")
        
# #         # Extract candidate information
# #         result.append("\nAnalyzing resume content...")
# #         candidate_info = processor.extract_candidate_info(resume_text)
        
# #         # Override with provided info if available
# #         if candidate_name:
# #             candidate_info['name'] = candidate_name
# #         if candidate_email:
# #             candidate_info['email'] = candidate_email
        
# #         # Store in database
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         INSERT INTO candidates (name, email, phone, resume_text, skills, experience, education, certifications)
# #         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# #         """, (
# #             candidate_info.get('name', ''),
# #             candidate_info.get('email', ''),
# #             candidate_info.get('phone', ''),
# #             resume_text,
# #             candidate_info.get('skills', ''),
# #             candidate_info.get('experience', ''),
# #             candidate_info.get('education', ''),
# #             candidate_info.get('certifications', '')
# #         ))
        
# #         candidate_id = cursor.lastrowid
# #         conn.commit()
# #         conn.close()
        
# #         # Update session with current candidate
# #         self.session['current_candidate'] = candidate_id
# #         self.session['current_resume'] = resume_path
        
# #         # Get a clean version of the candidate name for display
# #         candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
# #         result.append(f"\nSuccessfully processed resume for {candidate_name}.")
# #         result.append(f"Candidate added to database with ID: {candidate_id}")
        
# #         # Display extracted information
# #         result.append("\nExtracted Information:")
# #         result.append(f"Name: {candidate_info.get('name', 'Not detected')}")
# #         result.append(f"Email: {candidate_info.get('email', 'Not detected')}")
# #         result.append(f"Phone: {candidate_info.get('phone', 'Not detected')}")
        
# #         if 'skills' in candidate_info and candidate_info['skills']:
# #             result.append(f"\nSkills: {candidate_info['skills']}")
        
# #         if 'experience' in candidate_info and candidate_info['experience']:
# #             result.append(f"\nExperience: {candidate_info['experience']}")
        
# #         if 'education' in candidate_info and candidate_info['education']:
# #             result.append(f"\nEducation: {candidate_info['education']}")
        
# #         if 'certifications' in candidate_info and candidate_info['certifications']:
# #             result.append(f"\nCertifications: {candidate_info['certifications']}")
        
# #         result.append("\nYou can now analyze this candidate against available jobs by asking questions like:")
# #         result.append("- \"Find suitable jobs for this candidate\"")
# #         result.append("- \"Match this candidate with our open positions\"")
# #         result.append("- \"What roles would be a good fit?\"")
        
# #         return "\n".join(result)
    
# #     def analyze_candidate(self, candidate_id=None):
# #         """Match a candidate against available jobs"""
# #         # Use the current candidate if none specified
# #         if candidate_id is None:
# #             candidate_id = self.session.get('current_candidate')
# #             if not candidate_id:
# #                 return "No candidate is currently selected. Please process a resume first or specify a candidate ID."
        
# #         # Get candidate information
# #         candidate = self.get_candidate_info(candidate_id)
# #         if not candidate:
# #             return f"No candidate found with ID {candidate_id}."
        
# #         result = []
# #         result.append(f"Analyzing matches for {candidate['name']} (ID: {candidate_id})...")
        
# #         # Match against all jobs
# #         matcher = self.system.matcher
# #         shortlisted_jobs = matcher.match_candidate_to_all_jobs(candidate_id)
        
# #         # Store in session
# #         self.session['analyzed_jobs'] = [job_id for job_id, _, _ in shortlisted_jobs]
# #         self.session['shortlisted_jobs'] = shortlisted_jobs
        
# #         result.append(f"\nAnalysis complete. {candidate['name']} was shortlisted for {len(shortlisted_jobs)} positions.")
        
# #         if shortlisted_jobs:
# #             result.append("\nYou can now schedule interviews for these positions by saying:")
# #             result.append("- \"Schedule interviews for these positions\"")
# #             result.append("- \"Send interview invitations\"")
# #             result.append("- \"Set up interviews for the shortlisted jobs\"")
# #         else:
# #             result.append("\nThe candidate wasn't shortlisted for any positions. You might want to:")
# #             result.append("- Process another resume")
# #             result.append("- Adjust the matching threshold (currently set to {:.0f}%)".format(matcher.threshold * 100))
        
# #         return "\n".join(result)
    
# #     def schedule_interviews(self):
# #         """Schedule interviews for shortlisted positions"""
# #         # Check if we have a current candidate and shortlisted jobs
# #         candidate_id = self.session.get('current_candidate')
# #         shortlisted_jobs = self.session.get('shortlisted_jobs', [])
        
# #         if not candidate_id:
# #             return "No candidate is currently selected. Please process a resume first."
        
# #         if not shortlisted_jobs:
# #             return "No positions have been shortlisted. Please analyze the candidate first."
        
# #         # Get candidate information
# #         candidate = self.get_candidate_info(candidate_id)
# #         if not candidate:
# #             return "The selected candidate could not be found in the database."
        
# #         result = []
# #         result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
        
# #         # Schedule interviews
# #         scheduler = self.system.scheduler
# #         num_scheduled = scheduler.schedule_all_pending_interviews()
        
# #         # Store in session
# #         self.session['scheduled_interviews'] = shortlisted_jobs
        
# #         if num_scheduled > 0:
# #             result.append(f"\nSuccessfully scheduled {num_scheduled} interviews for {candidate['name']}.")
# #             result.append("\nInterview invitations have been sent (or would be sent if email is configured).")
# #             result.append("\nThe following positions were included:")
            
# #             for job_id, _, _ in shortlisted_jobs:
# #                 job = self.get_job_info(job_id)
# #                 if job:
# #                     result.append(f"- {job['job_title']}")
            
# #             result.append("\nWhat would you like to do next?")
# #             result.append("- \"Process another resume\"")
# #             result.append("- \"Show me all candidates\"")
# #             result.append("- \"Show me all scheduled interviews\"")
# #         else:
# #             result.append("\nNo interviews were scheduled. This could be because:")
# #             result.append("- The interviews were already scheduled previously")
# #             result.append("- There was an issue with the email configuration")
# #             result.append("- The candidate wasn't actually shortlisted for any positions")
        
# #         return "\n".join(result)
    
# #     def get_system_status(self):
# #         """Get the current status of the recruitment system"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         # Count various metrics
# #         cursor.execute("SELECT COUNT(*) FROM job_descriptions")
# #         job_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM candidates")
# #         candidate_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
# #         shortlisted_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
# #         interview_count = cursor.fetchone()[0]
        
# #         conn.close()
        
# #         # Get current candidate context
# #         current_context = ""
# #         if self.session.get('current_candidate'):
# #             candidate = self.get_candidate_info(self.session['current_candidate'])
# #             if candidate:
# #                 current_context = f"Currently working with: {candidate['name']} (ID: {candidate['id']})"
                
# #                 if self.session.get('shortlisted_jobs'):
# #                     current_context += f"\nShortlisted for {len(self.session['shortlisted_jobs'])} positions"
                
# #                 if self.session.get('scheduled_interviews'):
# #                     current_context += f"\nInterviews scheduled for {len(self.session['scheduled_interviews'])} positions"
        
# #         # Build status message
# #         status = [
# #             "=== RECRUITMENT SYSTEM STATUS ===",
# #             f"Total Job Descriptions: {job_count}",
# #             f"Total Candidates: {candidate_count}",
# #             f"Total Shortlisted Matches: {shortlisted_count}",
# #             f"Total Scheduled Interviews: {interview_count}",
# #             "",
# #             f"Ollama Model: {self.config.get('ollama_model')}",
# #             f"Match Threshold: {self.config.get('match_threshold', 0.75) * 100:.0f}%",
# #             f"Max Shortlisted Positions: {self.config.get('max_shortlisted', 2)}",
# #             ""
# #         ]
        
# #         if current_context:
# #             status.append("--- CURRENT SESSION ---")
# #             status.append(current_context)
        
# #         return "\n".join(status)
    
# #     def process_command(self, user_input):
# #         """Process a natural language command from the user and maintain context"""
# #         # Add user input to history
# #         self.add_to_history('user', user_input)
        
# #         # Build prompt with conversation history for context
# #         conversation_context = "\n".join([
# #             f"{msg['speaker']}: {msg['message']}" 
# #             for msg in self.conversation_history[-10:]  # Include last 10 messages max
# #         ])
        
# #         # Get the current session state for context
# #         session_context = "Current session state:\n"
# #         if self.session.get('current_candidate'):
# #             candidate = self.get_candidate_info(self.session['current_candidate'])
# #             if candidate:
# #                 session_context += f"- Working with candidate: {candidate['name']} (ID: {candidate['id']})\n"
# #         if self.session.get('shortlisted_jobs'):
# #             session_context += f"- Candidate has been matched with {len(self.session['shortlisted_jobs'])} positions\n"
# #         if self.session.get('scheduled_interviews'):
# #             session_context += f"- Interviews have been scheduled for {len(self.session['scheduled_interviews'])} positions\n"
        
# #         # Build prompt for Ollama to understand intent
# #         prompt = f"""You are an AI assistant for a recruitment system. Based on the conversation history and current session state, determine what action the user wants to take.

# # {session_context}

# # Recent conversation:
# # {conversation_context}

# # User's latest message: "{user_input}"

# # Analyze this message and respond with a JSON object indicating the action to take and any parameters. Possible actions are:
# # 1. "process_resume" - Process a resume file
# # 2. "analyze_candidate" - Match a candidate with jobs
# # 3. "schedule_interviews" - Schedule interviews for shortlisted positions
# # 4. "list_candidates" - Show all candidates
# # 5. "list_jobs" - Show all jobs
# # 6. "get_candidate" - Get details for a specific candidate
# # 7. "get_job" - Get details for a specific job
# # 8. "system_status" - Show system status
# # 9. "help" - Show help information
# # 10. "unknown" - Could not determine intent

# # For "process_resume", include "resume_path", "candidate_name", and "candidate_email" if mentioned.
# # For "get_candidate" or "analyze_candidate", include "candidate_id" if mentioned.
# # For "get_job", include "job_id" if mentioned.

# # Reply with only valid JSON. Example:
# # {{"action": "process_resume", "params": {{"resume_path": "resume.pdf", "candidate_name": "John Doe", "candidate_email": "john@example.com"}}}}

# # JSON:"""

# #         # Get response from Ollama
# #         llm_response = self._ollama_query(prompt)
        
# #         try:
# #             # Extract JSON from the response
# #             json_match = re.search(r'({[\s\S]*})', llm_response)
# #             if json_match:
# #                 intent_data = json.loads(json_match.group(1))
# #                 action = intent_data.get('action', 'unknown')
# #                 params = intent_data.get('params', {})
# #             else:
# #                 action = 'unknown'
# #                 params = {}
# #         except Exception as e:
# #             print(f"Error parsing LLM response: {e}")
# #             action = 'unknown'
# #             params = {}
        
# #         # Execute the appropriate action
# #         response = ""
        
# #         if action == 'process_resume':
# #             resume_path = params.get('resume_path')
# #             if resume_path:
# #                 response = self.process_resume(
# #                     resume_path,
# #                     params.get('candidate_name'),
# #                     params.get('candidate_email')
# #                 )
# #             else:
# #                 response = "I need a resume file to process. Please specify the path to the resume."
        
# #         elif action == 'analyze_candidate':
# #             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
# #             if candidate_id:
# #                 response = self.analyze_candidate(candidate_id)
# #             else:
# #                 response = "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
# #         elif action == 'schedule_interviews':
# #             response = self.schedule_interviews()
        
# #         elif action == 'list_candidates':
# #             candidates = self.list_candidates()
# #             if candidates:
# #                 lines = ["Here are all the candidates in the system:"]
# #                 for candidate in candidates:
# #                     lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
# #                 response = "\n".join(lines)
# #             else:
# #                 response = "No candidates found in the database."
        
# #         elif action == 'list_jobs':
# #             jobs = self.list_jobs()
# #             if jobs:
# #                 lines = ["Here are all the job positions in the system:"]
# #                 for job in jobs:
# #                     lines.append(f"{job['id']}: {job['job_title']}")
# #                     if job['summary']:
# #                         summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
# #                         lines.append(f"   {summary}")
# #                 response = "\n".join(lines)
# #             else:
# #                 response = "No jobs found in the database."
        
# #         elif action == 'get_candidate':
# #             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
# #             if candidate_id:
# #                 candidate = self.get_candidate_info(candidate_id)
# #                 if candidate:
# #                     lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
# #                     lines.append(f"Email: {candidate['email']}")
# #                     lines.append(f"Phone: {candidate['phone']}")
# #                     lines.append(f"\nSkills: {candidate['skills']}")
# #                     lines.append(f"\nExperience: {candidate['experience']}")
# #                     lines.append(f"\nEducation: {candidate['education']}")
# #                     lines.append(f"\nCertifications: {candidate['certifications']}")
# #                     response = "\n".join(lines)
# #                 else:
# #                     response = f"No candidate found with ID {candidate_id}."
# #             else:
# #                 response = "Please specify a candidate ID or process a resume first."
        
# #         elif action == 'get_job':
# #             job_id = params.get('job_id')
# #             if job_id:
# #                 job = self.get_job_info(job_id)
# #                 if job:
# #                     lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
# #                     lines.append(f"\nSummary: {job['summary']}")
# #                     lines.append(f"\nRequired Skills: {job['required_skills']}")
# #                     lines.append(f"\nRequired Experience: {job['required_experience']}")
# #                     lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
# #                     lines.append(f"\nResponsibilities: {job['responsibilities']}")
# #                     response = "\n".join(lines)
# #                 else:
# #                     response = f"No job found with ID {job_id}."
# #             else:
# #                 response = "Please specify a job ID."
        
# #         elif action == 'system_status':
# #             response = self.get_system_status()
        
# #         elif action == 'help':
# #             response = """
# # I can help you with the following recruiting tasks:

# # Resume Processing:
# # - "Process resume.pdf for John Doe (john@example.com)"
# # - "Extract data from the resume in path/to/file.pdf"

# # Candidate Analysis:
# # - "Find matching jobs for this candidate"
# # - "Match this candidate with available positions"
# # - "What roles would be a good fit?"

# # Interview Scheduling:
# # - "Schedule interviews for the shortlisted positions"
# # - "Send interview invitations"
# # - "Set up interviews for these jobs"

# # Information Lookup:
# # - "Show me all candidates"
# # - "List all jobs"
# # - "Show me details for candidate 3"
# # - "Tell me about job position 5"

# # System Information:
# # - "What's the current status?"
# # - "Show system status"
# # - "Who am I working with right now?"

# # I maintain context throughout our conversation, so you can refer to "this candidate" or "these positions" and I'll understand based on our discussion.
# # """
        
# #         else:  # 'unknown' action
# #             response = "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."
        
# #         # Add response to history
# #         self.add_to_history('assistant', response)
        
# #         return response

# # def main():
# #     """Main entry point for the conversational recruitment system"""
# #     parser = argparse.ArgumentParser(description='Conversational Recruitment System')
# #     parser.add_argument('--model', default='gemma2:2b', help='Ollama model to use (default: gemma2:2b)')
# #     args = parser.parse_args()
    
# #     system = ConversationalRecruitmentSystem(ollama_model=args.model)
    
# #     print("\n============================================")
# #     print("     RECRUITMENT SYSTEM - CONVERSATION     ")
# #     print("============================================")
# #     print("I can help you process resumes, match candidates with jobs, and schedule interviews.")
# #     print("Type 'help' for more information or 'exit' to quit.")
    
# #     while True:
# #         try:
# #             user_input = input("\n> ")
            
# #             if user_input.lower() in ['exit', 'quit', 'q']:
# #                 print("Goodbye!")
# #                 break
            
# #             if user_input.strip():
# #                 response = system.process_command(user_input)
# #                 print("\n" + response)
            
# #         except KeyboardInterrupt:
# #             print("\nGoodbye!")
# #             break
# #         except Exception as e:
# #             print(f"Error: {e}")

# # if __name__ == "__main__":
# #     main()


# #!/usr/bin/env python3
# # import argparse
# # import os
# # import sys
# # import sqlite3
# # import json
# # import re
# # import requests
# # import tempfile
# # from datetime import datetime
# # import shutil
# # import time

# # # Ensure we can import from the current directory
# # sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
# # from db_setup import setup_database, import_jobs_from_csv

# # # Custom enhanced ResumeProcessor with improved extraction
# # class EnhancedResumeProcessor(ResumeProcessor):
# #     def extract_candidate_info(self, resume_text):
# #         """Extract candidate information from resume text with improved name and email detection"""
# #         # Initialize empty candidate info dictionary
# #         candidate_info = {}
        
# #         # Try regex extraction first for email
# #         email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
# #         email_match = re.search(email_pattern, resume_text)
# #         if email_match:
# #             candidate_info['email'] = email_match.group(0)
# #             print(f"Email extracted via regex: {candidate_info['email']}")

# #         # Look for phone numbers with regex
# #         phone_patterns = [
# #             r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # Standard formats
# #             r'(\+\d{1,3}[\s-]?)?\d{5,}',  # International without separators
# #         ]
# #         for pattern in phone_patterns:
# #             phone_match = re.search(pattern, resume_text)
# #             if phone_match:
# #                 candidate_info['phone'] = phone_match.group(0)
# #                 print(f"Phone extracted via regex: {candidate_info['phone']}")
# #                 break
        
# #         # Look for "Name:" pattern in resume text
# #         name_pattern = r'Name:\s*([^\n]+)'
# #         name_match = re.search(name_pattern, resume_text)
# #         if name_match:
# #             candidate_info['name'] = name_match.group(1).strip()
# #             print(f"Name extracted via regex: {candidate_info['name']}")
# #         else:
# #             # Create a focused prompt just for name extraction
# #             # This gives the LLM one specific task to focus on
# #             name_prompt = f"""You are a recruiting expert. Extract ONLY the candidate's full name from this resume text.
# #             Look at the top of the resume first, as names typically appear at the beginning.
            
# #             Resume text:
# #             {resume_text[:2000]}
            
# #             Respond with ONLY the full name without any explanation or additional text. 
# #             If you cannot determine the name with high confidence, respond with "Unknown".
# #             """
            
# #             name_response = self._ollama_query(name_prompt)
# #             if name_response and name_response.strip() != "Unknown":
# #                 candidate_info['name'] = name_response.strip()
# #                 print(f"Name extracted via focused prompt: {candidate_info['name']}")
        
# #         # Now get the rest of the information with a separate prompt
# #         # This approach splits the extraction to get better results for each part
# #         skills_prompt = f"""You are a recruiting expert. Extract information from this resume text as JSON with the following structure:
# #         {{
# #             "skills": "comma-separated list of technical and soft skills",
# #             "experience": "comma-separated work history with company names and roles",
# #             "education": "comma-separated education details including institutions and degrees",
# #             "certifications": "comma-separated list of professional certifications"
# #         }}

# #         Resume text:
# #         {resume_text[:5000]}
        
# #         Return only valid JSON. Do not include any explanation or additional text:"""
        
# #         skills_response = self._ollama_query(skills_prompt)
        
# #         try:
# #             # Extract JSON from the response (handling potential non-JSON text around it)
# #             json_match = re.search(r'({[\s\S]*})', skills_response)
# #             if json_match:
# #                 skills_info = json.loads(json_match.group(1))
# #                 # Update candidate_info with skills_info
# #                 for key, value in skills_info.items():
# #                     candidate_info[key] = value
# #             else:
# #                 print("Failed to extract JSON from Ollama response for skills")
# #         except Exception as e:
# #             print(f"Error parsing skills JSON response: {e}")
        
# #         # Log extraction summary
# #         print("Candidate information extracted:")
# #         for key, value in candidate_info.items():
# #             if key == 'experience' or key == 'education':
# #                 # Truncate long text fields for logging
# #                 value_preview = value[:100] + "..." if value and len(value) > 100 else value
# #                 print(f"- {key}: {value_preview}")
# #             else:
# #                 print(f"- {key}: {value}")
        
# #         return candidate_info

# # class ConversationalRecruitmentSystem:
# #     """A conversational interface for the recruitment system that maintains context"""
    
# #     def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
# #         self.db_path = db_path
# #         self.ollama_model = ollama_model
# #         self.ollama_base_url = "http://localhost:11434/api"
        
# #         # Load config
# #         self.config = self.load_config()
        
# #         # Initialize underlying recruitment system with custom processor
# #         self.system = RecruitmentSystem(
# #             db_path=db_path,
# #             ollama_model=self.config.get('ollama_model', ollama_model),
# #             smtp_server=self.config.get('smtp_server'),
# #             smtp_port=self.config.get('smtp_port', 587),
# #             smtp_username=self.config.get('smtp_username'),
# #             smtp_password=self.config.get('smtp_password'),
# #             match_threshold=self.config.get('match_threshold', 0.75),
# #             max_shortlisted=self.config.get('max_shortlisted', 2)
# #         )
        
# #         # Replace the default processor with our enhanced version
# #         self.system.processor = EnhancedResumeProcessor(db_path, ollama_model)
        
# #         # Session state to maintain context
# #         self.session = {
# #             'current_candidate': None,  # Current candidate being discussed
# #             'current_resume': None,     # Path to the current resume
# #             'analyzed_jobs': [],        # Jobs that have been analyzed
# #             'shortlisted_jobs': [],     # Jobs that were shortlisted
# #             'scheduled_interviews': []  # Interviews that have been scheduled
# #         }
        
# #         # Conversation history
# #         self.conversation_history = []
        
# #         # File upload directory for resumes
# #         self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
# #         os.makedirs(self.uploads_dir, exist_ok=True)
    
# #     def load_config(self):
# #         """Load configuration from config.json if it exists"""
# #         config = {
# #             'ollama_model': 'gemma2:2b',
# #             'smtp_server': None,
# #             'smtp_port': 587,
# #             'smtp_username': None,
# #             'smtp_password': None,
# #             'match_threshold': 0.75,
# #             'max_shortlisted': 2
# #         }
        
# #         if os.path.exists('config.json'):
# #             try:
# #                 with open('config.json', 'r') as f:
# #                     stored_config = json.load(f)
# #                     config.update(stored_config)
# #             except Exception as e:
# #                 print(f"Error loading config: {e}")
        
# #         return config
    
# #     def save_config(self):
# #         """Save configuration to config.json"""
# #         try:
# #             with open('config.json', 'w') as f:
# #                 json.dump(self.config, f, indent=2)
# #             return "Configuration saved successfully."
# #         except Exception as e:
# #             return f"Error saving configuration: {e}"
    
# #     def add_to_history(self, speaker, message):
# #         """Add a message to the conversation history"""
# #         self.conversation_history.append({
# #             'speaker': speaker,
# #             'message': message,
# #             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #         })
    
# #     def _ollama_query(self, prompt):
# #         """Use the Ollama model to generate responses"""
# #         try:
# #             response = requests.post(
# #                 f"{self.ollama_base_url}/generate",
# #                 json={
# #                     "model": self.config.get('ollama_model', self.ollama_model),
# #                     "prompt": prompt,
# #                     "stream": False
# #                 }
# #             )
            
# #             if response.status_code != 200:
# #                 return f"Error: Ollama API returned status code {response.status_code}"
            
# #             return response.json().get('response', '')
# #         except Exception as e:
# #             return f"Error connecting to Ollama: {e}"
    
# #     def get_candidate_info(self, candidate_id):
# #         """Get candidate information from the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, name, email, phone, skills, experience, education, certifications
# #         FROM candidates
# #         WHERE id = ?
# #         """, (candidate_id,))
        
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         if not result:
# #             return None
        
# #         return {
# #             'id': result[0],
# #             'name': result[1],
# #             'email': result[2],
# #             'phone': result[3],
# #             'skills': result[4],
# #             'experience': result[5],
# #             'education': result[6],
# #             'certifications': result[7]
# #         }
    
# #     def get_job_info(self, job_id):
# #         """Get job information from the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, job_title, summary, required_skills, required_experience, 
# #                required_qualifications, responsibilities
# #         FROM job_descriptions
# #         WHERE id = ?
# #         """, (job_id,))
        
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         if not result:
# #             return None
        
# #         return {
# #             'id': result[0],
# #             'job_title': result[1],
# #             'summary': result[2],
# #             'required_skills': result[3],
# #             'required_experience': result[4],
# #             'required_qualifications': result[5],
# #             'responsibilities': result[6]
# #         }
    
# #     def list_candidates(self):
# #         """Get a list of all candidates in the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, name, email
# #         FROM candidates
# #         ORDER BY id
# #         """)
        
# #         results = cursor.fetchall()
# #         conn.close()
        
# #         candidates = []
# #         for result in results:
# #             candidates.append({
# #                 'id': result[0],
# #                 'name': result[1],
# #                 'email': result[2]
# #             })
        
# #         return candidates
    
# #     def list_jobs(self):
# #         """Get a list of all jobs in the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, job_title, summary
# #         FROM job_descriptions
# #         ORDER BY id
# #         """)
        
# #         results = cursor.fetchall()
# #         conn.close()
        
# #         jobs = []
# #         for result in results:
# #             jobs.append({
# #                 'id': result[0],
# #                 'job_title': result[1],
# #                 'summary': result[2]
# #             })
        
# #         return jobs
    
# #     def save_uploaded_resume(self, resume_path):
# #         """Save an uploaded resume to the uploads directory"""
# #         if not os.path.exists(resume_path):
# #             return None
        
# #         # Create a unique filename based on timestamp
# #         filename = f"resume_{int(time.time())}_{os.path.basename(resume_path)}"
# #         destination = os.path.join(self.uploads_dir, filename)
        
# #         try:
# #             shutil.copy2(resume_path, destination)
# #             return destination
# #         except Exception as e:
# #             print(f"Error saving resume: {e}")
# #             return None
    
# #     def process_resume(self, resume_path, candidate_name=None, candidate_email=None):
# #         """Process a resume file with detailed output"""
# #         # Save the resume if it's not already in our uploads directory
# #         if not resume_path.startswith(self.uploads_dir):
# #             saved_path = self.save_uploaded_resume(resume_path)
# #             if saved_path:
# #                 resume_path = saved_path
# #             else:
# #                 return "Error: Could not access the resume file."
        
# #         # Process the resume
# #         processor = self.system.processor
# #         processor.verbose = True  # Enable verbose output
        
# #         result = []
# #         result.append(f"Processing resume: {os.path.basename(resume_path)}")
        
# #         # Extract text from resume
# #         resume_text = processor.extract_resume_text(resume_path)
# #         if not resume_text:
# #             result.append("Failed to extract text from the resume.")
# #             return "\n".join(result)
        
# #         result.append(f"Extracted {len(resume_text)} characters of text.")
# #         result.append(f"Text sample: {resume_text[:150]}...")
        
# #         # Extract candidate information
# #         result.append("\nAnalyzing resume content...")
# #         candidate_info = processor.extract_candidate_info(resume_text)
        
# #         # IMPORTANT FIX: Only override with provided info if it's not None AND not empty
# #         if candidate_name and candidate_name.strip():
# #             print(f"Overriding extracted name with provided name: {candidate_name}")
# #             candidate_info['name'] = candidate_name
# #         if candidate_email and candidate_email.strip():
# #             print(f"Overriding extracted email with provided email: {candidate_email}")
# #             candidate_info['email'] = candidate_email
        
# #         # Store in database
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         INSERT INTO candidates (name, email, phone, resume_text, skills, experience, education, certifications)
# #         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# #         """, (
# #             candidate_info.get('name', ''),
# #             candidate_info.get('email', ''),
# #             candidate_info.get('phone', ''),
# #             resume_text,
# #             candidate_info.get('skills', ''),
# #             candidate_info.get('experience', ''),
# #             candidate_info.get('education', ''),
# #             candidate_info.get('certifications', '')
# #         ))
        
# #         candidate_id = cursor.lastrowid
# #         conn.commit()
# #         conn.close()
        
# #         # Update session with current candidate
# #         self.session['current_candidate'] = candidate_id
# #         self.session['current_resume'] = resume_path
        
# #         # Get a clean version of the candidate name for display
# #         candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
# #         result.append(f"\nSuccessfully processed resume for {candidate_name}.")
# #         result.append(f"Candidate added to database with ID: {candidate_id}")
        
# #         # Display extracted information
# #         result.append("\nExtracted Information:")
# #         result.append(f"Name: {candidate_info.get('name', 'Not detected')}")
# #         result.append(f"Email: {candidate_info.get('email', 'Not detected')}")
# #         result.append(f"Phone: {candidate_info.get('phone', 'Not detected')}")
        
# #         if 'skills' in candidate_info and candidate_info['skills']:
# #             result.append(f"\nSkills: {candidate_info['skills']}")
        
# #         if 'experience' in candidate_info and candidate_info['experience']:
# #             result.append(f"\nExperience: {candidate_info['experience']}")
        
# #         if 'education' in candidate_info and candidate_info['education']:
# #             result.append(f"\nEducation: {candidate_info['education']}")
        
# #         if 'certifications' in candidate_info and candidate_info['certifications']:
# #             result.append(f"\nCertifications: {candidate_info['certifications']}")
        
# #         result.append("\nYou can now analyze this candidate against available jobs by asking questions like:")
# #         result.append("- \"Find suitable jobs for this candidate\"")
# #         result.append("- \"Match this candidate with our open positions\"")
# #         result.append("- \"What roles would be a good fit?\"")
        
# #         return "\n".join(result)
    
# #     def analyze_candidate(self, candidate_id=None):
# #         """Match a candidate against available jobs"""
# #         # Use the current candidate if none specified
# #         if candidate_id is None:
# #             candidate_id = self.session.get('current_candidate')
# #             if not candidate_id:
# #                 return "No candidate is currently selected. Please process a resume first or specify a candidate ID."
        
# #         # Get candidate information
# #         candidate = self.get_candidate_info(candidate_id)
# #         if not candidate:
# #             return f"No candidate found with ID {candidate_id}."
        
# #         result = []
# #         result.append(f"Analyzing matches for {candidate['name']} (ID: {candidate_id})...")
        
# #         # Match against all jobs
# #         matcher = self.system.matcher
# #         shortlisted_jobs = matcher.match_candidate_to_all_jobs(candidate_id)
        
# #         # Store in session
# #         self.session['analyzed_jobs'] = [job_id for job_id, _, _ in shortlisted_jobs]
# #         self.session['shortlisted_jobs'] = shortlisted_jobs
# #         self.session['current_candidate'] = candidate_id  # Ensure candidate is set in session
        
# #         result.append(f"\nAnalysis complete. {candidate['name']} was shortlisted for {len(shortlisted_jobs)} positions.")
        
# #         if shortlisted_jobs:
# #             result.append("\nYou can now schedule interviews for these positions by saying:")
# #             result.append("- \"Schedule interviews for these positions\"")
# #             result.append("- \"Send interview invitations\"")
# #             result.append("- \"Set up interviews for the shortlisted jobs\"")
# #         else:
# #             result.append("\nThe candidate wasn't shortlisted for any positions. You might want to:")
# #             result.append("- Process another resume")
# #             result.append("- Adjust the matching threshold (currently set to {:.0f}%)".format(matcher.threshold * 100))
        
# #         return "\n".join(result)
    
# #     def schedule_interviews(self):
# #         """Schedule interviews for shortlisted positions"""
# #         # Check if we have a current candidate and shortlisted jobs
# #         candidate_id = self.session.get('current_candidate')
# #         shortlisted_jobs = self.session.get('shortlisted_jobs', [])
        
# #         if not candidate_id:
# #             return "No candidate is currently selected. Please process a resume first."
        
# #         if not shortlisted_jobs:
# #             return "No positions have been shortlisted. Please analyze the candidate first."
        
# #         # Get candidate information
# #         candidate = self.get_candidate_info(candidate_id)
# #         if not candidate:
# #             return "The selected candidate could not be found in the database."
        
# #         result = []
# #         result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
        
# #         # Get the job IDs from the shortlisted jobs in the session
# #         job_ids = [job_id for job_id, _, _ in shortlisted_jobs]
# #         print(f"Using previously identified shortlisted positions: {job_ids}")
        
# #         # Get match IDs for these jobs and this candidate
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         # Get match IDs for the current candidate that are shortlisted but not scheduled
# #         match_ids = []
# #         for job_id in job_ids:
# #             cursor.execute("""
# #             SELECT id FROM matches 
# #             WHERE candidate_id = ? AND job_id = ? AND is_shortlisted = 1 AND interview_scheduled = 0
# #             """, (candidate_id, job_id))
            
# #             row = cursor.fetchone()
# #             if row:
# #                 match_ids.append(row[0])
        
# #         conn.close()
        
# #         if not match_ids:
# #             result.append("\nNo matches found for scheduling. This could be because:")
# #             result.append("- The interviews were already scheduled previously")
# #             result.append("- There was an issue with the database")
# #             return "\n".join(result)
        
# #         # Schedule interviews for these matches
# #         scheduler = self.system.scheduler
# #         num_scheduled = 0
        
# #         for match_id in match_ids:
# #             print(f"Scheduling interview for match ID: {match_id}")
# #             if scheduler.schedule_interview(match_id):
# #                 num_scheduled += 1
        
# #         # Store in session
# #         self.session['scheduled_interviews'] = shortlisted_jobs
        
# #         if num_scheduled > 0:
# #             result.append(f"\nSuccessfully scheduled {num_scheduled} interviews for {candidate['name']}.")
# #             result.append("\nInterview invitations have been sent (or would be sent if email is configured).")
# #             result.append("\nThe following positions were included:")
            
# #             for job_id, _, _ in shortlisted_jobs:
# #                 job = self.get_job_info(job_id)
# #                 if job:
# #                     result.append(f"- {job['job_title']}")
            
# #             result.append("\nWhat would you like to do next?")
# #             result.append("- \"Process another resume\"")
# #             result.append("- \"Show me all candidates\"")
# #             result.append("- \"Show me all scheduled interviews\"")
# #         else:
# #             result.append("\nNo interviews were scheduled. This could be because:")
# #             result.append("- The interviews were already scheduled previously")
# #             result.append("- There was an issue with the email configuration")
# #             result.append("- The candidate wasn't actually shortlisted for any positions")
        
# #         return "\n".join(result)
    
# #     def get_system_status(self):
# #         """Get the current status of the recruitment system"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         # Count various metrics
# #         cursor.execute("SELECT COUNT(*) FROM job_descriptions")
# #         job_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM candidates")
# #         candidate_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
# #         shortlisted_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
# #         interview_count = cursor.fetchone()[0]
        
# #         conn.close()
        
# #         # Get current candidate context
# #         current_context = ""
# #         if self.session.get('current_candidate'):
# #             candidate = self.get_candidate_info(self.session['current_candidate'])
# #             if candidate:
# #                 current_context = f"Currently working with: {candidate['name']} (ID: {candidate['id']})"
                
# #                 if self.session.get('shortlisted_jobs'):
# #                     current_context += f"\nShortlisted for {len(self.session['shortlisted_jobs'])} positions"
                
# #                 if self.session.get('scheduled_interviews'):
# #                     current_context += f"\nInterviews scheduled for {len(self.session['scheduled_interviews'])} positions"
        
# #         # Build status message
# #         status = [
# #             "=== RECRUITMENT SYSTEM STATUS ===",
# #             f"Total Job Descriptions: {job_count}",
# #             f"Total Candidates: {candidate_count}",
# #             f"Total Shortlisted Matches: {shortlisted_count}",
# #             f"Total Scheduled Interviews: {interview_count}",
# #             "",
# #             f"Ollama Model: {self.config.get('ollama_model')}",
# #             f"Match Threshold: {self.config.get('match_threshold', 0.75) * 100:.0f}%",
# #             f"Max Shortlisted Positions: {self.config.get('max_shortlisted', 2)}",
# #             ""
# #         ]
        
# #         if current_context:
# #             status.append("--- CURRENT SESSION ---")
# #             status.append(current_context)
        
# #         return "\n".join(status)
    
# #     def process_command(self, user_input):
# #         """Process a natural language command with stricter parameter handling"""
# #         # Add user input to history
# #         self.add_to_history('user', user_input)
        
# #         # Map simple commands directly without using LLM to prevent default value creation
# #         lower_input = user_input.lower()
        
# #         # Direct command mapping for common cases
# #         if "process" in lower_input and (".pdf" in lower_input or ".docx" in lower_input):
# #             # Extract just the resume path without adding defaults
# #             resume_path = None
            
# #             # Look for PDF or DOCX file
# #             file_pattern = r'([a-zA-Z0-9_\-\.]+\.(pdf|docx))'
# #             file_match = re.search(file_pattern, user_input)
# #             if file_match:
# #                 resume_path = file_match.group(1)
                
# #                 # Only process resume without any name/email override
# #                 response = self.process_resume(resume_path, None, None)
# #                 self.add_to_history('assistant', response)
# #                 return response
        
# #         # For other commands, build conversation context as before
# #         conversation_context = "\n".join([
# #             f"{msg['speaker']}: {msg['message']}" 
# #             for msg in self.conversation_history[-10:]
# #         ])
        
# #         # Get the current session state for context
# #         session_context = "Current session state:\n"
# #         if self.session.get('current_candidate'):
# #             candidate = self.get_candidate_info(self.session['current_candidate'])
# #             if candidate:
# #                 session_context += f"- Working with candidate: {candidate['name']} (ID: {candidate['id']})\n"
# #         if self.session.get('shortlisted_jobs'):
# #             session_context += f"- Candidate has been matched with {len(self.session['shortlisted_jobs'])} positions\n"
# #         if self.session.get('scheduled_interviews'):
# #             session_context += f"- Interviews have been scheduled for {len(self.session['scheduled_interviews'])} positions\n"
        
# #         # Build prompt for Ollama with VERY strict instructions about not adding defaults
# #         prompt = f"""You are an AI assistant for a recruitment system. Based on the conversation history and current session state, determine what action the user wants to take.

# #     {session_context}

# #     Recent conversation:
# #     {conversation_context}

# #     User's latest message: "{user_input}"

# #     IMPORTANT INSTRUCTIONS:
# #     1. DO NOT add any default values for parameters unless the user explicitly mentions them
# #     2. For "process_resume", ONLY include "resume_path" parameter unless the user explicitly provides a name or email
# #     3. NEVER create fictional candidate names or emails
# #     4. If user just says "process resume X.pdf", ONLY include the resume_path

# #     Analyze this message and respond with a JSON object indicating the action to take and any parameters. Possible actions are:
# #     1. "process_resume" - Process a resume file
# #     2. "analyze_candidate" - Match a candidate with jobs
# #     3. "schedule_interviews" - Schedule interviews for shortlisted positions
# #     4. "list_candidates" - Show all candidates
# #     5. "list_jobs" - Show all jobs
# #     6. "get_candidate" - Get details for a specific candidate
# #     7. "get_job" - Get details for a specific job
# #     8. "system_status" - Show system status
# #     9. "help" - Show help information
# #     10. "unknown" - Could not determine intent

# #     Reply with only valid JSON. Example for resume processing:
# #     {{"action": "process_resume", "params": {{"resume_path": "resume.pdf"}}}}

# #     JSON:"""

# #         # Get response from Ollama
# #         llm_response = self._ollama_query(prompt)
        
# #         try:
# #             # Extract JSON from the response
# #             json_match = re.search(r'({[\s\S]*})', llm_response)
# #             if json_match:
# #                 intent_data = json.loads(json_match.group(1))
# #                 action = intent_data.get('action', 'unknown')
# #                 params = intent_data.get('params', {})
                
# #                 # Extra safety check: ensure we don't have empty params
# #                 for key in list(params.keys()):
# #                     if params[key] == "" or params[key] is None:
# #                         del params[key]
                        
# #                 # For resume processing, verify we don't have name/email unless explicitly mentioned
# #                 if action == 'process_resume':
# #                     # Check if the user input actually contains names or emails
# #                     has_explicit_name = re.search(r'for\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', user_input) is not None
# #                     has_explicit_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input) is not None
                    
# #                     # Remove parameters not explicitly mentioned
# #                     if not has_explicit_name and 'candidate_name' in params:
# #                         print("Removing auto-generated candidate name")
# #                         del params['candidate_name']
                        
# #                     if not has_explicit_email and 'candidate_email' in params:
# #                         print("Removing auto-generated candidate email")
# #                         del params['candidate_email']
# #             else:
# #                 action = 'unknown'
# #                 params = {}
# #         except Exception as e:
# #             print(f"Error parsing LLM response: {e}")
# #             action = 'unknown'
# #             params = {}
        
# #         # Rest of the processing...
# #         response = ""
        
# #         if action == 'process_resume':
# #             resume_path = params.get('resume_path')
# #             if resume_path:
# #                 # Only pass these parameters if they exist and are non-empty
# #                 candidate_name = params.get('candidate_name') if 'candidate_name' in params else None
# #                 candidate_email = params.get('candidate_email') if 'candidate_email' in params else None
                
# #                 # Double-check to make absolutely sure we're not using empty values
# #                 if candidate_name == "":
# #                     candidate_name = None
# #                 if candidate_email == "":
# #                     candidate_email = None
                    
# #                 # Debug info
# #                 if candidate_name:
# #                     print(f"Using explicitly provided name: {candidate_name}")
# #                 if candidate_email:
# #                     print(f"Using explicitly provided email: {candidate_email}")
                    
# #                 response = self.process_resume(
# #                     resume_path,
# #                     candidate_name,
# #                     candidate_email
# #                 )
# #             else:
# #                 response = "I need a resume file to process. Please specify the path to the resume."
        
# #         elif action == 'analyze_candidate':
# #             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
# #             if candidate_id:
# #                 response = self.analyze_candidate(candidate_id)
# #             else:
# #                 response = "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
# #         elif action == 'schedule_interviews':
# #             response = self.schedule_interviews()
        
# #         elif action == 'list_candidates':
# #             candidates = self.list_candidates()
# #             if candidates:
# #                 lines = ["Here are all the candidates in the system:"]
# #                 for candidate in candidates:
# #                     lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
# #                 response = "\n".join(lines)
# #             else:
# #                 response = "No candidates found in the database."
        
# #         elif action == 'list_jobs':
# #             jobs = self.list_jobs()
# #             if jobs:
# #                 lines = ["Here are all the job positions in the system:"]
# #                 for job in jobs:
# #                     lines.append(f"{job['id']}: {job['job_title']}")
# #                     if job['summary']:
# #                         summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
# #                         lines.append(f"   {summary}")
# #                 response = "\n".join(lines)
# #             else:
# #                 response = "No jobs found in the database."
        
# #         elif action == 'get_candidate':
# #             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
# #             if candidate_id:
# #                 candidate = self.get_candidate_info(candidate_id)
# #                 if candidate:
# #                     lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
# #                     lines.append(f"Email: {candidate['email']}")
# #                     lines.append(f"Phone: {candidate['phone']}")
# #                     lines.append(f"\nSkills: {candidate['skills']}")
# #                     lines.append(f"\nExperience: {candidate['experience']}")
# #                     lines.append(f"\nEducation: {candidate['education']}")
# #                     lines.append(f"\nCertifications: {candidate['certifications']}")
# #                     response = "\n".join(lines)
# #                 else:
# #                     response = f"No candidate found with ID {candidate_id}."
# #             else:
# #                 response = "Please specify a candidate ID or process a resume first."
        
# #         elif action == 'get_job':
# #             job_id = params.get('job_id')
# #             if job_id:
# #                 job = self.get_job_info(job_id)
# #                 if job:
# #                     lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
# #                     lines.append(f"\nSummary: {job['summary']}")
# #                     lines.append(f"\nRequired Skills: {job['required_skills']}")
# #                     lines.append(f"\nRequired Experience: {job['required_experience']}")
# #                     lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
# #                     lines.append(f"\nResponsibilities: {job['responsibilities']}")
# #                     response = "\n".join(lines)
# #                 else:
# #                     response = f"No job found with ID {job_id}."
# #             else:
# #                 response = "Please specify a job ID."
        
# #         elif action == 'system_status':
# #             response = self.get_system_status()
        
# #         elif action == 'help':
# #             response = """
# #     I can help you with the following recruiting tasks:

# #     Resume Processing:
# #     - "Process resume.pdf for John Doe (john@example.com)"
# #     - "Extract data from the resume in path/to/file.pdf"

# #     Candidate Analysis:
# #     - "Find matching jobs for this candidate"
# #     - "Match this candidate with available positions"
# #     - "What roles would be a good fit?"

# #     Interview Scheduling:
# #     - "Schedule interviews for the shortlisted positions"
# #     - "Send interview invitations"
# #     - "Set up interviews for these jobs"

# #     Information Lookup:
# #     - "Show me all candidates"
# #     - "List all jobs"
# #     - "Show me details for candidate 3"
# #     - "Tell me about job position 5"

# #     System Information:
# #     - "What's the current status?"
# #     - "Show system status"
# #     - "Who am I working with right now?"

# #     I maintain context throughout our conversation, so you can refer to "this candidate" or "these positions" and I'll understand based on our discussion.
# #     """
        
# #         else:  # 'unknown' action
# #             response = "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."
        
# #         # Add response to history
# #         self.add_to_history('assistant', response)
        
# #         return response
# # def main():
# #     """Main entry point for the conversational recruitment system"""
# #     parser = argparse.ArgumentParser(description='Conversational Recruitment System')
# #     parser.add_argument('--model', default='gemma2:2b', help='Ollama model to use (default: gemma2:2b)')
# #     args = parser.parse_args()
    
# #     system = ConversationalRecruitmentSystem(ollama_model=args.model)
    
# #     print("\n============================================")
# #     print("     RECRUITMENT SYSTEM - CONVERSATION     ")
# #     print("============================================")
# #     print("I can help you process resumes, match candidates with jobs, and schedule interviews.")
# #     print("Type 'help' for more information or 'exit' to quit.")
    
# #     while True:
# #         try:
# #             user_input = input("\n> ")
            
# #             if user_input.lower() in ['exit', 'quit', 'q']:
# #                 print("Goodbye!")
# #                 break
            
# #             if user_input.strip():
# #                 response = system.process_command(user_input)
# #                 print("\n" + response)
            
# #         except KeyboardInterrupt:
# #             print("\nGoodbye!")
# #             break
# #         except Exception as e:
# #             print(f"Error: {e}")

# # if __name__ == "__main__":
# #     main()

# #!/usr/bin/env python3
# # import argparse
# # import os
# # import sys
# # import sqlite3
# # import json
# # import re
# # import requests
# # import tempfile
# # from datetime import datetime
# # import shutil
# # import time

# # # Ensure we can import from the current directory
# # sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
# # from db_setup import setup_database, import_jobs_from_csv



# # # Custom enhanced ResumeProcessor with improved extraction
# # class EnhancedResumeProcessor(ResumeProcessor):
# #     def extract_candidate_info(self, resume_text):
# #         """Extract candidate information from resume text with improved detection for all fields"""
# #         # Initialize empty candidate info dictionary
# #         candidate_info = {}
        
# #         # Try regex extraction for email
# #         email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
# #         email_match = re.search(email_pattern, resume_text)
# #         if email_match:
# #             candidate_info['email'] = email_match.group(0)
# #             print(f"Email extracted via regex: {candidate_info['email']}")

# #         # Expanded phone patterns to catch more formats
# #         phone_patterns = [
# #             r'Phone:\s*([+\d\s\-()]+)',  # Match "Phone: +1-842-6155"
# #             r'(\+\d{1,3}[\s-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})',  # Standard formats
# #             r'(\+\d{1,3}[\s-]?\d{3,})',  # International without separators
# #             r'(\d{3}[\s.-]?\d{3}[\s.-]?\d{4})'  # US format without country code
# #         ]
        
# #         for pattern in phone_patterns:
# #             phone_match = re.search(pattern, resume_text)
# #             if phone_match:
# #                 # If we matched "Phone: +1-842-6155", extract just the number part
# #                 if "Phone:" in pattern:
# #                     candidate_info['phone'] = phone_match.group(1).strip()
# #                 else:
# #                     candidate_info['phone'] = phone_match.group(0).strip()
# #                 print(f"Phone extracted via regex: {candidate_info['phone']}")
# #                 break
        
# #         # Look for "Name:" pattern in resume text
# #         name_pattern = r'Name:\s*([^\n]+)'
# #         name_match = re.search(name_pattern, resume_text)
# #         if name_match:
# #             candidate_info['name'] = name_match.group(1).strip()
# #             print(f"Name extracted via regex: {candidate_info['name']}")
# #         else:
# #             # Create a focused prompt just for name extraction
# #             name_prompt = f"""You are a recruiting expert. Extract ONLY the candidate's full name from this resume text.
# #             Look at the top of the resume first, as names typically appear at the beginning.
            
# #             Resume text:
# #             {resume_text[:2000]}
            
# #             Respond with ONLY the full name without any explanation or additional text. 
# #             If you cannot determine the name with high confidence, respond with "Unknown".
# #             """
            
# #             name_response = self._ollama_query(name_prompt)
# #             if name_response and name_response.strip() != "Unknown":
# #                 candidate_info['name'] = name_response.strip()
# #                 print(f"Name extracted via focused prompt: {candidate_info['name']}")
        
# #         # Look for common education patterns
# #         education_pattern = r'Education\s*(.+?)(?=\n\n|\n[A-Z]|$)'
# #         education_match = re.search(education_pattern, resume_text, re.DOTALL)
# #         if education_match:
# #             # Extract just the education section text for later use
# #             education_text = education_match.group(1).strip()
# #             print(f"Education section found via regex")
        
# #         # Now get the rest of the information with a separate prompt
# #         skills_prompt = f"""You are a recruiting expert. Extract information from this resume text as JSON with the following structure:
# #         {{
# #             "skills": "comma-separated list of technical and soft skills",
# #             "experience": "comma-separated work history with company names and roles",
# #             "education": "comma-separated education details including institutions and degrees",
# #             "certifications": "comma-separated list of professional certifications"
# #         }}

# #         Resume text:
# #         {resume_text[:5000]}
        
# #         Return only valid JSON. Do not include any explanation or additional text:"""
        
# #         skills_response = self._ollama_query(skills_prompt)
        
# #         try:
# #             # Extract JSON from the response (handling potential non-JSON text around it)
# #             json_match = re.search(r'({[\s\S]*})', skills_response)
# #             if json_match:
# #                 skills_info = json.loads(json_match.group(1))
# #                 # Update candidate_info with skills_info
# #                 for key, value in skills_info.items():
# #                     candidate_info[key] = value
# #             else:
# #                 print("Failed to extract JSON from Ollama response for skills")
# #         except Exception as e:
# #             print(f"Error parsing skills JSON response: {e}")
        
# #         # Log extraction summary
# #         print("Candidate information extracted:")
# #         for key, value in candidate_info.items():
# #             if key == 'experience' or key == 'education':
# #                 # Truncate long text fields for logging
# #                 value_preview = value[:100] + "..." if value and len(value) > 100 else value
# #                 print(f"- {key}: {value_preview}")
# #             else:
# #                 print(f"- {key}: {value}")
        
# #         return candidate_info

# # class EnhancedCandidateMatcher(CandidateMatcher):
# #     """Enhanced candidate matcher with better matching quality"""
    
# #     def match_candidate_to_job(self, candidate_id, job_id):
# #         """Calculate a match score between a candidate and a job with explanation"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         # Get candidate info
# #         cursor.execute("""
# #         SELECT name, skills, experience, education, certifications
# #         FROM candidates WHERE id = ?
# #         """, (candidate_id,))
# #         candidate = cursor.fetchone()
        
# #         if not candidate:
# #             print(f"Candidate with ID {candidate_id} not found")
# #             conn.close()
# #             return None, None
        
# #         # Get job info
# #         cursor.execute("""
# #         SELECT job_title, required_skills, required_experience, required_qualifications, responsibilities
# #         FROM job_descriptions WHERE id = ?
# #         """, (job_id,))
# #         job = cursor.fetchone()
        
# #         if not job:
# #             print(f"Job with ID {job_id} not found")
# #             conn.close()
# #             return None, None
        
# #         candidate_name, candidate_skills, candidate_experience, candidate_education, candidate_certifications = candidate
# #         job_title, required_skills, required_experience, required_qualifications, responsibilities = job
        
# #         # Create enhanced matching prompt with improved scoring guidance
# #         prompt = f"""You are a recruiting expert. Analyze how well this candidate matches the job requirements.

# # Job Position: {job_title}
# # Required Skills: {required_skills}
# # Required Experience: {required_experience}
# # Required Qualifications: {required_qualifications}
# # Job Responsibilities: {responsibilities}

# # Candidate Information:
# # Name: {candidate_name}
# # Skills: {candidate_skills}
# # Experience: {candidate_experience}
# # Education: {candidate_education}
# # Certifications: {candidate_certifications}

# # Score this match on a scale from 0.0 to 1.0 where:
# # - 0.9-1.0: Perfect match with all required skills and experience
# # - 0.8-0.89: Excellent match with most required skills and experience
# # - 0.7-0.79: Good match with many required skills and some experience
# # - 0.6-0.69: Moderate match with some skills and related experience
# # - 0.5-0.59: Basic match with a few relevant skills
# # - Below 0.5: Poor match

# # Important: Be realistic but generous in your scoring. Focus on whether the candidate's skills and experience directly match the job requirements. For tech positions, emphasize technical skill matches.

# # Format your response exactly as follows:
# # SCORE: [decimal number between 0.0-1.0]
# # REASONING: [2-3 sentence explanation of why they are a good match]
# # """

# #         # Get match score and reasoning from Ollama
# #         response = self._ollama_query(prompt)
        
# #         # Extract score and reasoning
# #         match_score = 0.0
# #         match_reasoning = ""
        
# #         score_match = re.search(r'SCORE:\s*([0-9]*[.]?[0-9]+)', response)
# #         if score_match:
# #             try:
# #                 match_score = float(score_match.group(1))
# #                 # Ensure score is between 0 and 1
# #                 match_score = max(0.0, min(1.0, match_score))
# #             except ValueError:
# #                 print("Invalid match score format from Ollama")
# #                 match_score = 0.0
        
# #         reasoning_match = re.search(r'REASONING:\s*(.*?)(?=$|\n\n)', response, re.DOTALL)
# #         if reasoning_match:
# #             match_reasoning = reasoning_match.group(1).strip()
# #         else:
# #             # Fallback if REASONING tag isn't found
# #             match_reasoning = response.replace(f"SCORE: {match_score}", "").strip()
        
# #         # Store match in database
# #         cursor.execute("""
# #         INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
# #         VALUES (?, ?, ?, ?)
# #         """, (job_id, candidate_id, match_score, 0))  # Default to not shortlisted
        
# #         match_id = cursor.lastrowid
# #         conn.commit()
# #         conn.close()
        
# #         return match_score, match_reasoning, match_id

# # class ConversationalRecruitmentSystem:
# #     """A conversational interface for the recruitment system that maintains context"""
    
# #     def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
# #         self.db_path = db_path
# #         self.ollama_model = ollama_model
# #         self.ollama_base_url = "http://localhost:11434/api"
        
# #         # Load config
# #         self.config = self.load_config()
        
# #         # Initialize underlying recruitment system
# #         self.system = RecruitmentSystem(
# #             db_path=db_path,
# #             ollama_model=self.config.get('ollama_model', ollama_model),
# #             smtp_server=self.config.get('smtp_server'),
# #             smtp_port=self.config.get('smtp_port', 587),
# #             smtp_username=self.config.get('smtp_username'),
# #             smtp_password=self.config.get('smtp_password'),
# #             match_threshold=self.config.get('match_threshold', 0.75),
# #             max_shortlisted=self.config.get('max_shortlisted', 2)
# #         )
        
# #         # Replace the default processor with our enhanced version
# #         self.system.processor = EnhancedResumeProcessor(db_path, ollama_model)
        
# #         # Replace the default matcher with our enhanced version
# #         self.system.matcher = EnhancedCandidateMatcher(
# #             db_path, 
# #             ollama_model,
# #             self.config.get('match_threshold', 0.75),
# #             self.config.get('max_shortlisted', 2)
# #         )
        
# #         # Session state to maintain context
# #         self.session = {
# #             'current_candidate': None,  # Current candidate being discussed
# #             'current_resume': None,     # Path to the current resume
# #             'analyzed_jobs': [],        # Jobs that have been analyzed
# #             'shortlisted_jobs': [],     # Jobs that were shortlisted
# #             'scheduled_interviews': []  # Interviews that have been scheduled
# #         }
        
# #         # Conversation history
# #         self.conversation_history = []
        
# #         # File upload directory for resumes
# #         self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
# #         os.makedirs(self.uploads_dir, exist_ok=True)
    
# #     def load_config(self):
# #         """Load configuration from config.json if it exists"""
# #         config = {
# #             'ollama_model': 'gemma2:2b',
# #             'smtp_server': None,
# #             'smtp_port': 587,
# #             'smtp_username': None,
# #             'smtp_password': None,
# #             'match_threshold': 0.75,
# #             'max_shortlisted': 2
# #         }
        
# #         if os.path.exists('config.json'):
# #             try:
# #                 with open('config.json', 'r') as f:
# #                     stored_config = json.load(f)
# #                     config.update(stored_config)
# #             except Exception as e:
# #                 print(f"Error loading config: {e}")
        
# #         return config
    
# #     def save_config(self):
# #         """Save configuration to config.json"""
# #         try:
# #             with open('config.json', 'w') as f:
# #                 json.dump(self.config, f, indent=2)
# #             return "Configuration saved successfully."
# #         except Exception as e:
# #             return f"Error saving configuration: {e}"
    
# #     def add_to_history(self, speaker, message):
# #         """Add a message to the conversation history"""
# #         self.conversation_history.append({
# #             'speaker': speaker,
# #             'message': message,
# #             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #         })
    
# #     def _ollama_query(self, prompt):
# #         """Use the Ollama model to generate responses"""
# #         try:
# #             response = requests.post(
# #                 f"{self.ollama_base_url}/generate",
# #                 json={
# #                     "model": self.config.get('ollama_model', self.ollama_model),
# #                     "prompt": prompt,
# #                     "stream": False
# #                 }
# #             )
            
# #             if response.status_code != 200:
# #                 return f"Error: Ollama API returned status code {response.status_code}"
            
# #             return response.json().get('response', '')
# #         except Exception as e:
# #             return f"Error connecting to Ollama: {e}"
    
# #     def get_candidate_info(self, candidate_id):
# #         """Get candidate information from the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, name, email, phone, skills, experience, education, certifications
# #         FROM candidates
# #         WHERE id = ?
# #         """, (candidate_id,))
        
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         if not result:
# #             return None
        
# #         return {
# #             'id': result[0],
# #             'name': result[1],
# #             'email': result[2],
# #             'phone': result[3],
# #             'skills': result[4],
# #             'experience': result[5],
# #             'education': result[6],
# #             'certifications': result[7]
# #         }
    
# #     def get_job_info(self, job_id):
# #         """Get job information from the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, job_title, summary, required_skills, required_experience, 
# #                required_qualifications, responsibilities
# #         FROM job_descriptions
# #         WHERE id = ?
# #         """, (job_id,))
        
# #         result = cursor.fetchone()
# #         conn.close()
        
# #         if not result:
# #             return None
        
# #         return {
# #             'id': result[0],
# #             'job_title': result[1],
# #             'summary': result[2],
# #             'required_skills': result[3],
# #             'required_experience': result[4],
# #             'required_qualifications': result[5],
# #             'responsibilities': result[6]
# #         }
    
# #     def list_candidates(self):
# #         """Get a list of all candidates in the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, name, email
# #         FROM candidates
# #         ORDER BY id
# #         """)
        
# #         results = cursor.fetchall()
# #         conn.close()
        
# #         candidates = []
# #         for result in results:
# #             candidates.append({
# #                 'id': result[0],
# #                 'name': result[1],
# #                 'email': result[2]
# #             })
        
# #         return candidates
    
# #     def list_jobs(self):
# #         """Get a list of all jobs in the database"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         SELECT id, job_title, summary
# #         FROM job_descriptions
# #         ORDER BY id
# #         """)
        
# #         results = cursor.fetchall()
# #         conn.close()
        
# #         jobs = []
# #         for result in results:
# #             jobs.append({
# #                 'id': result[0],
# #                 'job_title': result[1],
# #                 'summary': result[2]
# #             })
        
# #         return jobs
    
# #     def save_uploaded_resume(self, resume_path):
# #         """Save an uploaded resume to the uploads directory"""
# #         if not os.path.exists(resume_path):
# #             return None
        
# #         # Create a unique filename based on timestamp
# #         filename = f"resume_{int(time.time())}_{os.path.basename(resume_path)}"
# #         destination = os.path.join(self.uploads_dir, filename)
        
# #         try:
# #             shutil.copy2(resume_path, destination)
# #             return destination
# #         except Exception as e:
# #             print(f"Error saving resume: {e}")
# #             return None
    
# #     def process_resume(self, resume_path, candidate_name=None, candidate_email=None):
# #         """Process a resume file with detailed output"""
# #         # Save the resume if it's not already in our uploads directory
# #         if not resume_path.startswith(self.uploads_dir):
# #             saved_path = self.save_uploaded_resume(resume_path)
# #             if saved_path:
# #                 resume_path = saved_path
# #             else:
# #                 return "Error: Could not access the resume file."
        
# #         # Process the resume
# #         processor = self.system.processor
# #         processor.verbose = True  # Enable verbose output
        
# #         result = []
# #         result.append(f"Processing resume: {os.path.basename(resume_path)}")
        
# #         # Extract text from resume
# #         resume_text = processor.extract_resume_text(resume_path)
# #         if not resume_text:
# #             result.append("Failed to extract text from the resume.")
# #             return "\n".join(result)
        
# #         result.append(f"Extracted {len(resume_text)} characters of text.")
# #         result.append(f"Text sample: {resume_text[:150]}...")
        
# #         # Extract candidate information
# #         result.append("\nAnalyzing resume content...")
# #         candidate_info = processor.extract_candidate_info(resume_text)
        
# #         # IMPORTANT FIX: Only override with provided info if it's not None AND not empty
# #         if candidate_name and candidate_name.strip():
# #             print(f"Overriding extracted name with provided name: {candidate_name}")
# #             candidate_info['name'] = candidate_name
# #         if candidate_email and candidate_email.strip():
# #             print(f"Overriding extracted email with provided email: {candidate_email}")
# #             candidate_info['email'] = candidate_email
        
# #         # Store in database
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         cursor.execute("""
# #         INSERT INTO candidates (name, email, phone, resume_text, skills, experience, education, certifications)
# #         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# #         """, (
# #             candidate_info.get('name', ''),
# #             candidate_info.get('email', ''),
# #             candidate_info.get('phone', ''),
# #             resume_text,
# #             candidate_info.get('skills', ''),
# #             candidate_info.get('experience', ''),
# #             candidate_info.get('education', ''),
# #             candidate_info.get('certifications', '')
# #         ))
        
# #         candidate_id = cursor.lastrowid
# #         conn.commit()
# #         conn.close()
        
# #         # Update session with current candidate
# #         self.session['current_candidate'] = candidate_id
# #         self.session['current_resume'] = resume_path
        
# #         # Get a clean version of the candidate name for display
# #         candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
# #         result.append(f"\nSuccessfully processed resume for {candidate_name}.")
# #         result.append(f"Candidate added to database with ID: {candidate_id}")
        
# #         # Display extracted information
# #         result.append("\nExtracted Information:")
# #         result.append(f"Name: {candidate_info.get('name', 'Not detected')}")
# #         result.append(f"Email: {candidate_info.get('email', 'Not detected')}")
# #         result.append(f"Phone: {candidate_info.get('phone', 'Not detected')}")
        
# #         if 'skills' in candidate_info and candidate_info['skills']:
# #             result.append(f"\nSkills: {candidate_info['skills']}")
        
# #         if 'experience' in candidate_info and candidate_info['experience']:
# #             result.append(f"\nExperience: {candidate_info['experience']}")
        
# #         if 'education' in candidate_info and candidate_info['education']:
# #             result.append(f"\nEducation: {candidate_info['education']}")
        
# #         if 'certifications' in candidate_info and candidate_info['certifications']:
# #             result.append(f"\nCertifications: {candidate_info['certifications']}")
        
# #         result.append("\nYou can now analyze this candidate against available jobs by asking questions like:")
# #         result.append("- \"Find suitable jobs for this candidate\"")
# #         result.append("- \"Match this candidate with our open positions\"")
# #         result.append("- \"What roles would be a good fit?\"")
        
# #         return "\n".join(result)
    
# #     def analyze_candidate(self, candidate_id=None):
# #         """Match a candidate against available jobs"""
# #         # Use the current candidate if none specified
# #         if candidate_id is None:
# #             candidate_id = self.session.get('current_candidate')
# #             if not candidate_id:
# #                 return "No candidate is currently selected. Please process a resume first or specify a candidate ID."
        
# #         # Get candidate information
# #         candidate = self.get_candidate_info(candidate_id)
# #         if not candidate:
# #             return f"No candidate found with ID {candidate_id}."
        
# #         result = []
# #         result.append(f"Analyzing matches for {candidate['name']} (ID: {candidate_id})...")
        
# #         # Match against all jobs
# #         matcher = self.system.matcher
# #         shortlisted_jobs = matcher.match_candidate_to_all_jobs(candidate_id)
        
# #         # Store in session
# #         self.session['analyzed_jobs'] = [job_id for job_id, _, _ in shortlisted_jobs]
# #         self.session['shortlisted_jobs'] = shortlisted_jobs
# #         self.session['current_candidate'] = candidate_id  # Ensure candidate is set in session
        
# #         result.append(f"\nAnalysis complete. {candidate['name']} was shortlisted for {len(shortlisted_jobs)} positions.")
        
# #         if shortlisted_jobs:
# #             result.append("\nYou can now schedule interviews for these positions by saying:")
# #             result.append("- \"Schedule interviews for these positions\"")
# #             result.append("- \"Send interview invitations\"")
# #             result.append("- \"Set up interviews for the shortlisted jobs\"")
# #         else:
# #             result.append("\nThe candidate wasn't shortlisted for any positions. You might want to:")
# #             result.append("- Process another resume")
# #             result.append("- Adjust the matching threshold (currently set to {:.0f}%)".format(matcher.threshold * 100))
        
# #         return "\n".join(result)
    
# #     def schedule_interviews(self):
# #         """Schedule interviews for shortlisted positions"""
# #         # Check if we have a current candidate and shortlisted jobs
# #         candidate_id = self.session.get('current_candidate')
# #         shortlisted_jobs = self.session.get('shortlisted_jobs', [])
        
# #         if not candidate_id:
# #             return "No candidate is currently selected. Please process a resume first."
        
# #         if not shortlisted_jobs:
# #             return "No positions have been shortlisted. Please analyze the candidate first."
        
# #         # Get candidate information
# #         candidate = self.get_candidate_info(candidate_id)
# #         if not candidate:
# #             return "The selected candidate could not be found in the database."
        
# #         result = []
# #         result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
        
# #         # Get the job IDs from the shortlisted jobs in the session
# #         job_ids = [job_id for job_id, _, _ in shortlisted_jobs]
# #         print(f"Using previously identified shortlisted positions: {job_ids}")
        
# #         # Get match IDs for these jobs and this candidate
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         # Get match IDs for the current candidate that are shortlisted but not scheduled
# #         match_ids = []
# #         for job_id in job_ids:
# #             cursor.execute("""
# #             SELECT id FROM matches 
# #             WHERE candidate_id = ? AND job_id = ? AND is_shortlisted = 1 AND interview_scheduled = 0
# #             """, (candidate_id, job_id))
            
# #             row = cursor.fetchone()
# #             if row:
# #                 match_ids.append(row[0])
        
# #         conn.close()
        
# #         if not match_ids:
# #             result.append("\nNo matches found for scheduling. This could be because:")
# #             result.append("- The interviews were already scheduled previously")
# #             result.append("- There was an issue with the database")
# #             return "\n".join(result)
        
# #         # Schedule interviews for these matches
# #         scheduler = self.system.scheduler
# #         num_scheduled = 0
        
# #         for match_id in match_ids:
# #             print(f"Scheduling interview for match ID: {match_id}")
# #             if scheduler.schedule_interview(match_id):
# #                 num_scheduled += 1
        
# #         # Store in session
# #         self.session['scheduled_interviews'] = shortlisted_jobs
        
# #         if num_scheduled > 0:
# #             result.append(f"\nSuccessfully scheduled {num_scheduled} interviews for {candidate['name']}.")
# #             result.append("\nInterview invitations have been sent (or would be sent if email is configured).")
# #             result.append("\nThe following positions were included:")
            
# #             for job_id, _, _ in shortlisted_jobs:
# #                 job = self.get_job_info(job_id)
# #                 if job:
# #                     result.append(f"- {job['job_title']}")
            
# #             result.append("\nWhat would you like to do next?")
# #             result.append("- \"Process another resume\"")
# #             result.append("- \"Show me all candidates\"")
# #             result.append("- \"Show me all scheduled interviews\"")
# #         else:
# #             result.append("\nNo interviews were scheduled. This could be because:")
# #             result.append("- The interviews were already scheduled previously")
# #             result.append("- There was an issue with the email configuration")
# #             result.append("- The candidate wasn't actually shortlisted for any positions")
        
# #         return "\n".join(result)
    
# #     def get_system_status(self):
# #         """Get the current status of the recruitment system"""
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()
        
# #         # Count various metrics
# #         cursor.execute("SELECT COUNT(*) FROM job_descriptions")
# #         job_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM candidates")
# #         candidate_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
# #         shortlisted_count = cursor.fetchone()[0]
        
# #         cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
# #         interview_count = cursor.fetchone()[0]
        
# #         conn.close()
        
# #         # Get current candidate context
# #         current_context = ""
# #         if self.session.get('current_candidate'):
# #             candidate = self.get_candidate_info(self.session['current_candidate'])
# #             if candidate:
# #                 current_context = f"Currently working with: {candidate['name']} (ID: {candidate['id']})"
                
# #                 if self.session.get('shortlisted_jobs'):
# #                     current_context += f"\nShortlisted for {len(self.session['shortlisted_jobs'])} positions"
                
# #                 if self.session.get('scheduled_interviews'):
# #                     current_context += f"\nInterviews scheduled for {len(self.session['scheduled_interviews'])} positions"
        
# #         # Build status message
# #         status = [
# #             "=== RECRUITMENT SYSTEM STATUS ===",
# #             f"Total Job Descriptions: {job_count}",
# #             f"Total Candidates: {candidate_count}",
# #             f"Total Shortlisted Matches: {shortlisted_count}",
# #             f"Total Scheduled Interviews: {interview_count}",
# #             "",
# #             f"Ollama Model: {self.config.get('ollama_model')}",
# #             f"Match Threshold: {self.config.get('match_threshold', 0.75) * 100:.0f}%",
# #             f"Max Shortlisted Positions: {self.config.get('max_shortlisted', 2)}",
# #             ""
# #         ]
        
# #         if current_context:
# #             status.append("--- CURRENT SESSION ---")
# #             status.append(current_context)
        
# #         return "\n".join(status)
    
# #     def update_config(self, new_settings):
# #         """Update configuration settings"""
# #         for key, value in new_settings.items():
# #             if key in self.config:
# #                 # Convert to appropriate type
# #                 if key == 'match_threshold':
# #                     value = float(value)
# #                 elif key == 'max_shortlisted' or key == 'smtp_port':
# #                     value = int(value)
                
# #                 self.config[key] = value
                
# #                 # Special case for threshold - also update the matcher
# #                 if key == 'match_threshold' and hasattr(self.system, 'matcher'):
# #                     self.system.matcher.threshold = value
                
# #                 # Special case for max_shortlisted - also update the matcher
# #                 if key == 'max_shortlisted' and hasattr(self.system, 'matcher'):
# #                     self.system.matcher.max_shortlisted = value
        
# #         # Save the updated config
# #         self.save_config()
        
# #         return f"Configuration updated successfully. New settings: {new_settings}"
    
# #     def process_command(self, user_input):
# #         """Process a natural language command with stricter parameter handling"""
# #         # Add user input to history
# #         self.add_to_history('user', user_input)
        
# #         # Handle configuration change command
# #         if "change match threshold" in user_input.lower() or "set match threshold" in user_input.lower():
# #              # Extract the threshold value from the command
# #             threshold_match = re.search(r'threshold\s+(?:to\s+)?(\d+(?:\.\d+)?)', user_input)
# #             if threshold_match:
# #                 new_threshold = float(threshold_match.group(1))
# #                 # Convert percentage to decimal if needed
# #                 if new_threshold > 1:
# #                     new_threshold = new_threshold / 100
                
# #                 response = self.update_config({'match_threshold': new_threshold})
# #                 self.add_to_history('assistant', response)
# #                 return response
        
# #         # Map simple commands directly without using LLM to prevent default value creation
# #         lower_input = user_input.lower()
        
# #         # Direct command mapping for common cases
# #         if "process" in lower_input and (".pdf" in lower_input or ".docx" in lower_input):
# #             # Extract just the resume path without adding defaults
# #             resume_path = None
            
# #             # Look for PDF or DOCX file
# #             file_pattern = r'([a-zA-Z0-9_\-\.]+\.(pdf|docx))'
# #             file_match = re.search(file_pattern, user_input)
# #             if file_match:
# #                 resume_path = file_match.group(1)
                
# #                 # Only process resume without any name/email override
# #                 response = self.process_resume(resume_path, None, None)
# #                 self.add_to_history('assistant', response)
# #                 return response
        
# #         # For other commands, build conversation context as before
# #         conversation_context = "\n".join([
# #             f"{msg['speaker']}: {msg['message']}" 
# #             for msg in self.conversation_history[-10:]
# #         ])
        
# #         # Get the current session state for context
# #         session_context = "Current session state:\n"
# #         if self.session.get('current_candidate'):
# #             candidate = self.get_candidate_info(self.session['current_candidate'])
# #             if candidate:
# #                 session_context += f"- Working with candidate: {candidate['name']} (ID: {candidate['id']})\n"
# #         if self.session.get('shortlisted_jobs'):
# #             session_context += f"- Candidate has been matched with {len(self.session['shortlisted_jobs'])} positions\n which are {self.session['shortlisted_jobs']}"
# #         if self.session.get('scheduled_interviews'):
# #             session_context += f"- Interviews have been scheduled for {len(self.session['scheduled_interviews'])} positions\n"
        
# #         # Build prompt for Ollama with VERY strict instructions about not adding defaults
# #         prompt = f"""You are an AI assistant for a recruitment system. Based on the conversation history and current session state, determine what action the user wants to take.

# # {session_context}

# # Recent conversation:
# # {conversation_context}

# # User's latest message: "{user_input}"

# # IMPORTANT INSTRUCTIONS:
# # 1. DO NOT add any default values for parameters unless the user explicitly mentions them
# # 2. For "process_resume", ONLY include "resume_path" parameter unless the user explicitly provides a name or email
# # 3. NEVER create fictional candidate names or emails
# # 4. If user just says "process resume X.pdf", ONLY include the resume_path

# # Analyze this message and respond with a JSON object indicating the action to take and any parameters. Possible actions are:
# # 1. "process_resume" - Process a resume file
# # 2. "analyze_candidate" - Match a candidate with jobs
# # 3. "schedule_interviews" - Schedule interviews for shortlisted positions
# # 4. "list_candidates" - Show all candidates
# # 5. "list_jobs" - Show all jobs
# # 6. "get_candidate" - Get details for a specific candidate
# # 7. "get_job" - Get details for a specific job
# # 8. "system_status" - Show system status
# # 9. "help" - Show help information
# # 10. "unknown" - Could not determine intent

# # Reply with only valid JSON. Example for resume processing:
# # {{"action": "process_resume", "params": {{"resume_path": "resume.pdf"}}}}

# # JSON:"""

# #         # Get response from Ollama

# #         llm_response = self._ollama_query(prompt)
# #         print(prompt, llm_response)
        
# #         try:
# #             # Extract JSON from the response
# #             json_match = re.search(r'({[\s\S]*})', llm_response)
# #             if json_match:
# #                 intent_data = json.loads(json_match.group(1))
# #                 action = intent_data.get('action', 'unknown')
# #                 params = intent_data.get('params', {})
                
# #                 # Extra safety check: ensure we don't have empty params
# #                 for key in list(params.keys()):
# #                     if params[key] == "" or params[key] is None:
# #                         del params[key]
                        
# #                 # For resume processing, verify we don't have name/email unless explicitly mentioned
# #                 if action == 'process_resume':
# #                     # Check if the user input actually contains names or emails
# #                     has_explicit_name = re.search(r'for\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', user_input) is not None
# #                     has_explicit_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input) is not None
                    
# #                     # Remove parameters not explicitly mentioned
# #                     if not has_explicit_name and 'candidate_name' in params:
# #                         print("Removing auto-generated candidate name")
# #                         del params['candidate_name']
                        
# #                     if not has_explicit_email and 'candidate_email' in params:
# #                         print("Removing auto-generated candidate email")
# #                         del params['candidate_email']
# #             else:
# #                 action = 'unknown'
# #                 params = {}
# #         except Exception as e:
# #             print(f"Error parsing LLM response: {e}")
# #             action = 'unknown'
# #             params = {}
        
# #         # Rest of the processing...
# #         response = ""
        
# #         if action == 'process_resume':
# #             resume_path = params.get('resume_path')
# #             if resume_path:
# #                 # Only pass these parameters if they exist and are non-empty
# #                 candidate_name = params.get('candidate_name') if 'candidate_name' in params else None
# #                 candidate_email = params.get('candidate_email') if 'candidate_email' in params else None
                
# #                 # Double-check to make absolutely sure we're not using empty values
# #                 if candidate_name == "":
# #                     candidate_name = None
# #                 if candidate_email == "":
# #                     candidate_email = None
                    
# #                 # Debug info
# #                 if candidate_name:
# #                     print(f"Using explicitly provided name: {candidate_name}")
# #                 if candidate_email:
# #                     print(f"Using explicitly provided email: {candidate_email}")
                    
# #                 response = self.process_resume(
# #                     resume_path,
# #                     candidate_name,
# #                     candidate_email
# #                 )
# #             else:
# #                 response = "I need a resume file to process. Please specify the path to the resume."
        
# #         elif action == 'analyze_candidate':
# #             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
# #             if candidate_id:
# #                 response = self.analyze_candidate(candidate_id)
# #             else:
# #                 response = "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
# #         elif action == 'schedule_interviews':
# #             response = self.schedule_interviews()
        
# #         elif action == 'list_candidates':
# #             candidates = self.list_candidates()
# #             if candidates:
# #                 lines = ["Here are all the candidates in the system:"]
# #                 for candidate in candidates:
# #                     lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
# #                 response = "\n".join(lines)
# #             else:
# #                 response = "No candidates found in the database."
        
# #         elif action == 'list_jobs':
# #             jobs = self.list_jobs()
# #             if jobs:
# #                 lines = ["Here are all the job positions in the system:"]
# #                 for job in jobs:
# #                     lines.append(f"{job['id']}: {job['job_title']}")
# #                     if job['summary']:
# #                         summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
# #                         lines.append(f"   {summary}")
# #                 response = "\n".join(lines)
# #             else:
# #                 response = "No jobs found in the database."
        
# #         elif action == 'get_candidate':
# #             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
# #             if candidate_id:
# #                 candidate = self.get_candidate_info(candidate_id)
# #                 if candidate:
# #                     lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
# #                     lines.append(f"Email: {candidate['email']}")
# #                     lines.append(f"Phone: {candidate['phone']}")
# #                     lines.append(f"\nSkills: {candidate['skills']}")
# #                     lines.append(f"\nExperience: {candidate['experience']}")
# #                     lines.append(f"\nEducation: {candidate['education']}")
# #                     lines.append(f"\nCertifications: {candidate['certifications']}")
# #                     response = "\n".join(lines)
# #                 else:
# #                     response = f"No candidate found with ID {candidate_id}."
# #             else:
# #                 response = "Please specify a candidate ID or process a resume first."
        
# #         elif action == 'get_job':
# #             job_id = params.get('job_id')
# #             if job_id:
# #                 job = self.get_job_info(job_id)
# #                 if job:
# #                     lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
# #                     lines.append(f"\nSummary: {job['summary']}")
# #                     lines.append(f"\nRequired Skills: {job['required_skills']}")
# #                     lines.append(f"\nRequired Experience: {job['required_experience']}")
# #                     lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
# #                     lines.append(f"\nResponsibilities: {job['responsibilities']}")
# #                     response = "\n".join(lines)
# #                 else:
# #                     response = f"No job found with ID {job_id}."
# #             else:
# #                 response = "Please specify a job ID."
        
# #         elif action == 'system_status':
# #             response = self.get_system_status()
        
# #         elif action == 'help':
# #             response = """
# # I can help you with the following recruiting tasks:

# # Resume Processing:
# # - "Process resume.pdf for John Doe (john@example.com)"
# # - "Extract data from the resume in path/to/file.pdf"

# # Candidate Analysis:
# # - "Find matching jobs for this candidate"
# # - "Match this candidate with available positions"
# # - "What roles would be a good fit?"

# # Interview Scheduling:
# # - "Schedule interviews for the shortlisted positions"
# # - "Send interview invitations"
# # - "Set up interviews for these jobs"

# # Information Lookup:
# # - "Show me all candidates"
# # - "List all jobs"
# # - "Show me details for candidate 3"
# # - "Tell me about job position 5"

# # Configuration:
# # - "Change match threshold to 60%"
# # - "Set threshold to 0.65"

# # System Information:
# # - "What's the current status?"
# # - "Show system status"
# # - "Who am I working with right now?"

# # I maintain context throughout our conversation, so you can refer to "this candidate" or "these positions" and I'll understand based on our discussion.
# # """
        
# #         else:  # 'unknown' action
# #             response = "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."
        
# #         # Add response to history
# #         self.add_to_history('assistant', response)
        
# #         return response

# # def main():
# #     """Main entry point for the conversational recruitment system"""
# #     parser = argparse.ArgumentParser(description='Conversational Recruitment System')
# #     parser.add_argument('--model', default='gemma2:2b', help='Ollama model to use (default: gemma2:2b)')
# #     args = parser.parse_args()
    
# #     system = ConversationalRecruitmentSystem(ollama_model=args.model)
    
# #     print("\n============================================")
# #     print("     RECRUITMENT SYSTEM - CONVERSATION     ")
# #     print("============================================")
# #     print("I can help you process resumes, match candidates with jobs, and schedule interviews.")
# #     print("Type 'help' for more information or 'exit' to quit.")
    
# #     while True:
# #         try:
# #             user_input = input("\n> ")
            
# #             if user_input.lower() in ['exit', 'quit', 'q']:
# #                 print("Goodbye!")
# #                 break
            
# #             if user_input.strip():
# #                 response = system.process_command(user_input)
# #                 print("\n" + response)
            
# #         except KeyboardInterrupt:
# #             print("\nGoodbye!")
# #             break
# #         except Exception as e:
# #             print(f"Error: {e}")

# # if __name__ == "__main__":
# #     main()

# import argparse
# import os
# import sys
# import sqlite3
# import json
# import re
# import requests
# import tempfile
# from datetime import datetime
# import shutil
# import time

# # Ensure we can import from the current directory
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
# from db_setup import setup_database, import_jobs_from_csv



# # Custom enhanced ResumeProcessor with improved extraction
# class EnhancedResumeProcessor(ResumeProcessor):
#     def extract_candidate_info(self, resume_text):
#         """Extract candidate information from resume text with improved detection for all fields"""
#         # Initialize empty candidate info dictionary
#         candidate_info = {}
        
#         # Try regex extraction for email
#         email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
#         email_match = re.search(email_pattern, resume_text)
#         if email_match:
#             candidate_info['email'] = email_match.group(0)
#             print(f"Email extracted via regex: {candidate_info['email']}")

#         # Expanded phone patterns to catch more formats
#         phone_patterns = [
#             r'Phone:\s*([+\d\s\-()]+)',  # Match "Phone: +1-842-6155"
#             r'(\+\d{1,3}[\s-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})',  # Standard formats
#             r'(\+\d{1,3}[\s-]?\d{3,})',  # International without separators
#             r'(\d{3}[\s.-]?\d{3}[\s.-]?\d{4})'  # US format without country code
#         ]
        
#         for pattern in phone_patterns:
#             phone_match = re.search(pattern, resume_text)
#             if phone_match:
#                 # If we matched "Phone: +1-842-6155", extract just the number part
#                 if "Phone:" in pattern:
#                     candidate_info['phone'] = phone_match.group(1).strip()
#                 else:
#                     candidate_info['phone'] = phone_match.group(0).strip()
#                 print(f"Phone extracted via regex: {candidate_info['phone']}")
#                 break
        
#         # Look for "Name:" pattern in resume text
#         name_pattern = r'Name:\s*([^\n]+)'
#         name_match = re.search(name_pattern, resume_text)
#         if name_match:
#             candidate_info['name'] = name_match.group(1).strip()
#             print(f"Name extracted via regex: {candidate_info['name']}")
#         else:
#             # Create a focused prompt just for name extraction
#             name_prompt = f"""You are a recruiting expert. Extract ONLY the candidate's full name from this resume text.
#             Look at the top of the resume first, as names typically appear at the beginning.
            
#             Resume text:
#             {resume_text[:2000]}
            
#             Respond with ONLY the full name without any explanation or additional text. 
#             If you cannot determine the name with high confidence, respond with "Unknown".
#             """
            
#             name_response = self._ollama_query(name_prompt)
#             if name_response and name_response.strip() != "Unknown":
#                 candidate_info['name'] = name_response.strip()
#                 print(f"Name extracted via focused prompt: {candidate_info['name']}")
        
#         # Look for common education patterns
#         education_pattern = r'Education\s*(.+?)(?=\n\n|\n[A-Z]|$)'
#         education_match = re.search(education_pattern, resume_text, re.DOTALL)
#         if education_match:
#             # Extract just the education section text for later use
#             education_text = education_match.group(1).strip()
#             print(f"Education section found via regex")
        
#         # Now get the rest of the information with a separate prompt
#         skills_prompt = f"""You are a recruiting expert. Extract information from this resume text as JSON with the following structure:
#         {{
#             "skills": "comma-separated list of technical and soft skills",
#             "experience": "comma-separated work history with company names and roles",
#             "education": "comma-separated education details including institutions and degrees",
#             "certifications": "comma-separated list of professional certifications"
#         }}

#         Resume text:
#         {resume_text[:5000]}
        
#         Return only valid JSON. Do not include any explanation or additional text:"""
        
#         skills_response = self._ollama_query(skills_prompt)
        
#         try:
#             # Extract JSON from the response (handling potential non-JSON text around it)
#             json_match = re.search(r'({[\s\S]*})', skills_response)
#             if json_match:
#                 skills_info = json.loads(json_match.group(1))
#                 # Update candidate_info with skills_info
#                 for key, value in skills_info.items():
#                     candidate_info[key] = value
#             else:
#                 print("Failed to extract JSON from Ollama response for skills")
#         except Exception as e:
#             print(f"Error parsing skills JSON response: {e}")
        
#         # Log extraction summary
#         print("Candidate information extracted:")
#         for key, value in candidate_info.items():
#             if key == 'experience' or key == 'education':
#                 # Truncate long text fields for logging
#                 value_preview = value[:100] + "..." if value and len(value) > 100 else value
#                 print(f"- {key}: {value_preview}")
#             else:
#                 print(f"- {key}: {value}")
        
#         return candidate_info

# class EnhancedCandidateMatcher(CandidateMatcher):
#     """Enhanced candidate matcher with better matching quality"""
    
#     def match_candidate_to_job(self, candidate_id, job_id):
#         """Calculate a match score between a candidate and a job with explanation"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         # Get candidate info
#         cursor.execute("""
#         SELECT name, skills, experience, education, certifications
#         FROM candidates WHERE id = ?
#         """, (candidate_id,))
#         candidate = cursor.fetchone()
        
#         if not candidate:
#             print(f"Candidate with ID {candidate_id} not found")
#             conn.close()
#             return None, None
        
#         # Get job info
#         cursor.execute("""
#         SELECT job_title, required_skills, required_experience, required_qualifications, responsibilities
#         FROM job_descriptions WHERE id = ?
#         """, (job_id,))
#         job = cursor.fetchone()
        
#         if not job:
#             print(f"Job with ID {job_id} not found")
#             conn.close()
#             return None, None
        
#         candidate_name, candidate_skills, candidate_experience, candidate_education, candidate_certifications = candidate
#         job_title, required_skills, required_experience, required_qualifications, responsibilities = job
        
#         # Create enhanced matching prompt with improved scoring guidance
#         prompt = f"""You are a recruiting expert. Analyze how well this candidate matches the job requirements.

# Job Position: {job_title}
# Required Skills: {required_skills}
# Required Experience: {required_experience}
# Required Qualifications: {required_qualifications}
# Job Responsibilities: {responsibilities}

# Candidate Information:
# Name: {candidate_name}
# Skills: {candidate_skills}
# Experience: {candidate_experience}
# Education: {candidate_education}
# Certifications: {candidate_certifications}

# Score this match on a scale from 0.0 to 1.0 where:
# - 0.9-1.0: Perfect match with all required skills and experience
# - 0.8-0.89: Excellent match with most required skills and experience
# - 0.7-0.79: Good match with many required skills and some experience
# - 0.6-0.69: Moderate match with some skills and related experience
# - 0.5-0.59: Basic match with a few relevant skills
# - Below 0.5: Poor match

# Important: Be realistic but generous in your scoring. Focus on whether the candidate's skills and experience directly match the job requirements. For tech positions, emphasize technical skill matches.

# Format your response exactly as follows:
# SCORE: [decimal number between 0.0-1.0]
# REASONING: [2-3 sentence explanation of why they are a good match]
# """

#         # Get match score and reasoning from Ollama
#         response = self._ollama_query(prompt)
        
#         # Extract score and reasoning
#         match_score = 0.0
#         match_reasoning = ""
        
#         score_match = re.search(r'SCORE:\s*([0-9]*[.]?[0-9]+)', response)
#         if score_match:
#             try:
#                 match_score = float(score_match.group(1))
#                 # Ensure score is between 0 and 1
#                 match_score = max(0.0, min(1.0, match_score))
#             except ValueError:
#                 print("Invalid match score format from Ollama")
#                 match_score = 0.0
        
#         reasoning_match = re.search(r'REASONING:\s*(.*?)(?=$|\n\n)', response, re.DOTALL)
#         if reasoning_match:
#             match_reasoning = reasoning_match.group(1).strip()
#         else:
#             # Fallback if REASONING tag isn't found
#             match_reasoning = response.replace(f"SCORE: {match_score}", "").strip()
        
#         # Store match in database
#         cursor.execute("""
#         INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
#         VALUES (?, ?, ?, ?)
#         """, (job_id, candidate_id, match_score, 0))  # Default to not shortlisted
        
#         match_id = cursor.lastrowid
#         conn.commit()
#         conn.close()
        
#         return match_score, match_reasoning, match_id

# class ConversationalRecruitmentSystem:
#     """A conversational interface for the recruitment system that maintains context"""
    
#     def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
#         self.db_path = db_path
#         self.ollama_model = ollama_model
#         self.ollama_base_url = "http://localhost:11434/api"
        
#         # Load config
#         self.config = self.load_config()
        
#         # Initialize underlying recruitment system
#         self.system = RecruitmentSystem(
#             db_path=db_path,
#             ollama_model=self.config.get('ollama_model', ollama_model),
#             smtp_server=self.config.get('smtp_server'),
#             smtp_port=self.config.get('smtp_port', 587),
#             smtp_username=self.config.get('smtp_username'),
#             smtp_password=self.config.get('smtp_password'),
#             match_threshold=self.config.get('match_threshold', 0.75),
#             max_shortlisted=self.config.get('max_shortlisted', 2)
#         )
        
#         # Replace the default processor with our enhanced version
#         self.system.processor = EnhancedResumeProcessor(db_path, ollama_model)
        
#         # Replace the default matcher with our enhanced version
#         self.system.matcher = EnhancedCandidateMatcher(
#             db_path, 
#             ollama_model,
#             self.config.get('match_threshold', 0.75),
#             self.config.get('max_shortlisted', 2)
#         )
        
#         # Session state to maintain context
#         self.session = {
#             'current_candidate': None,  # Current candidate being discussed
#             'current_resume': None,     # Path to the current resume
#             'analyzed_jobs': [],        # Jobs that have been analyzed
#             'shortlisted_jobs': [],     # Jobs that were shortlisted
#             'scheduled_interviews': []  # Interviews that have been scheduled
#         }
        
#         # Conversation history
#         self.conversation_history = []
        
#         # File upload directory for resumes
#         self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
#         os.makedirs(self.uploads_dir, exist_ok=True)
    
#     def load_config(self):
#         """Load configuration from config.json if it exists"""
#         config = {
#             'ollama_model': 'gemma2:2b',
#             'smtp_server': None,
#             'smtp_port': 587,
#             'smtp_username': None,
#             'smtp_password': None,
#             'match_threshold': 0.75,
#             'max_shortlisted': 2
#         }
        
#         if os.path.exists('config.json'):
#             try:
#                 with open('config.json', 'r') as f:
#                     stored_config = json.load(f)
#                     config.update(stored_config)
#             except Exception as e:
#                 print(f"Error loading config: {e}")
        
#         return config
    
#     def save_config(self):
#         """Save configuration to config.json"""
#         try:
#             with open('config.json', 'w') as f:
#                 json.dump(self.config, f, indent=2)
#             return "Configuration saved successfully."
#         except Exception as e:
#             return f"Error saving configuration: {e}"
    
#     def add_to_history(self, speaker, message):
#         """Add a message to the conversation history"""
#         self.conversation_history.append({
#             'speaker': speaker,
#             'message': message,
#             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })
    
#     def _ollama_query(self, prompt):
#         """Use the Ollama model to generate responses"""
#         try:
#             response = requests.post(
#                 f"{self.ollama_base_url}/generate",
#                 json={
#                     "model": self.config.get('ollama_model', self.ollama_model),
#                     "prompt": prompt,
#                     "stream": False
#                 }
#             )
            
#             if response.status_code != 200:
#                 return f"Error: Ollama API returned status code {response.status_code}"
            
#             return response.json().get('response', '')
#         except Exception as e:
#             return f"Error connecting to Ollama: {e}"
    
#     def get_candidate_info(self, candidate_id):
#         """Get candidate information from the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, name, email, phone, skills, experience, education, certifications
#         FROM candidates
#         WHERE id = ?
#         """, (candidate_id,))
        
#         result = cursor.fetchone()
#         conn.close()
        
#         if not result:
#             return None
        
#         return {
#             'id': result[0],
#             'name': result[1],
#             'email': result[2],
#             'phone': result[3],
#             'skills': result[4],
#             'experience': result[5],
#             'education': result[6],
#             'certifications': result[7]
#         }
    
#     def get_job_info(self, job_id):
#         """Get job information from the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, job_title, summary, required_skills, required_experience, 
#                required_qualifications, responsibilities
#         FROM job_descriptions
#         WHERE id = ?
#         """, (job_id,))
        
#         result = cursor.fetchone()
#         conn.close()
        
#         if not result:
#             return None
        
#         return {
#             'id': result[0],
#             'job_title': result[1],
#             'summary': result[2],
#             'required_skills': result[3],
#             'required_experience': result[4],
#             'required_qualifications': result[5],
#             'responsibilities': result[6]
#         }
    
#     def list_candidates(self):
#         """Get a list of all candidates in the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, name, email
#         FROM candidates
#         ORDER BY id
#         """)
        
#         results = cursor.fetchall()
#         conn.close()
        
#         candidates = []
#         for result in results:
#             candidates.append({
#                 'id': result[0],
#                 'name': result[1],
#                 'email': result[2]
#             })
        
#         return candidates
    
#     def list_jobs(self):
#         """Get a list of all jobs in the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, job_title, summary
#         FROM job_descriptions
#         ORDER BY id
#         """)
        
#         results = cursor.fetchall()
#         conn.close()
        
#         jobs = []
#         for result in results:
#             jobs.append({
#                 'id': result[0],
#                 'job_title': result[1],
#                 'summary': result[2]
#             })
        
#         return jobs
    
#     def save_uploaded_resume(self, resume_path):
#         """Save an uploaded resume to the uploads directory"""
#         if not os.path.exists(resume_path):
#             return None
        
#         # Create a unique filename based on timestamp
#         filename = f"resume_{int(time.time())}_{os.path.basename(resume_path)}"
#         destination = os.path.join(self.uploads_dir, filename)
        
#         try:
#             shutil.copy2(resume_path, destination)
#             return destination
#         except Exception as e:
#             print(f"Error saving resume: {e}")
#             return None
    
#     def process_resume(self, resume_path, candidate_name=None, candidate_email=None):
#         """Process a resume file with detailed output"""
#         # Save the resume if it's not already in our uploads directory
#         if not resume_path.startswith(self.uploads_dir):
#             saved_path = self.save_uploaded_resume(resume_path)
#             if saved_path:
#                 resume_path = saved_path
#             else:
#                 return "Error: Could not access the resume file."
        
#         # Process the resume
#         processor = self.system.processor
#         processor.verbose = True  # Enable verbose output
        
#         result = []
#         result.append(f"Processing resume: {os.path.basename(resume_path)}")
        
#         # Extract text from resume
#         resume_text = processor.extract_resume_text(resume_path)
#         if not resume_text:
#             result.append("Failed to extract text from the resume.")
#             return "\n".join(result)
        
#         result.append(f"Extracted {len(resume_text)} characters of text.")
#         result.append(f"Text sample: {resume_text[:150]}...")
        
#         # Extract candidate information
#         result.append("\nAnalyzing resume content...")
#         candidate_info = processor.extract_candidate_info(resume_text)
        
#         # IMPORTANT FIX: Only override with provided info if it's not None AND not empty
#         if candidate_name and candidate_name.strip():
#             print(f"Overriding extracted name with provided name: {candidate_name}")
#             candidate_info['name'] = candidate_name
#         if candidate_email and candidate_email.strip():
#             print(f"Overriding extracted email with provided email: {candidate_email}")
#             candidate_info['email'] = candidate_email
        
#         # Store in database
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         INSERT INTO candidates (name, email, phone, resume_text, skills, experience, education, certifications)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         """, (
#             candidate_info.get('name', ''),
#             candidate_info.get('email', ''),
#             candidate_info.get('phone', ''),
#             resume_text,
#             candidate_info.get('skills', ''),
#             candidate_info.get('experience', ''),
#             candidate_info.get('education', ''),
#             candidate_info.get('certifications', '')
#         ))
        
#         candidate_id = cursor.lastrowid
#         conn.commit()
#         conn.close()
        
#         # Update session with current candidate
#         self.session['current_candidate'] = candidate_id
#         self.session['current_resume'] = resume_path
        
#         # Get a clean version of the candidate name for display
#         candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
#         result.append(f"\nSuccessfully processed resume for {candidate_name}.")
#         result.append(f"Candidate added to database with ID: {candidate_id}")
        
#         # Display extracted information
#         result.append("\nExtracted Information:")
#         result.append(f"Name: {candidate_info.get('name', 'Not detected')}")
#         result.append(f"Email: {candidate_info.get('email', 'Not detected')}")
#         result.append(f"Phone: {candidate_info.get('phone', 'Not detected')}")
        
#         if 'skills' in candidate_info and candidate_info['skills']:
#             result.append(f"\nSkills: {candidate_info['skills']}")
        
#         if 'experience' in candidate_info and candidate_info['experience']:
#             result.append(f"\nExperience: {candidate_info['experience']}")
        
#         if 'education' in candidate_info and candidate_info['education']:
#             result.append(f"\nEducation: {candidate_info['education']}")
        
#         if 'certifications' in candidate_info and candidate_info['certifications']:
#             result.append(f"\nCertifications: {candidate_info['certifications']}")
        
#         result.append("\nYou can now analyze this candidate against available jobs by asking questions like:")
#         result.append("- \"Find suitable jobs for this candidate\"")
#         result.append("- \"Match this candidate with our open positions\"")
#         result.append("- \"What roles would be a good fit?\"")
        
#         return "\n".join(result)
    
#     def analyze_candidate(self, candidate_id=None):
#         """Match a candidate against available jobs"""
#         # Use the current candidate if none specified
#         if candidate_id is None:
#             candidate_id = self.session.get('current_candidate')
#             if not candidate_id:
#                 return "No candidate is currently selected. Please process a resume first or specify a candidate ID."
        
#         # Get candidate information
#         candidate = self.get_candidate_info(candidate_id)
#         if not candidate:
#             return f"No candidate found with ID {candidate_id}."
        
#         result = []
#         result.append(f"Analyzing matches for {candidate['name']} (ID: {candidate_id})...")
        
#         # Match against all jobs
#         matcher = self.system.matcher
#         shortlisted_jobs = matcher.match_candidate_to_all_jobs(candidate_id)
        
#         # Store in session
#         self.session['analyzed_jobs'] = [job_id for job_id, _, _ in shortlisted_jobs]
#         self.session['shortlisted_jobs'] = shortlisted_jobs
#         self.session['current_candidate'] = candidate_id  # Ensure candidate is set in session
        
#         result.append(f"\nAnalysis complete. {candidate['name']} was shortlisted for {len(shortlisted_jobs)} positions.")
        
#         if shortlisted_jobs:
#             result.append("\nYou can now schedule interviews for these positions by saying:")
#             result.append("- \"Schedule interviews for these positions\"")
#             result.append("- \"Send interview invitations\"")
#             result.append("- \"Set up interviews for the shortlisted jobs\"")
#         else:
#             result.append("\nThe candidate wasn't shortlisted for any positions. You might want to:")
#             result.append("- Process another resume")
#             result.append("- Adjust the matching threshold (currently set to {:.0f}%)".format(matcher.threshold * 100))
        
#         return "\n".join(result)
    
#     def schedule_interviews(self):
#         """Schedule interviews for shortlisted positions"""
#         # Check if we have a current candidate and shortlisted jobs
#         candidate_id = self.session.get('current_candidate')
#         shortlisted_jobs = self.session.get('shortlisted_jobs', [])
        
#         if not candidate_id:
#             return "No candidate is currently selected. Please process a resume first."
        
#         if not shortlisted_jobs:
#             return "No positions have been shortlisted. Please analyze the candidate first."
        
#         # Get candidate information
#         candidate = self.get_candidate_info(candidate_id)
#         if not candidate:
#             return "The selected candidate could not be found in the database."
        
#         result = []
#         result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
        
#         # Get the job IDs from the shortlisted jobs in the session
#         job_ids = [job_id for job_id, _, _ in shortlisted_jobs]
#         print(f"Scheduling interviews for these shortlisted positions: {job_ids}")
        
#         # Ensure matches exist and are properly marked as shortlisted
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         # First, ensure all shortlisted jobs have corresponding match entries marked as shortlisted
#         for job_id, score, reason in shortlisted_jobs:
#             cursor.execute("""
#             SELECT id FROM matches 
#             WHERE candidate_id = ? AND job_id = ?
#             """, (candidate_id, job_id))
            
#             match = cursor.fetchone()
#             if match:
#                 match_id = match[0]
#                 # Update to ensure it's marked as shortlisted
#                 cursor.execute("""
#                 UPDATE matches SET is_shortlisted = 1
#                 WHERE id = ?
#                 """, (match_id,))
#             else:
#                 # Create a match entry if it doesn't exist
#                 cursor.execute("""
#                 INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
#                 VALUES (?, ?, ?, 1)
#                 """, (job_id, candidate_id, score))
        
#         conn.commit()
        
#         # Now get all shortlisted matches for this candidate
#         cursor.execute("""
#         SELECT id, job_id FROM matches 
#         WHERE candidate_id = ? AND is_shortlisted = 1
#         """, (candidate_id,))
        
#         matches = cursor.fetchall()
        
#         if not matches:
#             result.append("\nNo matches found for scheduling. This could be because:")
#             result.append("- The interviews were already scheduled previously")
#             result.append("- There was an issue with the database")
#             conn.close()
#             return "\n".join(result)
        
#         # Schedule interviews for these matches
#         scheduler = self.system.scheduler
#         num_scheduled = 0
#         scheduled_job_ids = []
        
#         for match_id, job_id in matches:
#             print(f"Scheduling interview for match ID: {match_id}, job ID: {job_id}")
            
#             # First, mark the interview as scheduled in the database directly
#             # This ensures the interview status is updated even if email sending fails
#             cursor.execute("""
#             UPDATE matches 
#             SET interview_scheduled = 1,
#                 interview_date = ?
#             WHERE id = ?
#             """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), match_id))
#             conn.commit()
            
#             # Then try to send the email notification
#             if scheduler.schedule_interview(match_id):
#                 num_scheduled += 1
#                 scheduled_job_ids.append(job_id)
#             else:
#                 # Even if email fails, we still count this as scheduled since the DB was updated
#                 num_scheduled += 1
#                 scheduled_job_ids.append(job_id)
#                 print(f"Email notification failed for match ID: {match_id}, but interview was still scheduled")
        
#         conn.close()
        
#         # Store in session
#         self.session['scheduled_interviews'] = shortlisted_jobs
        
#         if num_scheduled > 0:
#             result.append(f"\nSuccessfully scheduled {num_scheduled} interviews for {candidate['name']}.")
#             result.append("\nInterview invitations have been sent (or would be sent if email is configured).")
#             result.append("\nThe following positions were included:")
            
#             # List all jobs that were scheduled
#             for job_id in scheduled_job_ids:
#                 job = self.get_job_info(job_id)
#                 if job:
#                     result.append(f"- {job['job_title']}")
            
#             result.append("\nWhat would you like to do next?")
#             result.append("- \"Process another resume\"")
#             result.append("- \"Show me all candidates\"")
#             result.append("- \"Show me all scheduled interviews\"")
#         else:
#             result.append("\nNo interviews were scheduled. This could be because:")
#             result.append("- The interviews were already scheduled previously")
#             result.append("- There was an issue with the email configuration")
#             result.append("- The candidate wasn't actually shortlisted for any positions")
        
#         return "\n".join(result)
    
#     def get_system_status(self):
#         """Get the current status of the recruitment system"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         # Count various metrics
#         cursor.execute("SELECT COUNT(*) FROM job_descriptions")
#         job_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM candidates")
#         candidate_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
#         shortlisted_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
#         interview_count = cursor.fetchone()[0]
        
#         conn.close()
        
#         # Get current candidate context
#         current_context = ""
#         if self.session.get('current_candidate'):
#             candidate = self.get_candidate_info(self.session['current_candidate'])
#             if candidate:
#                 current_context = f"Currently working with: {candidate['name']} (ID: {candidate['id']})"
                
#                 if self.session.get('shortlisted_jobs'):
#                     current_context += f"\nShortlisted for {len(self.session['shortlisted_jobs'])} positions"
                
#                 if self.session.get('scheduled_interviews'):
#                     current_context += f"\nInterviews scheduled for {len(self.session['scheduled_interviews'])} positions"
        
#         # Build status message
#         status = [
#             "=== RECRUITMENT SYSTEM STATUS ===",
#             f"Total Job Descriptions: {job_count}",
#             f"Total Candidates: {candidate_count}",
#             f"Total Shortlisted Matches: {shortlisted_count}",
#             f"Total Scheduled Interviews: {interview_count}",
#             "",
#             f"Ollama Model: {self.config.get('ollama_model')}",
#             f"Match Threshold: {self.config.get('match_threshold', 0.75) * 100:.0f}%",
#             f"Max Shortlisted Positions: {self.config.get('max_shortlisted', 2)}",
#             ""
#         ]
        
#         if current_context:
#             status.append("--- CURRENT SESSION ---")
#             status.append(current_context)
#             return "\n".join(status)
    
#     def update_config(self, new_settings):
#         """Update configuration settings"""
#         for key, value in new_settings.items():
#             if key in self.config:
#                 # Convert to appropriate type
#                 if key == 'match_threshold':
#                     value = float(value)
#                 elif key == 'max_shortlisted' or key == 'smtp_port':
#                     value = int(value)
                
#                 self.config[key] = value
                
#                 # Special case for threshold - also update the matcher
#                 if key == 'match_threshold' and hasattr(self.system, 'matcher'):
#                     self.system.matcher.threshold = value
                
#                 # Special case for max_shortlisted - also update the matcher
#                 if key == 'max_shortlisted' and hasattr(self.system, 'matcher'):
#                     self.system.matcher.max_shortlisted = value
        
#         # Save the updated config
#         self.save_config()
        
#         return f"Configuration updated successfully. New settings: {new_settings}"
    
#     def process_command(self, user_input):
#         """Process a natural language command with stricter parameter handling"""
#         # Add user input to history
#         self.add_to_history('user', user_input)
        
#         # Handle configuration change command
#         if "change match threshold" in user_input.lower() or "set match threshold" in user_input.lower():
#              # Extract the threshold value from the command
#             threshold_match = re.search(r'threshold\s+(?:to\s+)?(\d+(?:\.\d+)?)', user_input)
#             if threshold_match:
#                 new_threshold = float(threshold_match.group(1))
#                 # Convert percentage to decimal if needed
#                 if new_threshold > 1:
#                     new_threshold = new_threshold / 100
                
#                 response = self.update_config({'match_threshold': new_threshold})
#                 self.add_to_history('assistant', response)
#                 return response
        
#         # Map simple commands directly without using LLM to prevent default value creation
#         lower_input = user_input.lower()
        
#         # Direct command mapping for common cases
#         if "process" in lower_input and (".pdf" in lower_input or ".docx" in lower_input):
#             # Extract just the resume path without adding defaults
#             resume_path = None
            
#             # Look for PDF or DOCX file
#             file_pattern = r'([a-zA-Z0-9_\-\.]+\.(pdf|docx))'
#             file_match = re.search(file_pattern, user_input)
#             if file_match:
#                 resume_path = file_match.group(1)
                
#                 # Only process resume without any name/email override
#                 response = self.process_resume(resume_path, None, None)
#                 self.add_to_history('assistant', response)
#                 return response
                
#         # Direct handling for scheduling interviews command
#         if "schedule interview" in lower_input or "send invitation" in lower_input or "set up interview" in lower_input:
#             response = self.schedule_interviews()
#             self.add_to_history('assistant', response)
#             return response
            
#         # Direct handling for analyze candidate command
#         if "find suitable job" in lower_input or "match candidate" in lower_input or "what roles would" in lower_input:
#             response = self.analyze_candidate()
#             self.add_to_history('assistant', response)
#             return response
            
#         # For other commands, build conversation context as before
#         conversation_context = "\n".join([
#             f"{msg['speaker']}: {msg['message']}" 
#             for msg in self.conversation_history[-10:]
#         ])

#         # Get the current session state for context
#         session_context = "Current session state:\n"
#         if self.session.get('current_candidate'):
#             candidate = self.get_candidate_info(self.session['current_candidate'])
#             if candidate:
#                 session_context += f"- Working with candidate: {candidate['name']} (ID: {candidate['id']})\n"
#         if self.session.get('shortlisted_jobs'):
#             session_context += f"- Candidate has been matched with {len(self.session['shortlisted_jobs'])} positions\n which are {self.session['shortlisted_jobs']}"
#         if self.session.get('scheduled_interviews'):
#             session_context += f"- Interviews have been scheduled for {len(self.session['scheduled_interviews'])} positions\n"
        
#         # Build prompt for Ollama with VERY strict instructions about not adding defaults
#         prompt = f"""You are an AI assistant for a recruitment system. Based on the conversation history and current session state, determine what action the user wants to take.

# {session_context}

# Recent conversation:
# {conversation_context}

# User's latest message: "{user_input}"

# IMPORTANT INSTRUCTIONS:
# 1. DO NOT add any default values for parameters unless the user explicitly mentions them
# 2. For "process_resume", ONLY include "resume_path" parameter unless the user explicitly provides a name or email
# 3. NEVER create fictional candidate names or emails
# 4. If user just says "process resume X.pdf", ONLY include the resume_path

# Analyze this message and respond with a JSON object indicating the action to take and any parameters. Possible actions are:
# 1. "process_resume" - Process a resume file
# 2. "analyze_candidate" - Match a candidate with jobs
# 3. "schedule_interviews" - Schedule interviews for shortlisted positions
# 4. "list_candidates" - Show all candidates
# 5. "list_jobs" - Show all jobs
# 6. "get_candidate" - Get details for a specific candidate
# 7. "get_job" - Get details for a specific job
# 8. "system_status" - Show system status
# 9. "help" - Show help information
# 10. "unknown" - Could not determine intent

# Reply with only valid JSON. Example for resume processing:
# {{"action": "process_resume", "params": {{"resume_path": "resume.pdf"}}}}

# JSON:"""

#         # Get response from Ollama
#         llm_response = self._ollama_query(prompt)
#         print(f"Intent detection prompt response: {llm_response}")
        
#         try:
#             # Extract JSON from the response
#             json_match = re.search(r'({[\s\S]*})', llm_response)
#             if json_match:
#                 intent_data = json.loads(json_match.group(1))
#                 action = intent_data.get('action', 'unknown')
#                 params = intent_data.get('params', {})
                
#                 # Extra safety check: ensure we don't have empty params
#                 for key in list(params.keys()):
#                     if params[key] == "" or params[key] is None:
#                         del params[key]
                        
#                 # For resume processing, verify we don't have name/email unless explicitly mentioned
#                 if action == 'process_resume':
#                     # Check if the user input actually contains names or emails
#                     has_explicit_name = re.search(r'for\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', user_input) is not None
#                     has_explicit_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input) is not None
                    
#                     # Remove parameters not explicitly mentioned
#                     if not has_explicit_name and 'candidate_name' in params:
#                         print("Removing auto-generated candidate name")
#                         del params['candidate_name']
                        
#                     if not has_explicit_email and 'candidate_email' in params:
#                         print("Removing auto-generated candidate email")
#                         del params['candidate_email']
#             else:
#                 action = 'unknown'
#                 params = {}
#         except Exception as e:
#             print(f"Error parsing LLM response: {e}")
#             action = 'unknown'
#             params = {}
        
#         # Rest of the processing...
#         response = ""
        
#         if action == 'process_resume':
#             resume_path = params.get('resume_path')
#             if resume_path:
#                 # Only pass these parameters if they exist and are non-empty
#                 candidate_name = params.get('candidate_name') if 'candidate_name' in params else None
#                 candidate_email = params.get('candidate_email') if 'candidate_email' in params else None
                
#                 # Double-check to make absolutely sure we're not using empty values
#                 if candidate_name == "":
#                     candidate_name = None
#                 if candidate_email == "":
#                     candidate_email = None
                    
#                 # Debug info
#                 if candidate_name:
#                     print(f"Using explicitly provided name: {candidate_name}")
#                 if candidate_email:
#                     print(f"Using explicitly provided email: {candidate_email}")
                    
#                 response = self.process_resume(
#                     resume_path,
#                     candidate_name,
#                     candidate_email
#                 )
#             else:
#                 response = "I need a resume file to process. Please specify the path to the resume."
        
#         elif action == 'analyze_candidate':
#             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
#             if candidate_id:
#                 response = self.analyze_candidate(candidate_id)
#             else:
#                 response = "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
#         elif action == 'schedule_interviews':
#             response = self.schedule_interviews()
        
#         elif action == 'list_candidates':
#             candidates = self.list_candidates()
#             if candidates:
#                 lines = ["Here are all the candidates in the system:"]
#                 for candidate in candidates:
#                     lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
#                 response = "\n".join(lines)
#             else:
#                 response = "No candidates found in the database."
        
#         elif action == 'list_jobs':
#             jobs = self.list_jobs()
#             if jobs:
#                 lines = ["Here are all the job positions in the system:"]
#                 for job in jobs:
#                     lines.append(f"{job['id']}: {job['job_title']}")
#                     if job['summary']:
#                         summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
#                         lines.append(f"   {summary}")
#                 response = "\n".join(lines)
#             else:
#                 response = "No jobs found in the database."
        
#         elif action == 'get_candidate':
#             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
#             if candidate_id:
#                 candidate = self.get_candidate_info(candidate_id)
#                 if candidate:
#                     lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
#                     lines.append(f"Email: {candidate['email']}")
#                     lines.append(f"Phone: {candidate['phone']}")
#                     lines.append(f"\nSkills: {candidate['skills']}")
#                     lines.append(f"\nExperience: {candidate['experience']}")
#                     lines.append(f"\nEducation: {candidate['education']}")
#                     lines.append(f"\nCertifications: {candidate['certifications']}")
#                     response = "\n".join(lines)
#                 else:
#                     response = f"No candidate found with ID {candidate_id}."
#             else:
#                 response = "Please specify a candidate ID or process a resume first."
        
#         elif action == 'get_job':
#             job_id = params.get('job_id')
#             if job_id:
#                 job = self.get_job_info(job_id)
#                 if job:
#                     lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
#                     lines.append(f"\nSummary: {job['summary']}")
#                     lines.append(f"\nRequired Skills: {job['required_skills']}")
#                     lines.append(f"\nRequired Experience: {job['required_experience']}")
#                     lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
#                     lines.append(f"\nResponsibilities: {job['responsibilities']}")
#                     response = "\n".join(lines)
#                 else:
#                     response = f"No job found with ID {job_id}."
#             else:
#                 response = "Please specify a job ID."
        
#         elif action == 'system_status':
#             response = self.get_system_status()
        
#         elif action == 'help':
#             response = """
# I can help you with the following recruiting tasks:

# Resume Processing:
# - "Process resume.pdf for John Doe (john@example.com)"
# - "Extract data from the resume in path/to/file.pdf"

# Candidate Analysis:
# - "Find matching jobs for this candidate"
# - "Match this candidate with available positions"
# - "What roles would be a good fit?"

# Interview Scheduling:
# - "Schedule interviews for the shortlisted positions"
# - "Send interview invitations"
# - "Set up interviews for these jobs"

# Information Lookup:
# - "Show me all candidates"
# - "List all jobs"
# - "Show me details for candidate 3"
# - "Tell me about job position 5"

# Configuration:
# - "Change match threshold to 60%"
# - "Set threshold to 0.65"

# System Information:
# - "What's the current status?"
# - "Show system status"
# - "Who am I working with right now?"

# I maintain context throughout our conversation, so you can refer to "this candidate" or "these positions" and I'll understand based on our discussion.
# """
        
#         else:  # 'unknown' action
#             response = "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."
        
#         # Add response to history
#         self.add_to_history('assistant', response)
        
#         return response

# def main():
#     """Main entry point for the conversational recruitment system"""
#     parser = argparse.ArgumentParser(description='Conversational Recruitment System')
#     parser.add_argument('--model', default='gemma2:2b', help='Ollama model to use (default: gemma2:2b)')
#     parser.add_argument('--setup-db', action='store_true', help='Setup the database before starting')
#     parser.add_argument('--import-jobs', help='Import jobs from CSV file')
#     args = parser.parse_args()
    
#     # Setup database if requested
#     if args.setup_db:
#         print("Setting up database...")
#         setup_database('recruitment.db')
#         print("Database setup complete.")
    
#     # Import jobs if CSV provided
#     if args.import_jobs:
#         print(f"Importing jobs from {args.import_jobs}...")
#         import_jobs_from_csv('recruitment.db', args.import_jobs)
#         print("Jobs imported successfully.")
    
#     system = ConversationalRecruitmentSystem(ollama_model=args.model)
    
#     print("\n============================================")
#     print("     RECRUITMENT SYSTEM - CONVERSATION     ")
#     print("============================================")
#     print("I can help you process resumes, match candidates with jobs, and schedule interviews.")
#     print("Type 'help' for more information or 'exit' to quit.")
    
#     while True:
#         try:
#             user_input = input("\n> ")
            
#             if user_input.lower() in ['exit', 'quit', 'q']:
#                 print("Goodbye!")
#                 break
            
#             if user_input.strip():
#                 response = system.process_command(user_input)
#                 print("\n" + response)
            
#         except KeyboardInterrupt:
#             print("\nGoodbye!")
#             break
#         except Exception as e:
#             print(f"Error: {e}")
#             import traceback
#             traceback.print_exc()

# if __name__ == "__main__":
#     main()

# import argparse
# import os
# import sys
# import sqlite3
# import json
# import re
# import requests
# import tempfile
# from datetime import datetime
# import shutil
# import time

# # Ensure we can import from the current directory
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
# from db_setup import setup_database, import_jobs_from_csv



# # Custom enhanced ResumeProcessor with improved extraction
# class EnhancedResumeProcessor(ResumeProcessor):
#     def extract_candidate_info(self, resume_text):
#         """Extract candidate information from resume text with improved detection for all fields"""
#         # Initialize empty candidate info dictionary
#         candidate_info = {}
        
#         # Try regex extraction for email
#         email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
#         email_match = re.search(email_pattern, resume_text)
#         if email_match:
#             candidate_info['email'] = email_match.group(0)
#             print(f"Email extracted via regex: {candidate_info['email']}")

#         # Expanded phone patterns to catch more formats
#         phone_patterns = [
#             r'Phone:\s*([+\d\s\-()]+)',  # Match "Phone: +1-842-6155"
#             r'(\+\d{1,3}[\s-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})',  # Standard formats
#             r'(\+\d{1,3}[\s-]?\d{3,})',  # International without separators
#             r'(\d{3}[\s.-]?\d{3}[\s.-]?\d{4})'  # US format without country code
#         ]
        
#         for pattern in phone_patterns:
#             phone_match = re.search(pattern, resume_text)
#             if phone_match:
#                 # If we matched "Phone: +1-842-6155", extract just the number part
#                 if "Phone:" in pattern:
#                     candidate_info['phone'] = phone_match.group(1).strip()
#                 else:
#                     candidate_info['phone'] = phone_match.group(0).strip()
#                 print(f"Phone extracted via regex: {candidate_info['phone']}")
#                 break
        
#         # Look for "Name:" pattern in resume text
#         name_pattern = r'Name:\s*([^\n]+)'
#         name_match = re.search(name_pattern, resume_text)
#         if name_match:
#             candidate_info['name'] = name_match.group(1).strip()
#             print(f"Name extracted via regex: {candidate_info['name']}")
#         else:
#             # Create a focused prompt just for name extraction
#             name_prompt = f"""You are a recruiting expert. Extract ONLY the candidate's full name from this resume text.
#             Look at the top of the resume first, as names typically appear at the beginning.
            
#             Resume text:
#             {resume_text[:2000]}
            
#             Respond with ONLY the full name without any explanation or additional text. 
#             If you cannot determine the name with high confidence, respond with "Unknown".
#             """
            
#             name_response = self._ollama_query(name_prompt)
#             if name_response and name_response.strip() != "Unknown":
#                 candidate_info['name'] = name_response.strip()
#                 print(f"Name extracted via focused prompt: {candidate_info['name']}")
        
#         # Look for common education patterns
#         education_pattern = r'Education\s*(.+?)(?=\n\n|\n[A-Z]|$)'
#         education_match = re.search(education_pattern, resume_text, re.DOTALL)
#         if education_match:
#             # Extract just the education section text for later use
#             education_text = education_match.group(1).strip()
#             print(f"Education section found via regex")
        
#         # Now get the rest of the information with a separate prompt
#         skills_prompt = f"""You are a recruiting expert. Extract information from this resume text as JSON with the following structure:
#         {{
#             "skills": "comma-separated list of technical and soft skills",
#             "experience": "comma-separated work history with company names and roles",
#             "education": "comma-separated education details including institutions and degrees",
#             "certifications": "comma-separated list of professional certifications"
#         }}

#         Resume text:
#         {resume_text[:5000]}
        
#         Return only valid JSON. Do not include any explanation or additional text:"""
        
#         skills_response = self._ollama_query(skills_prompt)
        
#         try:
#             # Extract JSON from the response (handling potential non-JSON text around it)
#             json_match = re.search(r'({[\s\S]*})', skills_response)
#             if json_match:
#                 skills_info = json.loads(json_match.group(1))
#                 # Update candidate_info with skills_info
#                 for key, value in skills_info.items():
#                     candidate_info[key] = value
#             else:
#                 print("Failed to extract JSON from Ollama response for skills")
#         except Exception as e:
#             print(f"Error parsing skills JSON response: {e}")
        
#         # Log extraction summary
#         print("Candidate information extracted:")
#         for key, value in candidate_info.items():
#             if key == 'experience' or key == 'education':
#                 # Truncate long text fields for logging
#                 value_preview = value[:100] + "..." if value and len(value) > 100 else value
#                 print(f"- {key}: {value_preview}")
#             else:
#                 print(f"- {key}: {value}")
        
#         return candidate_info

# class EnhancedCandidateMatcher(CandidateMatcher):
#     """Enhanced candidate matcher with better matching quality"""
    
#     def match_candidate_to_job(self, candidate_id, job_id):
#         """Calculate a match score between a candidate and a job with explanation"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         # Get candidate info
#         cursor.execute("""
#         SELECT name, skills, experience, education, certifications
#         FROM candidates WHERE id = ?
#         """, (candidate_id,))
#         candidate = cursor.fetchone()
        
#         if not candidate:
#             print(f"Candidate with ID {candidate_id} not found")
#             conn.close()
#             return None, None
        
#         # Get job info
#         cursor.execute("""
#         SELECT job_title, required_skills, required_experience, required_qualifications, responsibilities
#         FROM job_descriptions WHERE id = ?
#         """, (job_id,))
#         job = cursor.fetchone()
        
#         if not job:
#             print(f"Job with ID {job_id} not found")
#             conn.close()
#             return None, None
        
#         candidate_name, candidate_skills, candidate_experience, candidate_education, candidate_certifications = candidate
#         job_title, required_skills, required_experience, required_qualifications, responsibilities = job
        
#         # Create enhanced matching prompt with improved scoring guidance
#         prompt = f"""You are a recruiting expert. Analyze how well this candidate matches the job requirements.

# Job Position: {job_title}
# Required Skills: {required_skills}
# Required Experience: {required_experience}
# Required Qualifications: {required_qualifications}
# Job Responsibilities: {responsibilities}

# Candidate Information:
# Name: {candidate_name}
# Skills: {candidate_skills}
# Experience: {candidate_experience}
# Education: {candidate_education}
# Certifications: {candidate_certifications}

# Score this match on a scale from 0.0 to 1.0 where:
# - 0.9-1.0: Perfect match with all required skills and experience
# - 0.8-0.89: Excellent match with most required skills and experience
# - 0.7-0.79: Good match with many required skills and some experience
# - 0.6-0.69: Moderate match with some skills and related experience
# - 0.5-0.59: Basic match with a few relevant skills
# - Below 0.5: Poor match

# Important: Be realistic but generous in your scoring. Focus on whether the candidate's skills and experience directly match the job requirements. For tech positions, emphasize technical skill matches.

# Format your response exactly as follows:
# SCORE: [decimal number between 0.0-1.0]
# REASONING: [2-3 sentence explanation of why they are a good match]
# """

#         # Get match score and reasoning from Ollama
#         response = self._ollama_query(prompt)
        
#         # Extract score and reasoning
#         match_score = 0.0
#         match_reasoning = ""
        
#         score_match = re.search(r'SCORE:\s*([0-9]*[.]?[0-9]+)', response)
#         if score_match:
#             try:
#                 match_score = float(score_match.group(1))
#                 # Ensure score is between 0 and 1
#                 match_score = max(0.0, min(1.0, match_score))
#             except ValueError:
#                 print("Invalid match score format from Ollama")
#                 match_score = 0.0
        
#         reasoning_match = re.search(r'REASONING:\s*(.*?)(?=$|\n\n)', response, re.DOTALL)
#         if reasoning_match:
#             match_reasoning = reasoning_match.group(1).strip()
#         else:
#             # Fallback if REASONING tag isn't found
#             match_reasoning = response.replace(f"SCORE: {match_score}", "").strip()
        
#         # Store match in database
#         cursor.execute("""
#         INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
#         VALUES (?, ?, ?, ?)
#         """, (job_id, candidate_id, match_score, 0))  # Default to not shortlisted
        
#         match_id = cursor.lastrowid
#         conn.commit()
#         conn.close()
        
#         return match_score, match_reasoning, match_id

# class ConversationalRecruitmentSystem:
#     """A conversational interface for the recruitment system that maintains context"""
    
#     def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
#         self.db_path = db_path
#         self.ollama_model = ollama_model
#         self.ollama_base_url = "http://localhost:11434/api"
        
#         # Load config
#         self.config = self.load_config()
        
#         # Initialize underlying recruitment system
#         self.system = RecruitmentSystem(
#             db_path=db_path,
#             ollama_model=self.config.get('ollama_model', ollama_model),
#             smtp_server=self.config.get('smtp_server'),
#             smtp_port=self.config.get('smtp_port', 587),
#             smtp_username=self.config.get('smtp_username'),
#             smtp_password=self.config.get('smtp_password'),
#             match_threshold=self.config.get('match_threshold', 0.75),
#             max_shortlisted=self.config.get('max_shortlisted', 2)
#         )
        
#         # Replace the default processor with our enhanced version
#         self.system.processor = EnhancedResumeProcessor(db_path, ollama_model)
        
#         # Replace the default matcher with our enhanced version
#         self.system.matcher = EnhancedCandidateMatcher(
#             db_path, 
#             ollama_model,
#             self.config.get('match_threshold', 0.75),
#             self.config.get('max_shortlisted', 2)
#         )
        
#         # Session state to maintain context
#         self.session = {
#             'current_candidate': None,  # Current candidate being discussed
#             'current_resume': None,     # Path to the current resume
#             'analyzed_jobs': [],        # Jobs that have been analyzed
#             'shortlisted_jobs': [],     # Jobs that were shortlisted
#             'scheduled_interviews': []  # Interviews that have been scheduled
#         }
        
#         # Conversation history
#         self.conversation_history = []
        
#         # File upload directory for resumes
#         self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
#         os.makedirs(self.uploads_dir, exist_ok=True)
    
#     def load_config(self):
#         """Load configuration from config.json if it exists"""
#         config = {
#             'ollama_model': 'gemma2:2b',
#             'smtp_server': None,
#             'smtp_port': 587,
#             'smtp_username': None,
#             'smtp_password': None,
#             'match_threshold': 0.75,
#             'max_shortlisted': 2
#         }
        
#         if os.path.exists('config.json'):
#             try:
#                 with open('config.json', 'r') as f:
#                     stored_config = json.load(f)
#                     config.update(stored_config)
#             except Exception as e:
#                 print(f"Error loading config: {e}")
        
#         return config
    
#     def save_config(self):
#         """Save configuration to config.json"""
#         try:
#             with open('config.json', 'w') as f:
#                 json.dump(self.config, f, indent=2)
#             return "Configuration saved successfully."
#         except Exception as e:
#             return f"Error saving configuration: {e}"
    
#     def add_to_history(self, speaker, message):
#         """Add a message to the conversation history"""
#         self.conversation_history.append({
#             'speaker': speaker,
#             'message': message,
#             'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })
    
#     def _ollama_query(self, prompt):
#         """Use the Ollama model to generate responses"""
#         try:
#             response = requests.post(
#                 f"{self.ollama_base_url}/generate",
#                 json={
#                     "model": self.config.get('ollama_model', self.ollama_model),
#                     "prompt": prompt,
#                     "stream": False
#                 }
#             )
            
#             if response.status_code != 200:
#                 return f"Error: Ollama API returned status code {response.status_code}"
            
#             return response.json().get('response', '')
#         except Exception as e:
#             return f"Error connecting to Ollama: {e}"
    
#     def get_candidate_info(self, candidate_id):
#         """Get candidate information from the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, name, email, phone, skills, experience, education, certifications
#         FROM candidates
#         WHERE id = ?
#         """, (candidate_id,))
        
#         result = cursor.fetchone()
#         conn.close()
        
#         if not result:
#             return None
        
#         return {
#             'id': result[0],
#             'name': result[1],
#             'email': result[2],
#             'phone': result[3],
#             'skills': result[4],
#             'experience': result[5],
#             'education': result[6],
#             'certifications': result[7]
#         }
    
#     def get_job_info(self, job_id):
#         """Get job information from the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, job_title, summary, required_skills, required_experience, 
#                required_qualifications, responsibilities
#         FROM job_descriptions
#         WHERE id = ?
#         """, (job_id,))
        
#         result = cursor.fetchone()
#         conn.close()
        
#         if not result:
#             return None
        
#         return {
#             'id': result[0],
#             'job_title': result[1],
#             'summary': result[2],
#             'required_skills': result[3],
#             'required_experience': result[4],
#             'required_qualifications': result[5],
#             'responsibilities': result[6]
#         }
    
#     def list_candidates(self):
#         """Get a list of all candidates in the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, name, email
#         FROM candidates
#         ORDER BY id
#         """)
        
#         results = cursor.fetchall()
#         conn.close()
        
#         candidates = []
#         for result in results:
#             candidates.append({
#                 'id': result[0],
#                 'name': result[1],
#                 'email': result[2]
#             })
        
#         return candidates
    
#     def list_jobs(self):
#         """Get a list of all jobs in the database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         SELECT id, job_title, summary
#         FROM job_descriptions
#         ORDER BY id
#         """)
        
#         results = cursor.fetchall()
#         conn.close()
        
#         jobs = []
#         for result in results:
#             jobs.append({
#                 'id': result[0],
#                 'job_title': result[1],
#                 'summary': result[2]
#             })
        
#         return jobs
    
#     def save_uploaded_resume(self, resume_path):
#         """Save an uploaded resume to the uploads directory"""
#         if not os.path.exists(resume_path):
#             return None
        
#         # Create a unique filename based on timestamp
#         filename = f"resume_{int(time.time())}_{os.path.basename(resume_path)}"
#         destination = os.path.join(self.uploads_dir, filename)
        
#         try:
#             shutil.copy2(resume_path, destination)
#             return destination
#         except Exception as e:
#             print(f"Error saving resume: {e}")
#             return None
    
#     def process_resume(self, resume_path, candidate_name=None, candidate_email=None):
#         """Process a resume file with detailed output"""
#         # Save the resume if it's not already in our uploads directory
#         if not resume_path.startswith(self.uploads_dir):
#             saved_path = self.save_uploaded_resume(resume_path)
#             if saved_path:
#                 resume_path = saved_path
#             else:
#                 return "Error: Could not access the resume file."
        
#         # Process the resume
#         processor = self.system.processor
#         processor.verbose = True  # Enable verbose output
        
#         result = []
#         result.append(f"Processing resume: {os.path.basename(resume_path)}")
        
#         # Extract text from resume
#         resume_text = processor.extract_resume_text(resume_path)
#         if not resume_text:
#             result.append("Failed to extract text from the resume.")
#             return "\n".join(result)
        
#         result.append(f"Extracted {len(resume_text)} characters of text.")
#         result.append(f"Text sample: {resume_text[:150]}...")
        
#         # Extract candidate information
#         result.append("\nAnalyzing resume content...")
#         candidate_info = processor.extract_candidate_info(resume_text)
        
#         # IMPORTANT FIX: Only override with provided info if it's not None AND not empty
#         if candidate_name and candidate_name.strip():
#             print(f"Overriding extracted name with provided name: {candidate_name}")
#             candidate_info['name'] = candidate_name
#         if candidate_email and candidate_email.strip():
#             print(f"Overriding extracted email with provided email: {candidate_email}")
#             candidate_info['email'] = candidate_email
        
#         # Store in database
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#         INSERT INTO candidates (name, email, phone, resume_text, skills, experience, education, certifications)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         """, (
#             candidate_info.get('name', ''),
#             candidate_info.get('email', ''),
#             candidate_info.get('phone', ''),
#             resume_text,
#             candidate_info.get('skills', ''),
#             candidate_info.get('experience', ''),
#             candidate_info.get('education', ''),
#             candidate_info.get('certifications', '')
#         ))
        
#         candidate_id = cursor.lastrowid
#         conn.commit()
#         conn.close()
        
#         # Update session with current candidate
#         self.session['current_candidate'] = candidate_id
#         self.session['current_resume'] = resume_path
        
#         # Get a clean version of the candidate name for display
#         candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
#         result.append(f"\nSuccessfully processed resume for {candidate_name}.")
#         result.append(f"Candidate added to database with ID: {candidate_id}")
        
#         # Display extracted information
#         result.append("\nExtracted Information:")
#         result.append(f"Name: {candidate_info.get('name', 'Not detected')}")
#         result.append(f"Email: {candidate_info.get('email', 'Not detected')}")
#         result.append(f"Phone: {candidate_info.get('phone', 'Not detected')}")
        
#         if 'skills' in candidate_info and candidate_info['skills']:
#             result.append(f"\nSkills: {candidate_info['skills']}")
        
#         if 'experience' in candidate_info and candidate_info['experience']:
#             result.append(f"\nExperience: {candidate_info['experience']}")
        
#         if 'education' in candidate_info and candidate_info['education']:
#             result.append(f"\nEducation: {candidate_info['education']}")
        
#         if 'certifications' in candidate_info and candidate_info['certifications']:
#             result.append(f"\nCertifications: {candidate_info['certifications']}")
        
#         result.append("\nYou can now analyze this candidate against available jobs by asking questions like:")
#         result.append("- \"Find suitable jobs for this candidate\"")
#         result.append("- \"Match this candidate with our open positions\"")
#         result.append("- \"What roles would be a good fit?\"")
        
#         return "\n".join(result)
    
#     def analyze_candidate(self, candidate_id=None):
#         """Match a candidate against available jobs"""
#         # Use the current candidate if none specified
#         if candidate_id is None:
#             candidate_id = self.session.get('current_candidate')
#             if not candidate_id:
#                 return "No candidate is currently selected. Please process a resume first or specify a candidate ID."
        
#         # Get candidate information
#         candidate = self.get_candidate_info(candidate_id)
#         if not candidate:
#             return f"No candidate found with ID {candidate_id}."
        
#         result = []
#         result.append(f"Analyzing matches for {candidate['name']} (ID: {candidate_id})...")
        
#         # Match against all jobs
#         matcher = self.system.matcher
#         print(f"Matching candidate {candidate_id} against {len(self.list_jobs())} jobs...")
#         shortlisted_jobs = matcher.match_candidate_to_all_jobs(candidate_id)
        
#         # Store in session
#         self.session['analyzed_jobs'] = [job_id for job_id, _, _ in shortlisted_jobs]
#         self.session['shortlisted_jobs'] = shortlisted_jobs
#         self.session['current_candidate'] = candidate_id  # Ensure candidate is set in session
        
#         result.append(f"\nAnalysis complete. {candidate['name']} was shortlisted for {len(shortlisted_jobs)} positions.")
        
#         if shortlisted_jobs:
#             result.append("\nYou can now schedule interviews for these positions by saying:")
#             result.append("- \"Schedule interviews for these positions\"")
#             result.append("- \"Send interview invitations\"")
#             result.append("- \"Set up interviews for the shortlisted jobs\"")
#         else:
#             result.append("\nThe candidate wasn't shortlisted for any positions. You might want to:")
#             result.append("- Process another resume")
#             result.append("- Adjust the matching threshold (currently set to {:.0f}%)".format(matcher.threshold * 100))
        
#         return "\n".join(result)
    
#     def schedule_interviews(self):
#         """Schedule interviews for shortlisted positions"""
#         # Check if we have a current candidate and shortlisted jobs
#         candidate_id = self.session.get('current_candidate')
#         shortlisted_jobs = self.session.get('shortlisted_jobs', [])
        
#         if not candidate_id:
#             return "No candidate is currently selected. Please process a resume first."
        
#         if not shortlisted_jobs:
#             return "No positions have been shortlisted. Please analyze the candidate first."
        
#         # Get candidate information
#         candidate = self.get_candidate_info(candidate_id)
#         if not candidate:
#             return "The selected candidate could not be found in the database."
        
#         result = []
#         result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
        
#         # Get the job IDs from the shortlisted jobs in the session
#         job_ids = [job_id for job_id, _, _ in shortlisted_jobs]
#         print(f"Scheduling interviews for these shortlisted positions: {job_ids}")
        
#         # Ensure matches exist and are properly marked as shortlisted
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         # First, ensure all shortlisted jobs have corresponding match entries marked as shortlisted
#         for job_id, score, reason in shortlisted_jobs:
#             cursor.execute("""
#             SELECT id FROM matches 
#             WHERE candidate_id = ? AND job_id = ?
#             """, (candidate_id, job_id))
            
#             match = cursor.fetchone()
#             if match:
#                 match_id = match[0]
#                 # Update to ensure it's marked as shortlisted
#                 cursor.execute("""
#                 UPDATE matches SET is_shortlisted = 1
#                 WHERE id = ?
#                 """, (match_id,))
#             else:
#                 # Create a match entry if it doesn't exist
#                 cursor.execute("""
#                 INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
#                 VALUES (?, ?, ?, 1)
#                 """, (job_id, candidate_id, score))
        
#         conn.commit()
        
#         # Now get all shortlisted matches for this candidate
#         cursor.execute("""
#         SELECT id, job_id FROM matches 
#         WHERE candidate_id = ? AND is_shortlisted = 1
#         """, (candidate_id,))
        
#         matches = cursor.fetchall()
        
#         if not matches:
#             result.append("\nNo matches found for scheduling. This could be because:")
#             result.append("- The interviews were already scheduled previously")
#             result.append("- There was an issue with the database")
#             conn.close()
#             return "\n".join(result)
        
#         # Schedule interviews for these matches
#         scheduler = self.system.scheduler
#         num_scheduled = 0
#         scheduled_job_ids = []
        
#         for match_id, job_id in matches:
#             print(f"Scheduling interview for match ID: {match_id}, job ID: {job_id}")
            
#             # First, mark the interview as scheduled in the database directly
#             # This ensures the interview status is updated even if email sending fails
#             cursor.execute("""
#             UPDATE matches 
#             SET interview_scheduled = 1,
#                 interview_date = ?
#             WHERE id = ?
#             """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), match_id))
#             conn.commit()
            
#             # Then try to send the email notification
#             if scheduler.schedule_interview(match_id):
#                 num_scheduled += 1
#                 scheduled_job_ids.append(job_id)
#             else:
#                 # Even if email fails, we still count this as scheduled since the DB was updated
#                 num_scheduled += 1
#                 scheduled_job_ids.append(job_id)
#                 print(f"Email notification failed for match ID: {match_id}, but interview was still scheduled")
        
#         conn.close()
        
#         # Store in session
#         self.session['scheduled_interviews'] = shortlisted_jobs
        
#         if num_scheduled > 0:
#             result.append(f"\nSuccessfully scheduled {num_scheduled} interviews for {candidate['name']}.")
#             result.append("\nInterview invitations have been sent (or would be sent if email is configured).")
#             result.append("\nThe following positions were included:")
            
#             # List all jobs that were scheduled
#             for job_id in scheduled_job_ids:
#                 job = self.get_job_info(job_id)
#                 if job:
#                     result.append(f"- {job['job_title']}")
            
#             result.append("\nWhat would you like to do next?")
#             result.append("- \"Process another resume\"")
#             result.append("- \"Show me all candidates\"")
#             result.append("- \"Show me all scheduled interviews\"")
#         else:
#             result.append("\nNo interviews were scheduled. This could be because:")
#             result.append("- The interviews were already scheduled previously")
#             result.append("- There was an issue with the email configuration")
#             result.append("- The candidate wasn't actually shortlisted for any positions")
        
#         return "\n".join(result)
    
#     def get_system_status(self):
#         """Get the current status of the recruitment system"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         # Count various metrics
#         cursor.execute("SELECT COUNT(*) FROM job_descriptions")
#         job_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM candidates")
#         candidate_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
#         shortlisted_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
#         interview_count = cursor.fetchone()[0]
        
#         conn.close()
        
#         # Get current candidate context
#         current_context = ""
#         if self.session.get('current_candidate'):
#             candidate = self.get_candidate_info(self.session['current_candidate'])
#             if candidate:
#                 current_context = f"Currently working with: {candidate['name']} (ID: {candidate['id']})"
                
#                 if self.session.get('shortlisted_jobs'):
#                     current_context += f"\nShortlisted for {len(self.session['shortlisted_jobs'])} positions"
                
#                 if self.session.get('scheduled_interviews'):
#                     current_context += f"\nInterviews scheduled for {len(self.session['scheduled_interviews'])} positions"
        
#         # Build status message
#         status = [
#             "=== RECRUITMENT SYSTEM STATUS ===",
#             f"Total Job Descriptions: {job_count}",
#             f"Total Candidates: {candidate_count}",
#             f"Total Shortlisted Matches: {shortlisted_count}",
#             f"Total Scheduled Interviews: {interview_count}",
#             "",
#             f"Ollama Model: {self.config.get('ollama_model')}",
#             f"Match Threshold: {self.config.get('match_threshold', 0.75) * 100:.0f}%",
#             f"Max Shortlisted Positions: {self.config.get('max_shortlisted', 2)}",
#             ""
#         ]
        
#         if current_context:
#             status.append("--- CURRENT SESSION ---")
#             status.append(current_context)
        
#         return "\n".join(status)
    
#     def update_config(self, new_settings):
#         """Update configuration settings"""
#         for key, value in new_settings.items():
#             if key in self.config:
#                 # Convert to appropriate type
#                 if key == 'match_threshold':
#                     value = float(value)
#                 elif key == 'max_shortlisted' or key == 'smtp_port':
#                     value = int(value)
                
#                 self.config[key] = value
                
#                 # Special case for threshold - also update the matcher
#                 if key == 'match_threshold' and hasattr(self.system, 'matcher'):
#                     self.system.matcher.threshold = value
                
#                 # Special case for max_shortlisted - also update the matcher
#                 if key == 'max_shortlisted' and hasattr(self.system, 'matcher'):
#                     self.system.matcher.max_shortlisted = value
        
#         # Save the updated config
#         self.save_config()
        
#         return f"Configuration updated successfully. New settings: {new_settings}"
    
#     def get_help_text(self):
#         """Return the help text for the system"""
#         return """
# I can help you with the following recruiting tasks:

# Resume Processing:
# - "Process resume.pdf for John Doe (john@example.com)"
# - "Extract data from the resume in path/to/file.pdf"

# Candidate Analysis:
# - "Find matching jobs for this candidate"
# - "Match this candidate with available positions"
# - "What roles would be a good fit?"

# Interview Scheduling:
# - "Schedule interviews for the shortlisted positions"
# - "Send interview invitations"
# - "Set up interviews for these jobs"

# Information Lookup:
# - "Show me all candidates"
# - "List all jobs"
# - "Show me details for candidate 3"
# - "Tell me about job position 5"

# Configuration:
# - "Change match threshold to 60%"
# - "Set threshold to 0.65"

# System Information:
# - "What's the current status?"
# - "Show system status"
# - "Who am I working with right now?"

# I maintain context throughout our conversation, so you can refer to "this candidate" or "these positions" and I'll understand based on our discussion.
# """
            
#     def process_intent_with_llm(self, user_input):
#         """Use LLM to determine user intent for more complex commands"""
#         # Build conversation context
#         conversation_context = "\n".join([
#             f"{msg['speaker']}: {msg['message']}" 
#             for msg in self.conversation_history[-10:]
#         ])

#         # Get the current session state for context
#         session_context = "Current session state:\n"
#         if self.session.get('current_candidate'):
#             candidate = self.get_candidate_info(self.session['current_candidate'])
#             if candidate:
#                 session_context += f"- Working with candidate: {candidate['name']} (ID: {candidate['id']})\n"
#         if self.session.get('shortlisted_jobs'):
#             session_context += f"- Candidate has been matched with {len(self.session['shortlisted_jobs'])} positions\n"
#         if self.session.get('scheduled_interviews'):
#             session_context += f"- Interviews have been scheduled for {len(self.session['scheduled_interviews'])} positions\n"
        
#         # Build prompt for Ollama with VERY strict instructions
#         prompt = f"""You are an AI assistant for a recruitment system. Based on the conversation history and current session state, determine what action the user wants to take.

# {session_context}

# Recent conversation:
# {conversation_context}

# User's latest message: "{user_input}"

# IMPORTANT INSTRUCTIONS:
# 1. DO NOT add any default values for parameters unless the user explicitly mentions them
# 2. For "process_resume", ONLY include "resume_path" parameter unless the user explicitly provides a name or email
# 3. NEVER create fictional candidate names or emails
# 4. If user just says "process resume X.pdf", ONLY include the resume_path
# 5. If the message mentions "schedule interview", "send invitation", or anything about interviews, ALWAYS choose "schedule_interviews" action with no parameters
# 6. If the message mentions finding jobs or matching candidates, ALWAYS choose "analyze_candidate" action with no parameters

# Analyze this message and respond with a JSON object indicating the action to take and any parameters. Possible actions are:
# 1. "process_resume" - Process a resume file
# 2. "analyze_candidate" - Match a candidate with jobs
# 3. "schedule_interviews" - Schedule interviews for shortlisted positions
# 4. "list_candidates" - Show all candidates
# 5. "list_jobs" - Show all jobs
# 6. "get_candidate" - Get details for a specific candidate
# 7. "get_job" - Get details for a specific job
# 8. "system_status" - Show system status
# 9. "help" - Show help information
# 10. "unknown" - Could not determine intent

# Reply with only valid JSON. Example for resume processing:
# {{"action": "process_resume", "params": {{"resume_path": "resume.pdf"}}}}

# JSON:"""

#         # Get response from Ollama
#         llm_response = self._ollama_query(prompt)
#         print(f"Intent detection prompt response: {llm_response}")
        
#         # Use LLM for intent detection for commands not caught by direct matching
#         try:
#             # Extract JSON from the response
#             json_match = re.search(r'({[\s\S]*})', llm_response)
#             if json_match:
#                 intent_data = json.loads(json_match.group(1))
#                 action = intent_data.get('action', 'unknown')
#                 params = intent_data.get('params', {})
                
#                 # Extra safety check: ensure we don't have empty params
#                 for key in list(params.keys()):
#                     if params[key] == "" or params[key] is None:
#                         del params[key]
                        
#                 # For resume processing, verify we don't have name/email unless explicitly mentioned
#                 if action == 'process_resume':
#                     # Check if the user input actually contains names or emails
#                     has_explicit_name = re.search(r'for\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', user_input) is not None
#                     has_explicit_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input) is not None
                    
#                     # Remove parameters not explicitly mentioned
#                     if not has_explicit_name and 'candidate_name' in params:
#                         print("Removing auto-generated candidate name")
#                         del params['candidate_name']
                        
#                     if not has_explicit_email and 'candidate_email' in params:
#                         print("Removing auto-generated candidate email")
#                         del params['candidate_email']
                
#                 # CRITICAL FIX: Double check interview scheduling intent
#                 # If there are keywords related to scheduling but action isn't set correctly
#                 interview_keywords = ["interview", "schedule", "invitation", "invite", "meeting"]
#                 if any(keyword in user_input.lower() for keyword in interview_keywords) and action != "schedule_interviews":
#                     print("Keyword match for interviews found, overriding action to schedule_interviews")
#                     action = "schedule_interviews"
#                     params = {}
#             else:
#                 action = 'unknown'
#                 params = {}
#         except Exception as e:
#             print(f"Error parsing LLM response: {e}")
#             action = 'unknown'
#             params = {}
            
#         return action, params
    
#     def process_command(self, user_input):
#         """Process a natural language command with stricter parameter handling"""
#         # Add user input to history
#         self.add_to_history('user', user_input)
        
#         # Handle configuration change command
#         if "change match threshold" in user_input.lower() or "set match threshold" in user_input.lower():
#              # Extract the threshold value from the command
#             threshold_match = re.search(r'threshold\s+(?:to\s+)?(\d+(?:\.\d+)?)', user_input)
#             if threshold_match:
#                 new_threshold = float(threshold_match.group(1))
#                 # Convert percentage to decimal if needed
#                 if new_threshold > 1:
#                     new_threshold = new_threshold / 100
                
#                 response = self.update_config({'match_threshold': new_threshold})
#                 self.add_to_history('assistant', response)
#                 return response
        
#         # Map simple commands directly without using LLM to prevent default value creation
#         lower_input = user_input.lower()
        
#         # === DIRECT COMMAND MAPPING FOR COMMON OPERATIONS ===
#         # These bypass the LLM intent detection to improve reliability
        
#         # 1. Resume processing direct command detection
#         if "process" in lower_input and (".pdf" in lower_input or ".docx" in lower_input):
#             # Extract just the resume path without adding defaults
#             resume_path = None
            
#             # Look for PDF or DOCX file
#             file_pattern = r'([a-zA-Z0-9_\-\.]+\.(pdf|docx))'
#             file_match = re.search(file_pattern, user_input)
#             if file_match:
#                 resume_path = file_match.group(1)
                
#                 # Only process resume without any name/email override
#                 response = self.process_resume(resume_path, None, None)
#                 self.add_to_history('assistant', response)
#                 return response
        
#         # 2. Interview scheduling direct command detection
#         # Check for any of the common phrases that indicate interview scheduling intent
#         interview_phrases = [
#             "schedule interview", "send invitation", "set up interview", 
#             "schedule meeting", "send invites", "setup interviews",
#             "invite candidate", "schedule the interview", "send the invitation"
#         ]
#         if any(phrase in lower_input for phrase in interview_phrases):
#             print("Direct command match: Scheduling interviews")
#             response = self.schedule_interviews()
#             self.add_to_history('assistant', response)
#             return response
        
#         # 3. Candidate analysis direct command detection
#         analysis_phrases = [
#             "find suitable job", "match candidate", "what roles would", 
#             "find matching job", "analyze candidate", "check job matches", 
#             "find positions", "identify jobs", "suitable position"
#         ]
#         if any(phrase in lower_input for phrase in analysis_phrases):
#             print("Direct command match: Analyzing candidate")
#             response = self.analyze_candidate()
#             self.add_to_history('assistant', response)
#             return response
        
#         # 4. System status direct command detection
#         if "status" in lower_input or "system info" in lower_input:
#             print("Direct command match: System status")
#             response = self.get_system_status()
#             self.add_to_history('assistant', response)
#             return response
        
#         # 5. Help command direct detection
#         if lower_input == "help" or "show commands" in lower_input:
#             print("Direct command match: Help")
#             response = self.get_help_text()
#             self.add_to_history('assistant', response)
#             return response
            
#         # 6. List candidates direct detection
#         if "list candidates" in lower_input or "show candidates" in lower_input or "all candidates" in lower_input:
#             candidates = self.list_candidates()
#             if candidates:
#                 lines = ["Here are all the candidates in the system:"]
#                 for candidate in candidates:
#                     lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
#                 response = "\n".join(lines)
#             else:
#                 response = "No candidates found in the database."
#             self.add_to_history('assistant', response)
#             return response
            
#         # 7. List jobs direct detection
#         if "list jobs" in lower_input or "show jobs" in lower_input or "all jobs" in lower_input or "available jobs" in lower_input:
#             jobs = self.list_jobs()
#             if jobs:
#                 lines = ["Here are all the job positions in the system:"]
#                 for job in jobs:
#                     lines.append(f"{job['id']}: {job['job_title']}")
#                     if job['summary']:
#                         summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
#                         lines.append(f"   {summary}")
#                 response = "\n".join(lines)
#             else:
#                 response = "No jobs found in the database."
#             self.add_to_history('assistant', response)
#             return response
            
#         # For more complex commands, use LLM-based intent detection
#         action, params = self.process_intent_with_llm(user_input)
        
#         # Execute the identified action
#         print(f"Executing action: {action} with params: {params}")
#         response = self.execute_action(action, params, user_input)
        
#         # Add response to history
#         self.add_to_history('assistant', response)
        
#         return response
        
#     def execute_action(self, action, params, original_input):
#         """Execute the identified action with the given parameters"""
#         if action == 'process_resume':
#             resume_path = params.get('resume_path')
#             if resume_path:
#                 # Only pass these parameters if they exist and are non-empty
#                 candidate_name = params.get('candidate_name') if 'candidate_name' in params else None
#                 candidate_email = params.get('candidate_email') if 'candidate_email' in params else None
                
#                 # Double-check to make absolutely sure we're not using empty values
#                 if candidate_name == "":
#                     candidate_name = None
#                 if candidate_email == "":
#                     candidate_email = None
                    
#                 # Debug info
#                 if candidate_name:
#                     print(f"Using explicitly provided name: {candidate_name}")
#                 if candidate_email:
#                     print(f"Using explicitly provided email: {candidate_email}")
                    
#                 return self.process_resume(
#                     resume_path,
#                     candidate_name,
#                     candidate_email
#                 )
#             else:
#                 return "I need a resume file to process. Please specify the path to the resume."
        
#         elif action == 'analyze_candidate':
#             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
#             if candidate_id:
#                 return self.analyze_candidate(candidate_id)
#             else:
#                 return "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
#         elif action == 'schedule_interviews':
#             # This is the critical fix - directly call schedule_interviews regardless of parameters
#             return self.schedule_interviews()
        
#         elif action == 'list_candidates':
#             candidates = self.list_candidates()
#             if candidates:
#                 lines = ["Here are all the candidates in the system:"]
#                 for candidate in candidates:
#                     lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
#                 return "\n".join(lines)
#             else:
#                 return "No candidates found in the database."
        
#         elif action == 'list_jobs':
#             jobs = self.list_jobs()
#             if jobs:
#                 lines = ["Here are all the job positions in the system:"]
#                 for job in jobs:
#                     lines.append(f"{job['id']}: {job['job_title']}")
#                     if job['summary']:
#                         summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
#                         lines.append(f"   {summary}")
#                 return "\n".join(lines)
#             else:
#                 return "No jobs found in the database."
        
#         elif action == 'get_candidate':
#             candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
#             if candidate_id:
#                 candidate = self.get_candidate_info(candidate_id)
#                 if candidate:
#                     lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
#                     lines.append(f"Email: {candidate['email']}")
#                     lines.append(f"Phone: {candidate['phone']}")
#                     lines.append(f"\nSkills: {candidate['skills']}")
#                     lines.append(f"\nExperience: {candidate['experience']}")
#                     lines.append(f"\nEducation: {candidate['education']}")
#                     lines.append(f"\nCertifications: {candidate['certifications']}")
#                     return "\n".join(lines)
#                 else:
#                     return f"No candidate found with ID {candidate_id}."
#             else:
#                 return "Please specify a candidate ID or process a resume first."
        
#         elif action == 'get_job':
#             job_id = params.get('job_id')
#             if job_id:
#                 job = self.get_job_info(job_id)
#                 if job:
#                     lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
#                     lines.append(f"\nSummary: {job['summary']}")
#                     lines.append(f"\nRequired Skills: {job['required_skills']}")
#                     lines.append(f"\nRequired Experience: {job['required_experience']}")
#                     lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
#                     lines.append(f"\nResponsibilities: {job['responsibilities']}")
#                     return "\n".join(lines)
#                 else:
#                     return f"No job found with ID {job_id}."
#             else:
#                 return "Please specify a job ID."
        
#         elif action == 'system_status':
#             return self.get_system_status()
        
#         elif action == 'help':
#             return self.get_help_text()
        
#         else:  # 'unknown' action
#             return "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."


# def main():
#     """Main entry point for the conversational recruitment system"""
#     parser = argparse.ArgumentParser(description='Conversational Recruitment System')
#     parser.add_argument('--model', default='gemma2:2b', help='Ollama model to use (default: gemma2:2b)')
#     parser.add_argument('--setup-db', action='store_true', help='Setup the database before starting')
#     parser.add_argument('--import-jobs', help='Import jobs from CSV file')
#     args = parser.parse_args()
    
#     # Setup database if requested
#     if args.setup_db:
#         print("Setting up database...")
#         setup_database('recruitment.db')
#         print("Database setup complete.")
    
#     # Import jobs if CSV provided
#     if args.import_jobs:
#         print(f"Importing jobs from {args.import_jobs}...")
#         import_jobs_from_csv('recruitment.db', args.import_jobs)
#         print("Jobs imported successfully.")
    
#     system = ConversationalRecruitmentSystem(ollama_model=args.model)
    
#     print("\n============================================")
#     print("     RECRUITMENT SYSTEM - CONVERSATION     ")
#     print("============================================")
#     print("I can help you process resumes, match candidates with jobs, and schedule interviews.")
#     print("Type 'help' for more information or 'exit' to quit.")
    
#     while True:
#         try:
#             user_input = input("\n> ")
            
#             if user_input.lower() in ['exit', 'quit', 'q']:
#                 print("Goodbye!")
#                 break
            
#             if user_input.strip():
#                 response = system.process_command(user_input)
#                 print("\n" + response)
            
#         except KeyboardInterrupt:
#             print("\nGoodbye!")
#             break
#         except Exception as e:
#             print(f"Error: {e}")
#             import traceback
#             traceback.print_exc()

# if __name__ == "__main__":
#     main()


import argparse
import os
import sys
import sqlite3
import json
import re
import requests
import tempfile
from datetime import datetime, timedelta
import shutil
import time

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
from db_setup import setup_database, import_jobs_from_csv



# Custom enhanced ResumeProcessor with improved extraction
class EnhancedResumeProcessor(ResumeProcessor):
    def extract_candidate_info(self, resume_text):
        """Extract candidate information from resume text with improved detection for all fields"""
        # Initialize empty candidate info dictionary
        candidate_info = {}
        
        # Try regex extraction for email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            candidate_info['email'] = email_match.group(0)
            print(f"Email extracted via regex: {candidate_info['email']}")

        # Expanded phone patterns to catch more formats
        phone_patterns = [
            r'Phone:\s*([+\d\s\-()]+)',  # Match "Phone: +1-842-6155"
            r'(\+\d{1,3}[\s-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})',  # Standard formats
            r'(\+\d{1,3}[\s-]?\d{3,})',  # International without separators
            r'(\d{3}[\s.-]?\d{3}[\s.-]?\d{4})'  # US format without country code
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, resume_text)
            if phone_match:
                # If we matched "Phone: +1-842-6155", extract just the number part
                if "Phone:" in pattern:
                    candidate_info['phone'] = phone_match.group(1).strip()
                else:
                    candidate_info['phone'] = phone_match.group(0).strip()
                print(f"Phone extracted via regex: {candidate_info['phone']}")
                break
        
        # Look for "Name:" pattern in resume text
        name_pattern = r'Name:\s*([^\n]+)'
        name_match = re.search(name_pattern, resume_text)
        if name_match:
            candidate_info['name'] = name_match.group(1).strip()
            print(f"Name extracted via regex: {candidate_info['name']}")
        else:
            # Create a focused prompt just for name extraction
            name_prompt = f"""You are a recruiting expert. Extract ONLY the candidate's full name from this resume text.
            Look at the top of the resume first, as names typically appear at the beginning.
            
            Resume text:
            {resume_text[:2000]}
            
            Respond with ONLY the full name without any explanation or additional text. 
            If you cannot determine the name with high confidence, respond with "Unknown".
            """
            
            name_response = self._ollama_query(name_prompt)
            if name_response and name_response.strip() != "Unknown":
                candidate_info['name'] = name_response.strip()
                print(f"Name extracted via focused prompt: {candidate_info['name']}")
        
        # Look for common education patterns
        education_pattern = r'Education\s*(.+?)(?=\n\n|\n[A-Z]|$)'
        education_match = re.search(education_pattern, resume_text, re.DOTALL)
        if education_match:
            # Extract just the education section text for later use
            education_text = education_match.group(1).strip()
            print(f"Education section found via regex")
        
        # Now get the rest of the information with a separate prompt
        skills_prompt = f"""You are a recruiting expert. Extract information from this resume text as JSON with the following structure:
        {{
            "skills": "comma-separated list of technical and soft skills",
            "experience": "comma-separated work history with company names and roles",
            "education": "comma-separated education details including institutions and degrees",
            "certifications": "comma-separated list of professional certifications"
        }}

        Resume text:
        {resume_text[:5000]}
        
        Return only valid JSON. Do not include any explanation or additional text:"""
        
        skills_response = self._ollama_query(skills_prompt)
        
        try:
            # Extract JSON from the response (handling potential non-JSON text around it)
            json_match = re.search(r'({[\s\S]*})', skills_response)
            if json_match:
                skills_info = json.loads(json_match.group(1))
                # Update candidate_info with skills_info
                for key, value in skills_info.items():
                    candidate_info[key] = value
            else:
                print("Failed to extract JSON from Ollama response for skills")
        except Exception as e:
            print(f"Error parsing skills JSON response: {e}")
        
        # Log extraction summary
        print("Candidate information extracted:")
        for key, value in candidate_info.items():
            if key == 'experience' or key == 'education':
                # Truncate long text fields for logging
                value_preview = value[:100] + "..." if value and len(value) > 100 else value
                print(f"- {key}: {value_preview}")
            else:
                print(f"- {key}: {value}")
        
        return candidate_info

class EnhancedCandidateMatcher(CandidateMatcher):
    """Enhanced candidate matcher with better matching quality"""
    
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
        
        # Create enhanced matching prompt with improved scoring guidance
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

Score this match on a scale from 0.0 to 1.0 where:
- 0.9-1.0: Perfect match with all required skills and experience
- 0.8-0.89: Excellent match with most required skills and experience
- 0.7-0.79: Good match with many required skills and some experience
- 0.6-0.69: Moderate match with some skills and related experience
- 0.5-0.59: Basic match with a few relevant skills
- Below 0.5: Poor match

Important: Be realistic but generous in your scoring. Focus on whether the candidate's skills and experience directly match the job requirements. For tech positions, emphasize technical skill matches.

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
        
        # Store match in database
        cursor.execute("""
        INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
        VALUES (?, ?, ?, ?)
        """, (job_id, candidate_id, match_score, 0))  # Default to not shortlisted
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return match_score, match_reasoning, match_id

class ConversationalRecruitmentSystem:
    """A conversational interface for the recruitment system that maintains context"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
        self.db_path = db_path
        self.ollama_model = ollama_model
        self.ollama_base_url = "http://localhost:11434/api"
        
        # Load config
        self.config = self.load_config()
        
        # Initialize underlying recruitment system
        self.system = RecruitmentSystem(
            db_path=db_path,
            ollama_model=self.config.get('ollama_model', ollama_model),
            smtp_server=self.config.get('smtp_server'),
            smtp_port=self.config.get('smtp_port', 587),
            smtp_username=self.config.get('smtp_username'),
            smtp_password=self.config.get('smtp_password'),
            match_threshold=self.config.get('match_threshold', 0.75),
            max_shortlisted=self.config.get('max_shortlisted', 2)
        )
        
        # Replace the default processor with our enhanced version
        self.system.processor = EnhancedResumeProcessor(db_path, ollama_model)
        
        # Replace the default matcher with our enhanced version
        self.system.matcher = EnhancedCandidateMatcher(
            db_path, 
            ollama_model,
            self.config.get('match_threshold', 0.75),
            self.config.get('max_shortlisted', 2)
        )
        
        # Session state to maintain context
        self.session = {
            'current_candidate': None,  # Current candidate being discussed
            'current_resume': None,     # Path to the current resume
            'analyzed_jobs': [],        # Jobs that have been analyzed
            'shortlisted_jobs': [],     # Jobs that were shortlisted
            'scheduled_interviews': []  # Interviews that have been scheduled
        }
        
        # Conversation history
        self.conversation_history = []
        
        # File upload directory for resumes
        self.uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(self.uploads_dir, exist_ok=True)
    
    def load_config(self):
        """Load configuration from config.json if it exists"""
        config = {
            'ollama_model': 'gemma2:2b',
            'smtp_server': None,
            'smtp_port': 587,
            'smtp_username': None,
            'smtp_password': None,
            'match_threshold': 0.75,
            'max_shortlisted': 2
        }
        
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r') as f:
                    stored_config = json.load(f)
                    config.update(stored_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return config
    
    def save_config(self):
        """Save configuration to config.json"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            return "Configuration saved successfully."
        except Exception as e:
            return f"Error saving configuration: {e}"
    
    def add_to_history(self, speaker, message):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            'speaker': speaker,
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def _ollama_query(self, prompt):
        """Use the Ollama model to generate responses"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/generate",
                json={
                    "model": self.config.get('ollama_model', self.ollama_model),
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                return f"Error: Ollama API returned status code {response.status_code}"
            
            return response.json().get('response', '')
        except Exception as e:
            return f"Error connecting to Ollama: {e}"
    
    def get_candidate_info(self, candidate_id):
        """Get candidate information from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, email, phone, skills, experience, education, certifications
        FROM candidates
        WHERE id = ?
        """, (candidate_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'id': result[0],
            'name': result[1],
            'email': result[2],
            'phone': result[3],
            'skills': result[4],
            'experience': result[5],
            'education': result[6],
            'certifications': result[7]
        }
    
    def get_job_info(self, job_id):
        """Get job information from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, job_title, summary, required_skills, required_experience, 
               required_qualifications, responsibilities
        FROM job_descriptions
        WHERE id = ?
        """, (job_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'id': result[0],
            'job_title': result[1],
            'summary': result[2],
            'required_skills': result[3],
            'required_experience': result[4],
            'required_qualifications': result[5],
            'responsibilities': result[6]
        }
    
    def list_candidates(self):
        """Get a list of all candidates in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, email
        FROM candidates
        ORDER BY id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        candidates = []
        for result in results:
            candidates.append({
                'id': result[0],
                'name': result[1],
                'email': result[2]
            })
        
        return candidates
    
    def list_jobs(self):
        """Get a list of all jobs in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, job_title, summary
        FROM job_descriptions
        ORDER BY id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        jobs = []
        for result in results:
            jobs.append({
                'id': result[0],
                'job_title': result[1],
                'summary': result[2]
            })
        
        return jobs
    
    def save_uploaded_resume(self, resume_path):
        """Save an uploaded resume to the uploads directory"""
        if not os.path.exists(resume_path):
            return None
        
        # Create a unique filename based on timestamp
        filename = f"resume_{int(time.time())}_{os.path.basename(resume_path)}"
        destination = os.path.join(self.uploads_dir, filename)
        
        try:
            shutil.copy2(resume_path, destination)
            return destination
        except Exception as e:
            print(f"Error saving resume: {e}")
            return None
    
    def process_resume(self, resume_path, candidate_name=None, candidate_email=None):
        """Process a resume file with detailed output"""
        # Save the resume if it's not already in our uploads directory
        if not resume_path.startswith(self.uploads_dir):
            saved_path = self.save_uploaded_resume(resume_path)
            if saved_path:
                resume_path = saved_path
            else:
                return "Error: Could not access the resume file."
        
        # Process the resume
        processor = self.system.processor
        processor.verbose = True  # Enable verbose output
        
        result = []
        result.append(f"Processing resume: {os.path.basename(resume_path)}")
        
        # Extract text from resume
        resume_text = processor.extract_resume_text(resume_path)
        if not resume_text:
            result.append("Failed to extract text from the resume.")
            return "\n".join(result)
        
        result.append(f"Extracted {len(resume_text)} characters of text.")
        result.append(f"Text sample: {resume_text[:150]}...")
        
        # Extract candidate information
        result.append("\nAnalyzing resume content...")
        candidate_info = processor.extract_candidate_info(resume_text)
        
        # IMPORTANT FIX: Only override with provided info if it's not None AND not empty
        if candidate_name and candidate_name.strip():
            print(f"Overriding extracted name with provided name: {candidate_name}")
            candidate_info['name'] = candidate_name
        if candidate_email and candidate_email.strip():
            print(f"Overriding extracted email with provided email: {candidate_email}")
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
        
        # Update session with current candidate
        self.session['current_candidate'] = candidate_id
        self.session['current_resume'] = resume_path
        
        # Get a clean version of the candidate name for display
        candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
        result.append(f"\nSuccessfully processed resume for {candidate_name}.")
        result.append(f"Candidate added to database with ID: {candidate_id}")
        
        # Display extracted information
        result.append("\nExtracted Information:")
        result.append(f"Name: {candidate_info.get('name', 'Not detected')}")
        result.append(f"Email: {candidate_info.get('email', 'Not detected')}")
        result.append(f"Phone: {candidate_info.get('phone', 'Not detected')}")
        
        if 'skills' in candidate_info and candidate_info['skills']:
            result.append(f"\nSkills: {candidate_info['skills']}")
        
        if 'experience' in candidate_info and candidate_info['experience']:
            result.append(f"\nExperience: {candidate_info['experience']}")
        
        if 'education' in candidate_info and candidate_info['education']:
            result.append(f"\nEducation: {candidate_info['education']}")
        
        if 'certifications' in candidate_info and candidate_info['certifications']:
            result.append(f"\nCertifications: {candidate_info['certifications']}")
        
        result.append("\nYou can now analyze this candidate against available jobs by asking questions like:")
        result.append("- \"Find suitable jobs for this candidate\"")
        result.append("- \"Match this candidate with our open positions\"")
        result.append("- \"What roles would be a good fit?\"")
        
        return "\n".join(result)
    
    def analyze_candidate(self, candidate_id=None):
        """Match a candidate against available jobs"""
        # Use the current candidate if none specified
        if candidate_id is None:
            candidate_id = self.session.get('current_candidate')
            if not candidate_id:
                return "No candidate is currently selected. Please process a resume first or specify a candidate ID."
        
        # Get candidate information
        candidate = self.get_candidate_info(candidate_id)
        if not candidate:
            return f"No candidate found with ID {candidate_id}."
        
        result = []
        result.append(f"Analyzing matches for {candidate['name']} (ID: {candidate_id})...")
        
        # Match against all jobs
        matcher = self.system.matcher
        print(f"Matching candidate {candidate_id} against {len(self.list_jobs())} jobs...")
        shortlisted_jobs = matcher.match_candidate_to_all_jobs(candidate_id)
        
        # Store in session
        self.session['analyzed_jobs'] = [job_id for job_id, _, _ in shortlisted_jobs]
        self.session['shortlisted_jobs'] = shortlisted_jobs
        self.session['current_candidate'] = candidate_id  # Ensure candidate is set in session
        
        result.append(f"\nAnalysis complete. {candidate['name']} was shortlisted for {len(shortlisted_jobs)} positions.")
        
        if shortlisted_jobs:
            result.append("\nYou can now schedule interviews for these positions by saying:")
            result.append("- \"Schedule interviews for these positions\"")
            result.append("- \"Send interview invitations\"")
            result.append("- \"Set up interviews for the shortlisted jobs\"")
        else:
            result.append("\nThe candidate wasn't shortlisted for any positions. You might want to:")
            result.append("- Process another resume")
            result.append("- Adjust the matching threshold (currently set to {:.0f}%)".format(matcher.threshold * 100))
        
        return "\n".join(result)
    
    def schedule_interviews(self, custom_dates=None, custom_times=None):
        """Schedule interviews for shortlisted positions
        
        Args:
            custom_dates: List of specific dates in format 'YYYY-MM-DD'
            custom_times: List of specific times in format 'HH:MM' (24-hour format)
            
        Returns:
            String response with scheduling results
        """
        # Check if we have a current candidate and shortlisted jobs
        candidate_id = self.session.get('current_candidate')
        shortlisted_jobs = self.session.get('shortlisted_jobs', [])
        
        if not candidate_id:
            return "No candidate is currently selected. Please process a resume first."
        
        if not shortlisted_jobs:
            return "No positions have been shortlisted. Please analyze the candidate first."
        
        # Get candidate information
        candidate = self.get_candidate_info(candidate_id)
        if not candidate:
            return "The selected candidate could not be found in the database."
        
        result = []
        
        # Display chosen date/time information if provided
        if custom_dates and custom_times:
            result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
            result.append("\nUsing custom interview schedule:")
            for date_str in custom_dates:
                for time_str in custom_times:
                    try:
                        # Validate date/time format
                        year, month, day = map(int, date_str.split('-'))
                        hour, minute = map(int, time_str.split(':'))
                        result.append(f"- {date_str} at {time_str}")
                    except ValueError:
                        result.append(f"- Warning: Invalid date/time format: {date_str} at {time_str}")
        else:
            result.append(f"Scheduling interviews for {candidate['name']} for {len(shortlisted_jobs)} positions...")
            result.append("Using default scheduling (weekdays starting 2 days from now)")
        
        # Get the job IDs from the shortlisted jobs in the session
        job_ids = [job_id for job_id, _, _ in shortlisted_jobs]
        print(f"Scheduling interviews for these shortlisted positions: {job_ids}")
        
        # Ensure matches exist and are properly marked as shortlisted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, ensure all shortlisted jobs have corresponding match entries marked as shortlisted
        for job_id, score, reason in shortlisted_jobs:
            cursor.execute("""
            SELECT id FROM matches 
            WHERE candidate_id = ? AND job_id = ?
            """, (candidate_id, job_id))
            
            match = cursor.fetchone()
            if match:
                match_id = match[0]
                # Update to ensure it's marked as shortlisted
                cursor.execute("""
                UPDATE matches SET is_shortlisted = 1
                WHERE id = ?
                """, (match_id,))
            else:
                # Create a match entry if it doesn't exist
                cursor.execute("""
                INSERT INTO matches (job_id, candidate_id, match_score, is_shortlisted)
                VALUES (?, ?, ?, 1)
                """, (job_id, candidate_id, score))
        
        conn.commit()
        
        # Now get all shortlisted matches for this candidate
        cursor.execute("""
        SELECT id, job_id FROM matches 
        WHERE candidate_id = ? AND is_shortlisted = 1
        """, (candidate_id,))
        
        matches = cursor.fetchall()
        
        if not matches:
            result.append("\nNo matches found for scheduling. This could be because:")
            result.append("- The interviews were already scheduled previously")
            result.append("- There was an issue with the database")
            conn.close()
            return "\n".join(result)
        
        # Schedule interviews for these matches
        scheduler = self.system.scheduler
        num_scheduled = 0
        scheduled_job_ids = []
        
        for match_id, job_id in matches:
            print(f"Scheduling interview for match ID: {match_id}, job ID: {job_id}")
            
            # First, mark the interview as scheduled in the database directly
            # This ensures the interview status is updated even if email sending fails
            interview_times = scheduler.generate_interview_times(
                custom_dates=custom_dates, 
                custom_times=custom_times
            )
            
            if interview_times:
                interview_date_str = interview_times[0].strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                UPDATE matches 
                SET interview_scheduled = 1,
                    interview_date = ?
                WHERE id = ?
                """, (interview_date_str, match_id))
                conn.commit()
            
            # Then try to send the email notification
            if scheduler.schedule_interview(match_id, custom_dates, custom_times):
                num_scheduled += 1
                scheduled_job_ids.append(job_id)
            else:
                # Even if email fails, we still count this as scheduled since the DB was updated
                num_scheduled += 1
                scheduled_job_ids.append(job_id)
                print(f"Email notification failed for match ID: {match_id}, but interview was still scheduled")
        
        conn.close()
        
        # Store in session
        self.session['scheduled_interviews'] = shortlisted_jobs
        
        if num_scheduled > 0:
            result.append(f"\nSuccessfully scheduled {num_scheduled} interviews for {candidate['name']}.")
            
            # Show the scheduled interview dates/times
            result.append("\nScheduled interview options:")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for job_id in scheduled_job_ids:
                job = self.get_job_info(job_id)
                if job:
                    # Get the interview date
                    cursor.execute("""
                    SELECT interview_date FROM matches 
                    WHERE candidate_id = ? AND job_id = ? AND interview_scheduled = 1
                    """, (candidate_id, job_id))
                    
                    date_result = cursor.fetchone()
                    if date_result and date_result[0]:
                        try:
                            # Parse the datetime from the database
                            interview_datetime = datetime.strptime(date_result[0], "%Y-%m-%d %H:%M:%S")
                            formatted_datetime = interview_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
                            result.append(f"- {job['job_title']}: {formatted_datetime}")
                        except:
                            result.append(f"- {job['job_title']}: Date parsing error")
                    else:
                        result.append(f"- {job['job_title']}: No date recorded")
            
            conn.close()
            
            result.append("\nInterview invitations have been sent (or would be sent if email is configured).")
            result.append("\nWhat would you like to do next?")
            result.append("- \"Process another resume\"")
            result.append("- \"Show me all candidates\"")
            result.append("- \"Show me all scheduled interviews\"")
        else:
            result.append("\nNo interviews were scheduled. This could be because:")
            result.append("- The interviews were already scheduled previously")
            result.append("- There was an issue with the email configuration")
            result.append("- The candidate wasn't actually shortlisted for any positions")
        
        return "\n".join(result)
    
    def get_system_status(self):
        """Get the current status of the recruitment system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count various metrics
        cursor.execute("SELECT COUNT(*) FROM job_descriptions")
        job_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM candidates")
        candidate_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
        shortlisted_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
        interview_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Get current candidate context
        current_context = ""
        if self.session.get('current_candidate'):
            candidate = self.get_candidate_info(self.session['current_candidate'])
            if candidate:
                current_context = f"Currently working with: {candidate['name']} (ID: {candidate['id']})"
                
                if self.session.get('shortlisted_jobs'):
                    current_context += f"\nShortlisted for {len(self.session['shortlisted_jobs'])} positions"
                
                if self.session.get('scheduled_interviews'):
                    current_context += f"\nInterviews scheduled for {len(self.session['scheduled_interviews'])} positions"
        
        # Build status message
        status = [
            "=== RECRUITMENT SYSTEM STATUS ===",
            f"Total Job Descriptions: {job_count}",
            f"Total Candidates: {candidate_count}",
            f"Total Shortlisted Matches: {shortlisted_count}",
            f"Total Scheduled Interviews: {interview_count}",
            "",
            f"Ollama Model: {self.config.get('ollama_model')}",
            f"Match Threshold: {self.config.get('match_threshold', 0.75) * 100:.0f}%",
            f"Max Shortlisted Positions: {self.config.get('max_shortlisted', 2)}",
            ""
        ]
        
        if current_context:
            status.append("--- CURRENT SESSION ---")
            status.append(current_context)
        
        return "\n".join(status)
    
    def update_config(self, new_settings):
        """Update configuration settings"""
        for key, value in new_settings.items():
            if key in self.config:
                # Convert to appropriate type
                if key == 'match_threshold':
                    value = float(value)
                elif key == 'max_shortlisted' or key == 'smtp_port':
                    value = int(value)
                
                self.config[key] = value
                
                # Special case for threshold - also update the matcher
                if key == 'match_threshold' and hasattr(self.system, 'matcher'):
                    self.system.matcher.threshold = value
                
                # Special case for max_shortlisted - also update the matcher
                if key == 'max_shortlisted' and hasattr(self.system, 'matcher'):
                    self.system.matcher.max_shortlisted = value
        
        # Save the updated config
        self.save_config()
        
        return f"Configuration updated successfully. New settings: {new_settings}"
    
    def get_help_text(self):
        """Return the help text for the system"""
        return """
    I can help you with the following recruiting tasks:

    Resume Processing:
    - "Process resume.pdf for John Doe (john@example.com)"
    - "Extract data from the resume in path/to/file.pdf"

    Candidate Analysis:
    - "Find matching jobs for this candidate"
    - "Match this candidate with available positions"
    - "What roles would be a good fit?"

    Interview Scheduling:
    - "Schedule interviews for the shortlisted positions"
    - "Send interview invitations"
    - "Schedule interviews on 2025-04-15 and 2025-04-16 at 10:00 and 14:30"
    - "Set up interviews for tomorrow at 11:00 AM"
    - "Schedule meetings for next week at 9:00 and 15:00"

    Information Lookup:
    - "Show me all candidates"
    - "List all jobs"
    - "Show me details for candidate 3"
    - "Tell me about job position 5"

    Configuration:
    - "Change match threshold to 60%"
    - "Set threshold to 0.65"

    System Information:
    - "What's the current status?"
    - "Show system status"
    - "Who am I working with right now?"

    I maintain context throughout our conversation, so you can refer to "this candidate" or "these positions" and I'll understand based on our discussion.
    """
            
    def process_intent_with_llm(self, user_input):
        """Use LLM to determine user intent for more complex commands"""
        # Build conversation context with more detail
        conversation_context = "\n".join([
            f"{msg['speaker']} ({msg['timestamp']}): {msg['message']}" 
            for msg in self.conversation_history[-5:]  # Reduced context window to focus on recent messages
        ])

        # Get the current session state for context with more details
        session_context = "Current session state:\n"
        
        if self.session.get('current_candidate'):
            candidate = self.get_candidate_info(self.session['current_candidate'])
            if candidate:
                session_context += f"- ACTIVE CANDIDATE: {candidate['name']} (ID: {candidate['id']})\n"
                session_context += f"  Email: {candidate['email']}\n"
                # Add truncated skills to give more context about the current candidate
                if candidate.get('skills'):
                    skills_preview = candidate['skills'][:100] + "..." if len(candidate['skills']) > 100 else candidate['skills']
                    session_context += f"  Skills preview: {skills_preview}\n"
        else:
            session_context += "- NO ACTIVE CANDIDATE SELECTED\n"
        
        if self.session.get('current_resume'):
            session_context += f"- Most recent resume: {os.path.basename(self.session['current_resume'])}\n"
                
        if self.session.get('shortlisted_jobs'):
            session_context += f"- CANDIDATE HAS BEEN MATCHED with {len(self.session['shortlisted_jobs'])} positions:\n"
            for job_id, score, reason in self.session.get('shortlisted_jobs')[:3]:  # Show first 3 shortlisted jobs
                job = self.get_job_info(job_id)
                if job:
                    session_context += f"  * {job['job_title']} (ID: {job_id}, match score: {score:.2f})\n"
        else:
            session_context += "- NO JOBS HAVE BEEN MATCHED YET\n"
                
        if self.session.get('scheduled_interviews'):
            session_context += f"- INTERVIEWS ALREADY SCHEDULED for {len(self.session['scheduled_interviews'])} positions\n"
        else:
            session_context += "- NO INTERVIEWS HAVE BEEN SCHEDULED YET\n"
        
        # Add system status info to give broader context
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM candidates")
        candidate_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM job_descriptions")
        job_count = cursor.fetchone()[0]
        conn.close()
        
        session_context += f"\nSystem overview:\n"
        session_context += f"- Total candidates in database: {candidate_count}\n"
        session_context += f"- Total jobs in database: {job_count}\n"
        session_context += f"- Match threshold: {self.config.get('match_threshold', 0.75):.2f}\n"
        
        # Build prompt with very explicit action instructions and examples
        prompt = f"""You are a recruiting assistant determining what action to take based on the user's message. Your task is ONLY to classify their intent into a specific action, not to execute it.

    DETAILED CONTEXT INFORMATION:
    {session_context}

    RECENT CONVERSATION:
    {conversation_context}

    USER'S LATEST MESSAGE: "{user_input}"

    AVAILABLE ACTIONS:
    1. "process_resume" - ONLY when user explicitly asks to process/parse/analyze a resume file
    Example user messages: "process resume.pdf", "analyze this applicant's resume", "extract data from resume"
    Parameters: "resume_path" (required), "candidate_name" and "candidate_email" (optional, only if explicitly stated)

    2. "analyze_candidate" - ONLY when user asks to find/match jobs for a candidate
    Example user messages: "find suitable jobs", "what positions match this candidate", "match with jobs"
    Parameters: "candidate_id" (optional)

    3. "schedule_interviews" - ONLY when user mentions scheduling/booking/arranging interviews or sending invites
    Example user messages: "schedule interviews", "send interview invitations", "book candidate meetings"
    Parameters: 
        - "custom_dates" (optional): List of dates in format 'YYYY-MM-DD' 
        - "custom_times" (optional): List of times in format 'HH:MM' (24-hour format)

    4. "list_candidates" - ONLY when user asks to show/list/view all candidates
    Example user messages: "show all candidates", "list the candidates", "who are the applicants"
    Parameters: none

    5. "list_jobs" - ONLY when user asks to show/list/view all jobs
    Example user messages: "show available jobs", "list all positions", "what jobs do we have"
    Parameters: none

    6. "get_candidate" - ONLY when user asks for details about a specific candidate
    Example user messages: "tell me about candidate 3", "show candidate details"
    Parameters: "candidate_id" (required)

    7. "get_job" - ONLY when user asks for details about a specific job
    Example user messages: "describe job 5", "what's job 2 about", "details for position 4"
    Parameters: "job_id" (required)

    8. "system_status" - ONLY when user asks about overall system status
    Example user messages: "system status", "what's the current status", "how is the system doing"
    Parameters: none

    9. "help" - ONLY when user asks for help or available commands
    Example user messages: "help", "what can you do", "show commands"
    Parameters: none

    10. "unknown" - When no clear intent can be determined
        Default when none of the above match

    VERY IMPORTANT RULES:
    1. NEVER invent parameters or values that were NOT explicitly mentioned by the user
    2. For "process_resume", ONLY include name/email if user EXPLICITLY provides them
    3. For "schedule_interviews", the action should be chosen if the message has ANY mention of interviews, scheduling, invitations, or meetings
    4. For "schedule_interviews", if the user specifies dates/times, extract them as "custom_dates" and "custom_times" parameters
    - Dates should be in 'YYYY-MM-DD' format (e.g., "2025-04-15")
    - Times should be in 'HH:MM' format (24-hour, e.g., "14:30" for 2:30 PM)
    5. If there's any uncertainty between "analyze_candidate" and another action, PREFER THE OTHER ACTION
    6. If the user has shortlisted jobs and is now talking about interviews, ALWAYS choose "schedule_interviews"
    7. Consider the conversation context - if they just processed a resume, they likely want to analyze it next
    8. ONLY choose "analyze_candidate" when the user EXPLICITLY asks to match a candidate with jobs, not for general follow-ups
    9. If the user just wants to continue or proceed after shortlisting, they likely want to schedule interviews

    Respond with ONLY a valid JSON object containing the action and parameters. Format:
    {{"action": "action_name", "params": {{"param1": "value1", "param2": "value2"}}}}

    For example:
    {{"action": "schedule_interviews", "params": {{"custom_dates": ["2025-04-15", "2025-04-16"], "custom_times": ["10:00", "14:30"]}}}}

    JSON:"""

        # Get response from Ollama
        llm_response = self._ollama_query(prompt)
        print(f"Intent detection prompt response: {llm_response}")
        
        # Extract the JSON from the response
        try:
            # Extract JSON from the response
            json_match = re.search(r'({[\s\S]*})', llm_response)
            if json_match:
                intent_data = json.loads(json_match.group(1))
                action = intent_data.get('action', 'unknown')
                params = intent_data.get('params', {})
                
                # Extra safety check: ensure we don't have empty params
                for key in list(params.keys()):
                    if params[key] == "" or params[key] is None:
                        del params[key]
                        
                # For resume processing, verify we don't have name/email unless explicitly mentioned
                if action == 'process_resume':
                    # Check if the user input actually contains names or emails
                    has_explicit_name = re.search(r'for\s+([A-Z][a-z]+\s+[A-Z][a-z]+)|name\s+is\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', user_input, re.IGNORECASE) is not None
                    has_explicit_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input) is not None
                    
                    # Remove parameters not explicitly mentioned
                    if not has_explicit_name and 'candidate_name' in params:
                        print("Removing auto-generated candidate name")
                        del params['candidate_name']
                        
                    if not has_explicit_email and 'candidate_email' in params:
                        print("Removing auto-generated candidate email")
                        del params['candidate_email']
                
                # CRITICAL FIX: Strong override for interview-related intents
                interview_keywords = ["interview", "schedule", "invitation", "invite", "meeting", 
                                    "book", "appointment", "calendar", "availability"]
                if any(keyword in user_input.lower() for keyword in interview_keywords):
                    print("Interview keyword detected, overriding action to schedule_interviews")
                    
                    # Extract dates and times using regex if the LLM didn't catch them
                    if action != "schedule_interviews" or "custom_dates" not in params or "custom_times" not in params:
                        # Extract dates in YYYY-MM-DD format
                        custom_dates = re.findall(r'(\d{4}-\d{2}-\d{2})', user_input)
                        
                        # Extract times in HH:MM format (both 24-hour and with AM/PM)
                        time_patterns = [
                            r'(\d{1,2}:\d{2})\s*(?:AM|PM|am|pm)?',  # HH:MM with optional AM/PM
                            r'(\d{1,2})\s*(?:AM|PM|am|pm)'          # HH with AM/PM
                        ]
                        
                        custom_times = []
                        for pattern in time_patterns:
                            matches = re.findall(pattern, user_input)
                            custom_times.extend(matches)
                        
                        # Convert times to 24-hour format if needed
                        normalized_times = []
                        for time_str in custom_times:
                            if ":" not in time_str:
                                # It's just an hour, add :00 for minutes
                                time_str = f"{time_str}:00"
                            
                            # Check if AM/PM is specified
                            if "PM" in user_input or "pm" in user_input:
                                # Convert to 24-hour format if it's PM
                                hour, minute = map(int, time_str.split(':'))
                                if hour < 12:
                                    hour += 12
                                time_str = f"{hour:02d}:{minute:02d}"
                            
                            normalized_times.append(time_str)
                        
                        # Update action and params
                        action = "schedule_interviews"
                        params = {}
                        
                        if custom_dates:
                            params["custom_dates"] = custom_dates
                            print(f"Extracted dates: {custom_dates}")
                        
                        if normalized_times:
                            params["custom_times"] = normalized_times
                            print(f"Extracted times: {normalized_times}")
                        
                    # If we still don't have dates/times, check for common phrases
                    if "tomorrow" in user_input.lower():
                        # Add tomorrow's date
                        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                        if "custom_dates" not in params:
                            params["custom_dates"] = [tomorrow]
                        else:
                            params["custom_dates"].append(tomorrow)
                        print(f"Added tomorrow's date: {tomorrow}")
                    
                    if "next week" in user_input.lower():
                        # Add dates for next week (Monday through Friday)
                        today = datetime.now()
                        next_week_start = today + timedelta(days=(7 - today.weekday()))
                        next_week_dates = []
                        for i in range(5):  # Monday through Friday
                            date = (next_week_start + timedelta(days=i)).strftime("%Y-%m-%d")
                            next_week_dates.append(date)
                        
                        if "custom_dates" not in params:
                            params["custom_dates"] = next_week_dates
                        else:
                            params["custom_dates"].extend(next_week_dates)
                        print(f"Added next week dates: {next_week_dates}")
                    
                    # Add default times if times were not specified
                    if "custom_dates" in params and "custom_times" not in params:
                        params["custom_times"] = ["10:00", "14:00"]  # Default to 10 AM and 2 PM
                        print("Added default times: 10:00 AM and 2:00 PM")
                        
                # CRITICAL FIX: If jobs are shortlisted but not scheduled, bias toward scheduling
                if (self.session.get('shortlisted_jobs') and 
                    not self.session.get('scheduled_interviews') and
                    any(word in user_input.lower() for word in ["next", "proceed", "go ahead", "continue", "now what"])):
                    print("User asking for next step after shortlisting, likely wants to schedule interviews")
                    action = "schedule_interviews"
                    # Keep any custom dates/times that might have been extracted
                    
                # Additional context-aware override
                if (action == "analyze_candidate" and 
                    self.session.get('shortlisted_jobs') and 
                    not self.session.get('scheduled_interviews')):
                    # Check for phrases that suggest wanting to move forward
                    proceed_phrases = ["what now", "proceed", "next step", "go ahead", "continue", "what's next", "what should i do"]
                    if any(phrase in user_input.lower() for phrase in proceed_phrases):
                        print("Context suggests scheduling is the next logical step after analysis")
                        action = "schedule_interviews"
                        # Keep any custom dates/times that might have been extracted
            else:
                action = 'unknown'
                params = {}
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            action = 'unknown'
            params = {}
            
        return action, params

    def execute_action(self, action, params, original_input):
        """Execute the identified action with the given parameters"""
        if action == 'process_resume':
            resume_path = params.get('resume_path')
            if resume_path:
                # Only pass these parameters if they exist and are non-empty
                candidate_name = params.get('candidate_name') if 'candidate_name' in params else None
                candidate_email = params.get('candidate_email') if 'candidate_email' in params else None
                
                # Double-check to make absolutely sure we're not using empty values
                if candidate_name == "":
                    candidate_name = None
                if candidate_email == "":
                    candidate_email = None
                    
                # Debug info
                if candidate_name:
                    print(f"Using explicitly provided name: {candidate_name}")
                if candidate_email:
                    print(f"Using explicitly provided email: {candidate_email}")
                    
                return self.process_resume(
                    resume_path,
                    candidate_name,
                    candidate_email
                )
            else:
                return "I need a resume file to process. Please specify the path to the resume."
        
        elif action == 'analyze_candidate':
            candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
            if candidate_id:
                return self.analyze_candidate(candidate_id)
            else:
                return "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
        elif action == 'schedule_interviews':
            # Extract custom dates and times from params if present
            custom_dates = params.get('custom_dates')
            custom_times = params.get('custom_times')
            
            # Log the custom scheduling information
            if custom_dates or custom_times:
                print(f"Custom interview scheduling requested:")
                if custom_dates:
                    print(f"  Dates: {custom_dates}")
                if custom_times:
                    print(f"  Times: {custom_times}")
            
            # Pass custom dates/times to the schedule_interviews method
            return self.schedule_interviews(custom_dates, custom_times)
        
        elif action == 'list_candidates':
            candidates = self.list_candidates()
            if candidates:
                lines = ["Here are all the candidates in the system:"]
                for candidate in candidates:
                    lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
                return "\n".join(lines)
            else:
                return "No candidates found in the database."
        
        elif action == 'list_jobs':
            jobs = self.list_jobs()
            if jobs:
                lines = ["Here are all the job positions in the system:"]
                for job in jobs:
                    lines.append(f"{job['id']}: {job['job_title']}")
                    if job['summary']:
                        summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
                        lines.append(f"   {summary}")
                return "\n".join(lines)
            else:
                return "No jobs found in the database."
        
        elif action == 'get_candidate':
            candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
            if candidate_id:
                candidate = self.get_candidate_info(candidate_id)
                if candidate:
                    lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
                    lines.append(f"Email: {candidate['email']}")
                    lines.append(f"Phone: {candidate['phone']}")
                    lines.append(f"\nSkills: {candidate['skills']}")
                    lines.append(f"\nExperience: {candidate['experience']}")
                    lines.append(f"\nEducation: {candidate['education']}")
                    lines.append(f"\nCertifications: {candidate['certifications']}")
                    return "\n".join(lines)
                else:
                    return f"No candidate found with ID {candidate_id}."
            else:
                return "Please specify a candidate ID or process a resume first."
        
        elif action == 'get_job':
            job_id = params.get('job_id')
            if job_id:
                job = self.get_job_info(job_id)
                if job:
                    lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
                    lines.append(f"\nSummary: {job['summary']}")
                    lines.append(f"\nRequired Skills: {job['required_skills']}")
                    lines.append(f"\nRequired Experience: {job['required_experience']}")
                    lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
                    lines.append(f"\nResponsibilities: {job['responsibilities']}")
                    return "\n".join(lines)
                else:
                    return f"No job found with ID {job_id}."
            else:
                return "Please specify a job ID."
        
        elif action == 'system_status':
            return self.get_system_status()
        
        elif action == 'help':
            return self.get_help_text()
        
        else:  # 'unknown' action
            # If we have a candidate and shortlisted jobs but no scheduled interviews,
            # a vague query might be asking to proceed with scheduling
            if (self.session.get('shortlisted_jobs') and 
                not self.session.get('scheduled_interviews') and
                any(word in original_input.lower() for word in ["next", "now", "then", "proceed", "go ahead"])):
                print("Interpreting vague query as intent to schedule after shortlisting")
                return self.schedule_interviews()
            
            return "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."
        
    def process_command(self, user_input):
        """Process a natural language command with stricter parameter handling"""
        # Add user input to history
        self.add_to_history('user', user_input)
        
        # Handle configuration change command
        if "change match threshold" in user_input.lower() or "set match threshold" in user_input.lower():
             # Extract the threshold value from the command
            threshold_match = re.search(r'threshold\s+(?:to\s+)?(\d+(?:\.\d+)?)', user_input)
            if threshold_match:
                new_threshold = float(threshold_match.group(1))
                # Convert percentage to decimal if needed
                if new_threshold > 1:
                    new_threshold = new_threshold / 100
                
                response = self.update_config({'match_threshold': new_threshold})
                self.add_to_history('assistant', response)
                return response
        
        # Map simple commands directly without using LLM to prevent default value creation
        lower_input = user_input.lower()
        
        # === DIRECT COMMAND MAPPING FOR COMMON OPERATIONS ===
        # These bypass the LLM intent detection to improve reliability
        
        # 1. Resume processing direct command detection
        if "process" in lower_input and (".pdf" in lower_input or ".docx" in lower_input):
            # Extract just the resume path without adding defaults
            resume_path = None
            
            # Look for PDF or DOCX file
            file_pattern = r'([a-zA-Z0-9_\-\.]+\.(pdf|docx))'
            file_match = re.search(file_pattern, user_input)
            if file_match:
                resume_path = file_match.group(1)
                
                # Check for explicit name in format "for John Doe"
                candidate_name = None
                name_pattern = r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
                name_match = re.search(name_pattern, user_input)
                if name_match:
                    candidate_name = name_match.group(1)
                
                # Check for explicit email
                candidate_email = None
                email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                email_match = re.search(email_pattern, user_input)
                if email_match:
                    candidate_email = email_match.group(1)
                
                # Process resume with any explicit values found
                response = self.process_resume(resume_path, candidate_name, candidate_email)
                self.add_to_history('assistant', response)
                return response
        
        # 2. Interview scheduling direct command detection
        # Check for any of the common phrases that indicate interview scheduling intent
        interview_phrases = [
            "schedule interview", "send invitation", "set up interview", 
            "schedule meeting", "send invites", "setup interviews",
            "invite candidate", "schedule the interview", "send the invitation"
        ]
        if any(phrase in lower_input for phrase in interview_phrases):
            print("Direct command match: Scheduling interviews")
            response = self.schedule_interviews()
            self.add_to_history('assistant', response)
            return response
        
        # 3. Candidate analysis direct command detection
        analysis_phrases = [
            "find suitable job", "match candidate", "what roles would", 
            "find matching job", "analyze candidate", "check job matches", 
            "find positions", "identify jobs", "suitable position"
        ]
        if any(phrase in lower_input for phrase in analysis_phrases):
            print("Direct command match: Analyzing candidate")
            response = self.analyze_candidate()
            self.add_to_history('assistant', response)
            return response
        
        # 4. System status direct command detection
        if "status" in lower_input or "system info" in lower_input:
            print("Direct command match: System status")
            response = self.get_system_status()
            self.add_to_history('assistant', response)
            return response
        
        # 5. Help command direct detection
        if lower_input == "help" or "show commands" in lower_input:
            print("Direct command match: Help")
            response = self.get_help_text()
            self.add_to_history('assistant', response)
            return response
            
        # 6. List candidates direct detection
        if "list candidates" in lower_input or "show candidates" in lower_input or "all candidates" in lower_input:
            candidates = self.list_candidates()
            if candidates:
                lines = ["Here are all the candidates in the system:"]
                for candidate in candidates:
                    lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
                response = "\n".join(lines)
            else:
                response = "No candidates found in the database."
            self.add_to_history('assistant', response)
            return response
            
        # 7. List jobs direct detection
        if "list jobs" in lower_input or "show jobs" in lower_input or "all jobs" in lower_input or "available jobs" in lower_input:
            jobs = self.list_jobs()
            if jobs:
                lines = ["Here are all the job positions in the system:"]
                for job in jobs:
                    lines.append(f"{job['id']}: {job['job_title']}")
                    if job['summary']:
                        summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
                        lines.append(f"   {summary}")
                response = "\n".join(lines)
            else:
                response = "No jobs found in the database."
            self.add_to_history('assistant', response)
            return response
            
        # 8. Progress from shortlisting to scheduling
        if (self.session.get('shortlisted_jobs') and not self.session.get('scheduled_interviews') and 
            any(phrase in lower_input for phrase in ["what now", "what next", "next step", "proceed", "continue"])):
            print("Direct command match: Progress from shortlisting to scheduling")
            response = self.schedule_interviews()
            self.add_to_history('assistant', response)
            return response
            
        # For more complex commands, use LLM-based intent detection
        action, params = self.process_intent_with_llm(user_input)
        
        # Execute the identified action
        print(f"Executing action: {action} with params: {params}")
        response = self.execute_action(action, params, user_input)
        
        # Add response to history
        self.add_to_history('assistant', response)
        
        return response
        
    def execute_action(self, action, params, original_input):
        """Execute the identified action with the given parameters"""
        if action == 'process_resume':
            resume_path = params.get('resume_path')
            if resume_path:
                # Only pass these parameters if they exist and are non-empty
                candidate_name = params.get('candidate_name') if 'candidate_name' in params else None
                candidate_email = params.get('candidate_email') if 'candidate_email' in params else None
                
                # Double-check to make absolutely sure we're not using empty values
                if candidate_name == "":
                    candidate_name = None
                if candidate_email == "":
                    candidate_email = None
                    
                # Debug info
                if candidate_name:
                    print(f"Using explicitly provided name: {candidate_name}")
                if candidate_email:
                    print(f"Using explicitly provided email: {candidate_email}")
                    
                return self.process_resume(
                    resume_path,
                    candidate_name,
                    candidate_email
                )
            else:
                return "I need a resume file to process. Please specify the path to the resume."
        
        elif action == 'analyze_candidate':
            candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
            if candidate_id:
                return self.analyze_candidate(candidate_id)
            else:
                return "I need a candidate to analyze. Please process a resume first or specify a candidate ID."
        
        elif action == 'schedule_interviews':
            # This is the critical fix - directly call schedule_interviews regardless of parameters
            return self.schedule_interviews()
        
        elif action == 'list_candidates':
            candidates = self.list_candidates()
            if candidates:
                lines = ["Here are all the candidates in the system:"]
                for candidate in candidates:
                    lines.append(f"{candidate['id']}: {candidate['name']} ({candidate['email']})")
                return "\n".join(lines)
            else:
                return "No candidates found in the database."
        
        elif action == 'list_jobs':
            jobs = self.list_jobs()
            if jobs:
                lines = ["Here are all the job positions in the system:"]
                for job in jobs:
                    lines.append(f"{job['id']}: {job['job_title']}")
                    if job['summary']:
                        summary = job['summary'] if len(job['summary']) < 100 else job['summary'][:97] + "..."
                        lines.append(f"   {summary}")
                return "\n".join(lines)
            else:
                return "No jobs found in the database."
        
        elif action == 'get_candidate':
            candidate_id = params.get('candidate_id', self.session.get('current_candidate'))
            if candidate_id:
                candidate = self.get_candidate_info(candidate_id)
                if candidate:
                    lines = [f"Information for {candidate['name']} (ID: {candidate['id']}):"]
                    lines.append(f"Email: {candidate['email']}")
                    lines.append(f"Phone: {candidate['phone']}")
                    lines.append(f"\nSkills: {candidate['skills']}")
                    lines.append(f"\nExperience: {candidate['experience']}")
                    lines.append(f"\nEducation: {candidate['education']}")
                    lines.append(f"\nCertifications: {candidate['certifications']}")
                    return "\n".join(lines)
                else:
                    return f"No candidate found with ID {candidate_id}."
            else:
                return "Please specify a candidate ID or process a resume first."
        
        elif action == 'get_job':
            job_id = params.get('job_id')
            if job_id:
                job = self.get_job_info(job_id)
                if job:
                    lines = [f"Job Description: {job['job_title']} (ID: {job['id']})"]
                    lines.append(f"\nSummary: {job['summary']}")
                    lines.append(f"\nRequired Skills: {job['required_skills']}")
                    lines.append(f"\nRequired Experience: {job['required_experience']}")
                    lines.append(f"\nRequired Qualifications: {job['required_qualifications']}")
                    lines.append(f"\nResponsibilities: {job['responsibilities']}")
                    return "\n".join(lines)
                else:
                    return f"No job found with ID {job_id}."
            else:
                return "Please specify a job ID."
        
        elif action == 'system_status':
            return self.get_system_status()
        
        elif action == 'help':
            return self.get_help_text()
        
        else:  # 'unknown' action
            # If we have a candidate and shortlisted jobs but no scheduled interviews,
            # a vague query might be asking to proceed with scheduling
            if (self.session.get('shortlisted_jobs') and 
                not self.session.get('scheduled_interviews') and
                any(word in original_input.lower() for word in ["next", "now", "then", "proceed", "go ahead"])):
                print("Interpreting vague query as intent to schedule after shortlisting")
                return self.schedule_interviews()
            
            return "I'm not sure what you want to do. Can you rephrase or provide more details? You can say 'help' to see available commands."


def main():
    """Main entry point for the conversational recruitment system"""
    parser = argparse.ArgumentParser(description='Conversational Recruitment System')
    parser.add_argument('--model', default='gemma2:2b', help='Ollama model to use (default: gemma2:2b)')
    parser.add_argument('--setup-db', action='store_true', help='Setup the database before starting')
    parser.add_argument('--import-jobs', help='Import jobs from CSV file')
    args = parser.parse_args()
    
    # Setup database if requested
    if args.setup_db:
        print("Setting up database...")
        setup_database('recruitment.db')
        print("Database setup complete.")
    
    # Import jobs if CSV provided
    if args.import_jobs:
        print(f"Importing jobs from {args.import_jobs}...")
        import_jobs_from_csv('recruitment.db', args.import_jobs)
        print("Jobs imported successfully.")
    
    system = ConversationalRecruitmentSystem(ollama_model=args.model)
    
    print("\n============================================")
    print("     RECRUITMENT SYSTEM - CONVERSATION     ")
    print("============================================")
    print("I can help you process resumes, match candidates with jobs, and schedule interviews.")
    print("Type 'help' for more information or 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.strip():
                response = system.process_command(user_input)
                print("\n" + response)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()