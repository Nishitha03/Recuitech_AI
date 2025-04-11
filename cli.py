# #!/usr/bin/env python3
# import argparse
# import os
# import sys
# import sqlite3
# import json

# # Ensure we can import from the current directory
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
# from db_setup import setup_database, import_jobs_from_csv

# def setup_parser():
#     """Set up command line argument parser"""
#     parser = argparse.ArgumentParser(description='Multi-Agent Recruitment System')
#     subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
#     # Setup database
#     subparsers.add_parser('setup-db', help='Set up the SQLite database')
    
#     # Import job descriptions
#     import_parser = subparsers.add_parser('import-jobs', help='Import job descriptions from CSV')
#     import_parser.add_argument('csv_path', help='Path to CSV file with job descriptions')
    
#     # Summarize job descriptions
#     summarize_parser = subparsers.add_parser('summarize', help='Summarize job descriptions')
#     summarize_parser.add_argument('--job-id', type=int, help='Specific job ID to summarize (optional)')
    
#     # Process resume
#     resume_parser = subparsers.add_parser('process-resume', help='Process a candidate resume')
#     resume_parser.add_argument('resume_path', help='Path to resume file (PDF or DOCX)')
#     resume_parser.add_argument('--name', help='Candidate name (optional)')
#     resume_parser.add_argument('--email', help='Candidate email (optional)')
#     resume_parser.add_argument('--analyze', action='store_true', help='Analyze and match with jobs')
    
#     # List jobs
#     subparsers.add_parser('list-jobs', help='List all job descriptions')
    
#     # List candidates
#     subparsers.add_parser('list-candidates', help='List all candidates')
    
#     # List matches
#     subparsers.add_parser('list-matches', help='List all candidate-job matches')
    
#     # Schedule interviews
#     schedule_parser = subparsers.add_parser('schedule', help='Schedule interviews for shortlisted candidates')
    
#     # Configure system
#     config_parser = subparsers.add_parser('config', help='Configure system settings')
#     config_parser.add_argument('--ollama-model', default='llama3', help='Ollama model to use')
#     config_parser.add_argument('--smtp-server', help='SMTP server for sending emails')
#     config_parser.add_argument('--smtp-port', type=int, default=587, help='SMTP port')
#     config_parser.add_argument('--smtp-username', help='SMTP username/email')
#     config_parser.add_argument('--smtp-password', help='SMTP password')
#     config_parser.add_argument('--save', action='store_true', help='Save configuration to config.json')
    
#     return parser

# def load_config():
#     """Load configuration from config.json if it exists"""
#     config = {
#         'ollama_model': 'gemma2:2b',
#         'smtp_server': "smtp",
#         'smtp_port': 587,
#         'smtp_username': None,
#         'smtp_password': None
#     }
    
#     if os.path.exists('config.json'):
#         try:
#             with open('config.json', 'r') as f:
#                 stored_config = json.load(f)
#                 config.update(stored_config)
#         except Exception as e:
#             print(f"Error loading config: {e}")
    
#     return config

# def save_config(config):
#     """Save configuration to config.json"""
#     try:
#         with open('config.json', 'w') as f:
#             json.dump(config, f, indent=2)
#         print("Configuration saved to config.json")
#     except Exception as e:
#         print(f"Error saving config: {e}")

# def summarize_jobs(args, ollama_model):
#     """Summarize job descriptions"""
#     summarizer = JobDescriptionSummarizer(ollama_model=ollama_model)
#     if args.job_id:
#         print(f"Summarizing job ID {args.job_id}...")
#         summarizer.summarize_job(args.job_id)
#     else:
#         print("Summarizing all unsummarized jobs...")
#         summarizer.summarize_all_jobs()

# def process_resume(args, config):
#     """Process a candidate resume"""
#     if args.analyze:
#         # Use the full recruitment system for analysis and matching
#         system = RecruitmentSystem(
#             ollama_model=config['ollama_model'],
#             smtp_server=config['smtp_server'],
#             smtp_port=config['smtp_port'],
#             smtp_username=config['smtp_username'],
#             smtp_password=config['smtp_password']
#         )
        
#         system.process_new_resume(args.resume_path, args.name, args.email)
#     else:
#         # Just process the resume without matching
#         processor = ResumeProcessor(ollama_model=config['ollama_model'])
#         candidate_id = processor.process_resume(args.resume_path, args.name, args.email)
#         if candidate_id:
#             print(f"Resume processed successfully. Candidate ID: {candidate_id}")
#         else:
#             print("Failed to process resume")

# def list_jobs():
#     """List all job descriptions in the database"""
#     conn = sqlite3.connect('recruitment.db')
#     cursor = conn.cursor()
    
#     cursor.execute("""
#     SELECT id, job_title, summary, required_skills
#     FROM job_descriptions
#     ORDER BY id
#     """)
    
#     jobs = cursor.fetchall()
#     conn.close()
    
#     if not jobs:
#         print("No jobs found in the database")
#         return
    
#     print(f"\n{'ID':<5}{'Job Title':<40}{'Summary':<60}")
#     print("-" * 105)
    
#     for job in jobs:
#         job_id, title, summary, skills = job
#         # Truncate long fields for display
#         title = (title[:37] + '...') if title and len(title) > 37 else title
#         summary = (summary[:57] + '...') if summary and len(summary) > 57 else summary
        
#         print(f"{job_id:<5}{title or 'N/A':<40}{summary or 'N/A':<60}")

# def list_candidates():
#     """List all candidates in the database"""
#     conn = sqlite3.connect('recruitment.db')
#     cursor = conn.cursor()
    
#     cursor.execute("""
#     SELECT id, name, email, skills, education
#     FROM candidates
#     ORDER BY id
#     """)
    
#     candidates = cursor.fetchall()
#     conn.close()
    
#     if not candidates:
#         print("No candidates found in the database")
#         return
    
#     print(f"\n{'ID':<5}{'Name':<30}{'Email':<30}{'Skills':<40}")
#     print("-" * 105)
    
#     for candidate in candidates:
#         candidate_id, name, email, skills, education = candidate
#         # Truncate long fields for display
#         name = (name[:27] + '...') if name and len(name) > 27 else name
#         email = (email[:27] + '...') if email and len(email) > 27 else email
#         skills = (skills[:37] + '...') if skills and len(skills) > 37 else skills
        
#         print(f"{candidate_id:<5}{name or 'N/A':<30}{email or 'N/A':<30}{skills or 'N/A':<40}")

# def list_matches():
#     """List all candidate-job matches in the database"""
#     conn = sqlite3.connect('recruitment.db')
#     cursor = conn.cursor()
    
#     cursor.execute("""
#     SELECT m.id, j.job_title, c.name, m.match_score, m.is_shortlisted, m.interview_scheduled, m.interview_date
#     FROM matches m
#     JOIN job_descriptions j ON m.job_id = j.id
#     JOIN candidates c ON m.candidate_id = c.id
#     ORDER BY m.match_score DESC
#     """)
    
#     matches = cursor.fetchall()
#     conn.close()
    
#     if not matches:
#         print("No matches found in the database")
#         return
    
#     print(f"\n{'ID':<5}{'Job Title':<30}{'Candidate':<25}{'Score':<10}{'Shortlisted':<15}{'Interview':<15}{'Date':<20}")
#     print("-" * 120)
    
#     for match in matches:
#         match_id, job_title, name, score, shortlisted, scheduled, date = match
#         # Truncate long fields for display
#         job_title = (job_title[:27] + '...') if job_title and len(job_title) > 27 else job_title
#         name = (name[:22] + '...') if name and len(name) > 22 else name
        
#         print(f"{match_id:<5}{job_title or 'N/A':<30}{name or 'N/A':<25}{score:.2f if score else 'N/A':<10}{'Yes' if shortlisted else 'No':<15}{'Yes' if scheduled else 'No':<15}{date or 'N/A':<20}")

# def schedule_interviews(config):
#     """Schedule interviews for shortlisted candidates"""
#     scheduler = InterviewScheduler(
#         ollama_model=config['ollama_model'],
#         smtp_server=config['smtp_server'],
#         smtp_port=config['smtp_port'],
#         smtp_username=config['smtp_username'],
#         smtp_password=config['smtp_password']
#     )
    
#     count = scheduler.schedule_all_pending_interviews()
#     print(f"Scheduled {count} interviews")

# def configure_system(args):
#     """Configure system settings"""
#     config = load_config()
    
#     # Update config with any provided values
#     if args.ollama_model:
#         config['ollama_model'] = args.ollama_model
#     if args.smtp_server:
#         config['smtp_server'] = args.smtp_server
#     if args.smtp_port:
#         config['smtp_port'] = args.smtp_port
#     if args.smtp_username:
#         config['smtp_username'] = args.smtp_username
#     if args.smtp_password:
#         config['smtp_password'] = args.smtp_password
    
#     # Display current configuration
#     print("\nCurrent Configuration:")
#     print(f"Ollama Model: {config['ollama_model']}")
#     print(f"SMTP Server: {config['smtp_server'] or 'Not configured'}")
#     print(f"SMTP Port: {config['smtp_port']}")
#     print(f"SMTP Username: {config['smtp_username'] or 'Not configured'}")
#     print(f"SMTP Password: {'Configured' if config['smtp_password'] else 'Not configured'}")
    
#     # Save if requested
#     if args.save:
#         save_config(config)
    
#     return config

# def main():
#     """Main entry point"""
#     parser = setup_parser()
#     args = parser.parse_args()
    
#     if not args.command:
#         parser.print_help()
#         return
    
#     # Load configuration
#     config = load_config()
    
#     # Execute the appropriate command
#     if args.command == 'setup-db':
#         setup_database()
#         print("Database setup complete")
    
#     elif args.command == 'import-jobs':
#         import_jobs_from_csv(args.csv_path)
    
#     elif args.command == 'summarize':
#         summarize_jobs(args, config['ollama_model'])
    
#     elif args.command == 'process-resume':
#         process_resume(args, config)
    
#     elif args.command == 'list-jobs':
#         list_jobs()
    
#     elif args.command == 'list-candidates':
#         list_candidates()
    
#     elif args.command == 'list-matches':
#         list_matches()
    
#     elif args.command == 'schedule':
#         schedule_interviews(config)
    
#     elif args.command == 'config':
#         config = configure_system(args)

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
import argparse
import os
import sys
import sqlite3
import json
import re
import requests

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multiagent_recruiter import RecruitmentSystem, JobDescriptionSummarizer, ResumeProcessor, CandidateMatcher, InterviewScheduler
from db_setup import setup_database, import_jobs_from_csv

class NaturalLanguageRecruitmentSystem:
    """A natural language interface for the multi-agent recruitment system"""
    
    def __init__(self, db_path='recruitment.db', ollama_model="gemma2:2b"):
        self.db_path = db_path
        self.ollama_model = ollama_model
        self.ollama_base_url = "http://localhost:11434/api"
        
        # Load config
        self.config = self.load_config()
        
        # Initialize agents but don't run actions automatically
        self.resumeProcessor = ResumeProcessor(db_path, ollama_model)
        self.candidateMatcher = CandidateMatcher(db_path, ollama_model, self.config.get('match_threshold', 0.8), self.config.get('max_shortlisted', 2))
        self.scheduler = InterviewScheduler(
            db_path, 
            ollama_model,
            self.config.get('smtp_server'),
            self.config.get('smtp_port', 587),
            self.config.get('smtp_username'),
            self.config.get('smtp_password')
        )
        
        # Set up a session with context
        self.session_data = {
            'last_analyzed_candidate': None,
            'last_shortlisted_jobs': [],
            'pending_actions': [],
            'last_command': None
        }
    
    def _ollama_query(self, prompt):
        """Send a query to the local Ollama instance for NL processing"""
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
            print("Configuration saved to config.json")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def parse_intent(self, user_input):
        """Use LLM to parse the user's intent from natural language input"""
        prompt = f"""As a recruitment system assistant, analyze the following user request and identify the primary intent and any relevant parameters.

User request: "{user_input}"

Possible intents:
1. process_resume - Extract data from a resume file
2. analyze_candidate - Match a candidate against available jobs
3. schedule_interviews - Schedule interviews for shortlisted candidates
4. list_jobs - Show available job descriptions
5. list_candidates - Show available candidates
6. list_matches - Show candidate-job matches
7. configure - Update system configuration
8. help - User needs assistance with the system

Respond with a JSON object containing the intent and parameters. For 'process_resume' and 'analyze_candidate', extract the resume path, candidate name, and email if mentioned.

Example response:
{{"intent": "analyze_candidate", "params": {{"resume_path": "path/to/resume.pdf", "name": "John Doe", "email": "john@example.com"}}}}

JSON response:"""

        response = self._ollama_query(prompt)
        
        try:
            # Extract JSON from the response
            json_match = re.search(r'({[\s\S]*})', response)
            if json_match:
                intent_data = json.loads(json_match.group(1))
                return intent_data
            else:
                print("Failed to extract intent from response")
                return {"intent": "unknown", "params": {}}
        except json.JSONDecodeError:
            print("Invalid JSON response from intent parsing")
            return {"intent": "unknown", "params": {}}
    
    def process_resume(self, resume_path, name=None, email=None):
        """Process a resume file and extract candidate information only"""
        print(f"Processing resume: {resume_path}")
        
        # Just process the resume without matching
        candidate_id = self.resumeProcessor.process_resume(resume_path, name, email)
        
        if candidate_id:
            print(f"Resume processed successfully. Candidate ID: {candidate_id}")
            self.session_data['last_analyzed_candidate'] = candidate_id
            self.session_data['last_command'] = 'process_resume'
            
            # Get candidate name for nicer messages
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM candidates WHERE id = ?", (candidate_id,))
            result = cursor.fetchone()
            candidate_name = result[0] if result else f"Candidate {candidate_id}"
            conn.close()
            
            print(f"\nCandidate information for {candidate_name} has been processed.")
            print("You can now analyze this candidate against jobs by saying something like:")
            print("  'Match this candidate with available jobs' or")
            print("  'Find the best positions for this candidate'")
        else:
            print("Failed to process resume")
        
        return candidate_id
    
    def analyze_candidate(self, candidate_id=None):
        """Analyze a candidate against jobs but don't schedule interviews yet"""
        if not candidate_id and self.session_data['last_analyzed_candidate']:
            candidate_id = self.session_data['last_analyzed_candidate']
        
        if not candidate_id:
            print("No candidate specified. Please process a resume first.")
            return False
        
        print(f"Analyzing candidate {candidate_id} against available jobs...")
        
        # Match against all jobs with limited shortlisting
        shortlisted_jobs = self.candidateMatcher.match_candidate_to_all_jobs(candidate_id)
        
        # Store the shortlisted jobs for later use
        if shortlisted_jobs:
            self.session_data['last_shortlisted_jobs'] = shortlisted_jobs
            self.session_data['pending_actions'] = ['schedule_interviews']
            
            print("\nAnalysis complete. Here's what you can do next:")
            print("  - 'Schedule interviews for this candidate'")
            print("  - 'Send interview invitations'")
            print("  - 'Show me the shortlisted positions again'")
        else:
            print("Candidate was not shortlisted for any position")
        
        self.session_data['last_command'] = 'analyze_candidate'
        return True
    
    def schedule_interviews(self):
        """Schedule interviews for the last analyzed candidate"""
        if not self.session_data['last_analyzed_candidate'] or not self.session_data['last_shortlisted_jobs']:
            print("No candidate has been analyzed yet or no jobs were shortlisted.")
            print("Please analyze a candidate first by saying something like:")
            print("  'Analyze resume.pdf for John Doe'")
            return False
        
        candidate_id = self.session_data['last_analyzed_candidate']
        
        # Get candidate name
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM candidates WHERE id = ?", (candidate_id,))
        result = cursor.fetchone()
        candidate_name = result[0] if result else f"Candidate {candidate_id}"
        
        # Get the shortlisted jobs
        job_ids = [job_id for job_id, _, _ in self.session_data['last_shortlisted_jobs']]
        
        if not job_ids:
            print("No jobs were shortlisted for this candidate.")
            return False
        
        job_titles = []
        for job_id in job_ids:
            cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
            result = cursor.fetchone()
            if result:
                job_titles.append(result[0])
        
        conn.close()
        
        # Confirm before scheduling
        print("\n========== INTERVIEW SCHEDULING ==========")
        print(f"Ready to schedule interviews for {candidate_name} for the following positions:")
        for title in job_titles:
            print(f"  - {title}")
        
        confirmation = input("\nDo you want to proceed with scheduling these interviews? (y/n): ")
        if confirmation.lower() not in ['y', 'yes']:
            print("Interview scheduling cancelled.")
            return False
        
        # Schedule the interviews
        print("\nScheduling interviews...")
        num_scheduled = self.scheduler.schedule_all_pending_interviews()
        
        print(f"Successfully scheduled {num_scheduled} interviews for {candidate_name}.")
        
        # Clear the pending actions
        self.session_data['pending_actions'] = []
        self.session_data['last_command'] = 'schedule_interviews'
        
        return True
    
    def list_jobs(self):
        """List all job descriptions in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, job_title, summary, required_skills
        FROM job_descriptions
        ORDER BY id
        """)
        
        jobs = cursor.fetchall()
        conn.close()
        
        if not jobs:
            print("No jobs found in the database")
            return
        
        print(f"\n{'ID':<5}{'Job Title':<40}{'Summary':<60}")
        print("-" * 105)
        
        for job in jobs:
            job_id, title, summary, skills = job
            # Truncate long fields for display
            title = (title[:37] + '...') if title and len(title) > 37 else title
            summary = (summary[:57] + '...') if summary and len(summary) > 57 else summary
            
            print(f"{job_id:<5}{title or 'N/A':<40}{summary or 'N/A':<60}")
        
        self.session_data['last_command'] = 'list_jobs'
    
    def list_candidates(self):
        """List all candidates in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, email, skills, education
        FROM candidates
        ORDER BY id
        """)
        
        candidates = cursor.fetchall()
        conn.close()
        
        if not candidates:
            print("No candidates found in the database")
            return
        
        print(f"\n{'ID':<5}{'Name':<30}{'Email':<30}{'Skills':<40}")
        print("-" * 105)
        
        for candidate in candidates:
            candidate_id, name, email, skills, education = candidate
            # Truncate long fields for display
            name = (name[:27] + '...') if name and len(name) > 27 else name
            email = (email[:27] + '...') if email and len(email) > 27 else email
            skills = (skills[:37] + '...') if skills and len(skills) > 37 else skills
            
            print(f"{candidate_id:<5}{name or 'N/A':<30}{email or 'N/A':<30}{skills or 'N/A':<40}")
        
        self.session_data['last_command'] = 'list_candidates'
    
    def list_matches(self):
        """List all candidate-job matches in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT m.id, j.job_title, c.name, m.match_score, m.is_shortlisted, m.interview_scheduled, m.interview_date
        FROM matches m
        JOIN job_descriptions j ON m.job_id = j.id
        JOIN candidates c ON m.candidate_id = c.id
        ORDER BY m.match_score DESC
        """)
        
        matches = cursor.fetchall()
        conn.close()
        
        if not matches:
            print("No matches found in the database")
            return
        
        print(f"\n{'ID':<5}{'Job Title':<30}{'Candidate':<25}{'Score':<10}{'Shortlisted':<15}{'Interview':<15}{'Date':<20}")
        print("-" * 120)
        
        for match in matches:
            match_id, job_title, name, score, shortlisted, scheduled, date = match
            # Truncate long fields for display
            job_title = (job_title[:27] + '...') if job_title and len(job_title) > 27 else job_title
            name = (name[:22] + '...') if name and len(name) > 22 else name
            
            print(f"{match_id:<5}{job_title or 'N/A':<30}{name or 'N/A':<25}{score:.2f if score else 'N/A':<10}{'Yes' if shortlisted else 'No':<15}{'Yes' if scheduled else 'No':<15}{date or 'N/A':<20}")
        
        self.session_data['last_command'] = 'list_matches'
    
    def update_configuration(self, params):
        """Update system configuration"""
        if 'ollama_model' in params:
            self.config['ollama_model'] = params['ollama_model']
        if 'smtp_server' in params:
            self.config['smtp_server'] = params['smtp_server']
        if 'smtp_port' in params:
            self.config['smtp_port'] = int(params['smtp_port'])
        if 'smtp_username' in params:
            self.config['smtp_username'] = params['smtp_username']
        if 'smtp_password' in params:
            self.config['smtp_password'] = params['smtp_password']
        if 'match_threshold' in params:
            self.config['match_threshold'] = float(params['match_threshold'])
        if 'max_shortlisted' in params:
            self.config['max_shortlisted'] = int(params['max_shortlisted'])
        
        # Display current configuration
        print("\nCurrent Configuration:")
        print(f"Ollama Model: {self.config['ollama_model']}")
        print(f"SMTP Server: {self.config['smtp_server'] or 'Not configured'}")
        print(f"SMTP Port: {self.config['smtp_port']}")
        print(f"SMTP Username: {self.config['smtp_username'] or 'Not configured'}")
        print(f"SMTP Password: {'Configured' if self.config['smtp_password'] else 'Not configured'}")
        print(f"Match Threshold: {self.config['match_threshold']}")
        print(f"Max Shortlisted: {self.config['max_shortlisted']}")
        
        save_conf = input("Do you want to save this configuration? (y/n): ")
        if save_conf.lower() in ['y', 'yes']:
            self.save_config()
        
        self.session_data['last_command'] = 'configure'
    
    def show_help(self):
        """Show help information"""
        print("\n========== RECRUITMENT SYSTEM HELP ==========")
        print("Natural Language Interface - Command Examples:")
        print("\nResume Processing:")
        print("  - \"Process resume.pdf for John Doe (john@example.com)\"")
        print("  - \"Extract data from the resume in path/to/file.pdf\"")
        print("\nCandidate Analysis:")
        print("  - \"Analyze candidate 3 against all jobs\"")
        print("  - \"Find matching jobs for the last candidate\"")
        print("  - \"Match this resume with available positions\"")
        print("\nInterview Scheduling:")
        print("  - \"Schedule interviews for shortlisted candidates\"")
        print("  - \"Send interview invitations to the matched candidate\"")
        print("\nListing Information:")
        print("  - \"Show me all jobs\"")
        print("  - \"List all candidates\"")
        print("  - \"Show me the matches\"")
        print("\nConfiguration:")
        print("  - \"Update SMTP settings\"")
        print("  - \"Change the Ollama model to llama3\"")
        print("  - \"Set match threshold to 0.8\"")
        print("=========================================")
    
    def process_command(self, user_input):
        """Process a natural language command from the user"""
        intent_data = self.parse_intent(user_input)
        intent = intent_data.get('intent', 'unknown')
        params = intent_data.get('params', {})
        
        if intent == 'process_resume':
            resume_path = params.get('resume_path')
            if not resume_path:
                print("Please specify a resume path. For example:")
                print("  'Process resume.pdf for John Doe'")
                return
            
            self.process_resume(
                resume_path, 
                params.get('name'), 
                params.get('email')
            )
        
        elif intent == 'analyze_candidate':
            # Use the last processed candidate if available
            candidate_id = params.get('candidate_id')
            if not candidate_id and self.session_data['last_analyzed_candidate']:
                candidate_id = self.session_data['last_analyzed_candidate']
            
            if candidate_id:
                self.analyze_candidate(candidate_id)
            else:
                print("Please specify a candidate ID or process a resume first.")
        
        elif intent == 'schedule_interviews':
            self.schedule_interviews()
        
        elif intent == 'list_jobs':
            self.list_jobs()
        
        elif intent == 'list_candidates':
            self.list_candidates()
        
        elif intent == 'list_matches':
            self.list_matches()
        
        elif intent == 'configure':
            self.update_configuration(params)
        
        elif intent == 'help':
            self.show_help()
        
        else:
            print("I'm not sure what you want to do. Try rephrasing or type 'help' for assistance.")

def main():
    """Main entry point for natural language interface"""
    print("\n============================================")
    print("     RECRUITMENT SYSTEM - NL INTERFACE      ")
    print("============================================")
    print("Type 'help' for command examples or 'exit' to quit.")
    
    system = NaturalLanguageRecruitmentSystem()
    
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.strip():
                system.process_command(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()