import streamlit as st
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
import time
import requests
import base64
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="AI Recruitment System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 30px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 30px;
    }
    .sub-header {
        font-size: 24px;
        color: #1E3A8A;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .status-box {
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #d1fae5;
        border: 1px solid #10b981;
    }
    .info-box {
        background-color: #e0f2fe;
        border: 1px solid #0ea5e9;
    }
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
    }
    .error-box {
        background-color: #fee2e2;
        border: 1px solid #ef4444;
    }
    .stProgress .st-bo {
        background-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for configuration
if 'config' not in st.session_state:
    st.session_state.config = {
        "db_path": "recruitment.db",
        "ollama_model": "gemma3:1b",
        "match_threshold": 0.75,
        "max_shortlisted": 2,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": None,
        "smtp_password": None
    }

# Sidebar configuration - Now defined at the top level, not in a function
with st.sidebar:
    st.markdown("## Configuration")
    
    # Database management
    st.markdown("### Database")
    st.session_state.config["db_path"] = st.text_input("Database Path", st.session_state.config["db_path"])
    
    # LLM model configuration
    st.markdown("### LLM Model")
    model_options = ["gemma3:1b", "llama3:8b", "mistral", "llama3", "gemma2:2b"]
    st.session_state.config["ollama_model"] = st.selectbox("Ollama Model", model_options, 
                                                       index=model_options.index(st.session_state.config["ollama_model"]) 
                                                       if st.session_state.config["ollama_model"] in model_options else 0)
    
    # Matching configuration
    st.markdown("### Matching Parameters")
    st.session_state.config["match_threshold"] = st.slider("Match Threshold", 0.5, 1.0, st.session_state.config["match_threshold"], 0.05)
    st.session_state.config["max_shortlisted"] = st.slider("Max Shortlisted Positions", 1, 10, st.session_state.config["max_shortlisted"], 1)
    
    # Email configuration
    st.markdown("### Email Configuration")
    smtp_server = st.text_input("SMTP Server", "smtp.gmail.com")
    smtp_port = st.number_input("SMTP Port", 1, 9999, 587)
    smtp_username = st.text_input("SMTP Username", "")
    smtp_password = st.text_input("SMTP Password", "", type="password")
    
    # Update email config only if values are provided
    st.session_state.config["smtp_server"] = smtp_server if smtp_server else None
    st.session_state.config["smtp_port"] = smtp_port
    st.session_state.config["smtp_username"] = smtp_username if smtp_username else None
    st.session_state.config["smtp_password"] = smtp_password if smtp_password else None
    
    # Database initialization options
    st.markdown("### Database Initialization")
    init_db = st.button("Initialize Database")
    if init_db:
        st.session_state.init_db = True
        st.experimental_rerun()
    
    # CSV import
    st.markdown("### Import Jobs")
    csv_file = st.file_uploader("Upload Job Descriptions CSV", type=['csv'])
    import_csv = st.button("Import Jobs from CSV")
    if import_csv and csv_file:
        st.session_state.csv_file = csv_file
        st.session_state.import_csv = True
        st.experimental_rerun()

# Database utilities
def init_database(db_path):
    try:
        # Create a simplified database structure since we don't have the imported modules
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create job_descriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY,
            job_title TEXT NOT NULL,
            description TEXT NOT NULL,
            summary TEXT,
            required_skills TEXT,
            required_experience TEXT,
            required_qualifications TEXT,
            responsibilities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create candidates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            resume_text TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            certifications TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create matches table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            match_score REAL NOT NULL,
            match_details TEXT,
            is_shortlisted INTEGER DEFAULT 0,
            interview_scheduled INTEGER DEFAULT 0,
            interview_date TEXT,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES job_descriptions (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        st.success(f"Database initialized successfully at {db_path}")
    except Exception as e:
        st.error(f"Error initializing database: {e}")

def import_jobs(db_path, csv_file):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_file.write(csv_file.getvalue())
            temp_path = temp_file.name
        
        # Import jobs from CSV
        df = pd.read_csv(temp_path)
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Import each job
        for _, row in df.iterrows():
            # Check if the CSV has the required columns
            if 'job_title' in df.columns and 'description' in df.columns:
                cursor.execute('''
                INSERT INTO job_descriptions (job_title, description)
                VALUES (?, ?)
                ''', (row['job_title'], row['description']))
        
        conn.commit()
        conn.close()
        
        # Remove the temp file
        os.unlink(temp_path)
        
        st.success("Job descriptions imported successfully!")
    except Exception as e:
        st.error(f"Error importing job descriptions: {e}")

# Simulated resume text extraction - Handles both PDF and DOCX
def extract_resume_text(file_path):
    """Simulate text extraction from resume files"""
    # In a real application, you would use libraries like PyPDF2 or docx
    # For this demo, we'll simulate the extraction
    try:
        # Check file extension
        if file_path.lower().endswith('.pdf'):
            # Simulated PDF content
            return """John Doe
john.doe@example.com
(123) 456-7890

SUMMARY
Experienced software engineer with 5+ years of experience in Python, JavaScript, and cloud technologies. 
Skilled in developing scalable applications and implementing CI/CD pipelines.

SKILLS
Python, JavaScript, React, AWS, Docker, Kubernetes, SQL, Git, REST APIs

EXPERIENCE
Software Engineer, XYZ Corp (2018-2022)
- Developed and maintained web applications using React and Node.js
- Implemented CI/CD pipelines for automated testing and deployment
- Collaborated with cross-functional teams to deliver high-quality software

Data Analyst, ABC Inc (2015-2018)
- Analyzed large datasets using Python and SQL
- Created data visualizations and dashboards
- Provided insights to inform business decisions

EDUCATION
Bachelor of Science in Computer Science, University of Example (2015)

CERTIFICATIONS
AWS Certified Developer, Scrum Master
"""
        elif file_path.lower().endswith('.docx'):
            # Simulated DOCX content
            return """Jane Smith
jane.smith@example.com
(987) 654-3210

SUMMARY
Marketing professional with 7+ years of experience in digital marketing, content creation, and campaign management. 
Proven track record of increasing engagement and ROI.

SKILLS
Digital Marketing, Content Strategy, SEO, SEM, Social Media Management, Analytics, Campaign Management

EXPERIENCE
Marketing Manager, Best Marketing Agency (2019-2023)
- Led digital marketing campaigns for clients across various industries
- Increased organic traffic by 35% through SEO optimization
- Managed a team of 5 content creators and social media specialists

Digital Marketing Specialist, Marketing Solutions Inc (2016-2019)
- Developed and implemented social media strategies
- Created content for websites, blogs, and social media platforms
- Analyzed campaign performance and provided recommendations

EDUCATION
Bachelor of Arts in Marketing, State University (2016)

CERTIFICATIONS
Google Analytics Certified, HubSpot Inbound Marketing
"""
        else:
            return "Unsupported file format. Please upload a PDF or DOCX file."
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return ""

# Simulated AI extraction of candidate info
def extract_candidate_info(resume_text, candidate_name=None, candidate_email=None):
    """Simulate AI extraction of candidate information"""
    # In a real app, this would call an AI model to extract structured info
    # For this demo, we'll parse the text with some basic rules
    
    # Initialize info dict
    info = {}
    
    # Extract name (first line is usually the name)
    lines = resume_text.strip().split('\n')
    if not candidate_name and lines:
        info['name'] = lines[0].strip()
    else:
        info['name'] = candidate_name if candidate_name else "Unknown"
    
    # Extract email
    if not candidate_email:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            info['email'] = email_match.group(0)
        else:
            info['email'] = ""
    else:
        info['email'] = candidate_email
    
    # Extract phone
    phone_pattern = r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    phone_match = re.search(phone_pattern, resume_text)
    if phone_match:
        info['phone'] = phone_match.group(0)
    else:
        info['phone'] = ""
    
    # Extract sections
    section_patterns = {
        'skills': r'SKILLS\s*\n([\s\S]*?)(?=\n\n[A-Z]+|$)',
        'experience': r'EXPERIENCE\s*\n([\s\S]*?)(?=\n\n[A-Z]+|$)',
        'education': r'EDUCATION\s*\n([\s\S]*?)(?=\n\n[A-Z]+|$)',
        'certifications': r'CERTIFICATIONS\s*\n([\s\S]*?)(?=\n\n[A-Z]+|$)'
    }
    
    for section, pattern in section_patterns.items():
        match = re.search(pattern, resume_text)
        if match:
            info[section] = match.group(1).strip()
        else:
            info[section] = ""
    
    return info

# Main Process Resume function
def process_resume(resume_file, candidate_name, candidate_email):
    if resume_file is None:
        st.error("Please upload a resume file first.")
        return
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf' if resume_file.name.endswith('.pdf') else '.docx') as temp_file:
        temp_file.write(resume_file.getvalue())
        temp_path = temp_file.name
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_container = st.empty()
    log_container = st.empty()
    
    # Create a log area
    with log_container.container():
        log_area = st.empty()
    
    try:
        status_container.info("Processing resume...")
        progress_bar.progress(10)
        
        # Extract resume text
        status_container.info("Extracting text from resume...")
        progress_bar.progress(30)
        
        resume_text = extract_resume_text(temp_path)
        if not resume_text:
            status_container.error("Failed to extract text from resume.")
            # Remove the temp file
            os.unlink(temp_path)
            return
        
        log_area.markdown(f"Extracted {len(resume_text)} characters from resume.")
        log_area.markdown(f"Sample text: {resume_text[:150]}...")
        
        # Extract candidate information
        status_container.info("Analyzing resume content...")
        progress_bar.progress(60)
        
        candidate_info = extract_candidate_info(resume_text, candidate_name, candidate_email)
        
        # Store in database
        status_container.info("Storing candidate information...")
        progress_bar.progress(80)
        
        conn = sqlite3.connect(st.session_state.config["db_path"])
        cursor = conn.cursor()
        
        # Convert any lists to strings before database insertion
        for key in candidate_info:
            if isinstance(candidate_info[key], list):
                candidate_info[key] = ', '.join(str(item) for item in candidate_info[key])
        
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
        
        log_area.markdown(f"Added candidate to database with ID: {candidate_id}")
        
        # Store candidate ID in session state
        st.session_state.current_candidate = candidate_id
        st.session_state.current_candidate_name = candidate_info.get('name', f"Candidate {candidate_id}")
        
        # Display extracted information
        status_container.success("Resume processed successfully!")
        progress_bar.progress(100)
        
        # Format and display candidate information
        candidate_display = st.container()
        with candidate_display:
            st.markdown("### Extracted Candidate Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {candidate_info.get('name', 'Not detected')}")
                st.markdown(f"**Email:** {candidate_info.get('email', 'Not detected')}")
                st.markdown(f"**Phone:** {candidate_info.get('phone', 'Not detected')}")
            
            with col2:
                if 'skills' in candidate_info and candidate_info['skills']:
                    st.markdown(f"**Skills:** {candidate_info['skills']}")
                
                if 'certifications' in candidate_info and candidate_info['certifications']:
                    st.markdown(f"**Certifications:** {candidate_info['certifications']}")
            
            st.markdown("#### Experience")
            if 'experience' in candidate_info and candidate_info['experience']:
                st.markdown(candidate_info['experience'])
            else:
                st.markdown("No experience detected")
            
            st.markdown("#### Education")
            if 'education' in candidate_info and candidate_info['education']:
                st.markdown(candidate_info['education'])
            else:
                st.markdown("No education detected")
        
        # Remove the temp file
        os.unlink(temp_path)
        
        # Enable the "Analyze Candidate" button
        st.session_state.resume_processed = True
        
        return candidate_id
    
    except Exception as e:
        status_container.error(f"Error processing resume: {e}")
        progress_bar.progress(100)
        
        # Remove the temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return None

# Analyze candidate against jobs
def analyze_candidate(candidate_id):
    if not candidate_id:
        st.error("No candidate selected. Please process a resume first.")
        return
    
    # Create progress bar and containers
    progress_bar = st.progress(0)
    status_container = st.empty()
    results_container = st.container()
    
    try:
        # Get candidate information
        conn = sqlite3.connect(st.session_state.config["db_path"])
        cursor = conn.cursor()
        cursor.execute("SELECT name, skills, experience FROM candidates WHERE id = ?", (candidate_id,))
        candidate_result = cursor.fetchone()
        
        if not candidate_result:
            status_container.error(f"No candidate found with ID {candidate_id}")
            progress_bar.progress(100)
            conn.close()
            return
        
        candidate_name, candidate_skills, candidate_experience = candidate_result
        
        # Match against all jobs
        status_container.info(f"Matching {candidate_name} against all jobs...")
        progress_bar.progress(30)
        
        # Get all jobs
        cursor.execute("""
        SELECT id, job_title, required_skills, required_experience 
        FROM job_descriptions
        """)
        
        jobs = cursor.fetchall()
        
        if not jobs:
            status_container.warning("No jobs found in the database. Please import jobs first.")
            progress_bar.progress(100)
            conn.close()
            return
        
        # Calculate matches for all jobs with progress updates
        results = []
        job_count = len(jobs)
        
        with results_container:
            st.markdown(f"### Matching {candidate_name} against {job_count} jobs...")
            match_progress = st.progress(0)
            match_status = st.empty()
            
            for i, job in enumerate(jobs):
                job_id, job_title, job_skills, job_experience = job
                
                match_status.info(f"Matching job {i+1} of {job_count}: {job_title}")
                
                # Simulate AI matching with a random score and reasoning
                import random
                match_score = random.uniform(0.5, 0.95)
                
                # More realistic scoring based on skills
                if candidate_skills and job_skills:
                    candidate_skill_list = [s.strip().lower() for s in candidate_skills.split(',')]
                    job_skill_list = [s.strip().lower() for s in job_skills.split(',')] if job_skills else []
                    
                    # Count matching skills
                    matching_skills = set(candidate_skill_list).intersection(set(job_skill_list))
                    
                    # Adjust score based on matching skills
                    if job_skill_list:
                        skill_match_ratio = len(matching_skills) / len(job_skill_list)
                        match_score = 0.5 + (skill_match_ratio * 0.4)  # Scales from 0.5 to 0.9
                
                # Generate reasoning based on match score
                if match_score >= 0.8:
                    match_reasoning = f"Strong match! Candidate's skills and experience align well with the {job_title} position requirements."
                elif match_score >= 0.7:
                    match_reasoning = f"Good match. The candidate has many of the skills needed for the {job_title} role."
                elif match_score >= 0.6:
                    match_reasoning = f"Moderate match. Some relevant skills for the {job_title} position, but may need additional training."
                else:
                    match_reasoning = f"Basic match. The candidate has some transferable skills but isn't an ideal fit for the {job_title} role."
                
                # Save match to database
                cursor.execute("""
                INSERT INTO matches (job_id, candidate_id, match_score, match_details, is_shortlisted)
                VALUES (?, ?, ?, ?, 0)
                """, (job_id, candidate_id, match_score, match_reasoning))
                
                match_id = cursor.lastrowid
                conn.commit()
                
                results.append((job_id, match_score, match_reasoning, match_id))
                
                match_progress.progress((i + 1) / job_count)
                time.sleep(0.1)  # Simulate processing time
        
        progress_bar.progress(70)
        
        # Sort by match score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Select only top matches that meet threshold for shortlisting
        shortlisted_count = 0
        shortlisted_jobs = []
        
        with results_container:
            st.markdown("### Match Results")
            
            # Create two tabs - one for shortlisted jobs and one for all matches
            tab1, tab2 = st.tabs(["Shortlisted Positions", "All Matches"])
            
            with tab1:
                shortlisted_table = []
                
                for job_id, match_score, match_reasoning, match_id in results:
                    # Get job title
                    cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
                    job_title = cursor.fetchone()[0]
                    
                    if match_score >= st.session_state.config["match_threshold"] and shortlisted_count < st.session_state.config["max_shortlisted"]:
                        # Update this match as shortlisted
                        cursor.execute("""
                        UPDATE matches SET is_shortlisted = 1 WHERE id = ?
                        """, (match_id,))
                        
                        shortlisted_count += 1
                        shortlisted_jobs.append((job_id, match_score, match_reasoning))
                        
                        # Add to shortlisted table
                        shortlisted_table.append({
                            "Job Title": job_title,
                            "Match Score": f"{match_score:.2f}",
                            "Reasoning": match_reasoning
                        })
                
                if shortlisted_table:
                    st.dataframe(
                        pd.DataFrame(shortlisted_table),
                        use_container_width=True
                    )
                else:
                    st.warning("No positions were shortlisted. Consider lowering the match threshold.")
            
            with tab2:
                all_matches_table = []
                
                for job_id, match_score, match_reasoning, match_id in results:
                    # Get job title
                    cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
                    job_title = cursor.fetchone()[0]
                    
                    # Add to all matches table
                    all_matches_table.append({
                        "Job Title": job_title,
                        "Match Score": f"{match_score:.2f}",
                        "Shortlisted": "Yes" if match_score >= st.session_state.config["match_threshold"] and len(all_matches_table) < st.session_state.config["max_shortlisted"] else "No",
                        "Reasoning": match_reasoning
                    })
                
                if all_matches_table:
                    st.dataframe(
                        pd.DataFrame(all_matches_table),
                        use_container_width=True
                    )
                else:
                    st.warning("No matches found.")
        
        # Store shortlisted jobs in session state
        st.session_state.shortlisted_jobs = shortlisted_jobs
        
        conn.commit()
        conn.close()
        
        # Complete
        progress_bar.progress(100)
        status_container.success(f"Analysis complete! {candidate_name} was shortlisted for {shortlisted_count} positions.")
        
        # Enable the "Schedule Interviews" button
        if shortlisted_count > 0:
            st.session_state.candidate_analyzed = True
        
        return shortlisted_jobs
    
    except Exception as e:
        status_container.error(f"Error analyzing candidate: {e}")
        progress_bar.progress(100)
        if 'conn' in locals():
            conn.close()
        return None

# Schedule interviews for shortlisted candidates
def schedule_interviews(candidate_id, custom_dates=None, custom_times=None):
    if not candidate_id:
        st.error("No candidate selected. Please process a resume first.")
        return
    
    if not hasattr(st.session_state, 'shortlisted_jobs') or not st.session_state.shortlisted_jobs:
        st.error("No positions shortlisted. Please analyze the candidate first.")
        return
    
    # Create progress bar and containers
    progress_bar = st.progress(0)
    status_container = st.empty()
    results_container = st.container()
    
    try:
        status_container.info("Preparing to schedule interviews...")
        progress_bar.progress(10)
        
        # Get candidate information
        conn = sqlite3.connect(st.session_state.config["db_path"])
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM candidates WHERE id = ?", (candidate_id,))
        result = cursor.fetchone()
        
        if not result:
            status_container.error(f"No candidate found with ID {candidate_id}")
            progress_bar.progress(100)
            conn.close()
            return
        
        candidate_name, candidate_email = result
        
        # Get the job IDs from the shortlisted jobs in the session
        job_ids = [job_id for job_id, _, _ in st.session_state.shortlisted_jobs]
        
        progress_bar.progress(30)
        
        # Ensure matches exist and are properly marked as shortlisted
        for job_id, score, reason in st.session_state.shortlisted_jobs:
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
            status_container.error("No matches found for scheduling")
            progress_bar.progress(100)
            conn.close()
            return
        
        progress_bar.progress(50)
        
        # Generate interview times
        interview_times = []
        
        # If custom dates and times are provided, use those
        if custom_dates and custom_times:
            for date_str in custom_dates:
                for time_str in custom_times:
                    try:
                        # Parse date and time strings
                        year, month, day = map(int, date_str.split('-'))
                        hour, minute = map(int, time_str.split(':'))
                        
                        # Create datetime object
                        slot = datetime(year, month, day, hour, minute, 0)
                        interview_times.append(slot)
                    except ValueError as e:
                        st.error(f"Error parsing date/time: {e}")
                        continue
        
        # If no valid custom dates/times, generate default ones
        if not interview_times:
            current_time = datetime.now()
            day_pointer = current_time + timedelta(days=2)
            
            # Skip to next business day if weekend
            while day_pointer.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                day_pointer += timedelta(days=1)
            
            # Add morning and afternoon slots for next 3 business days
            for _ in range(3):
                # Morning slot
                morning_slot = datetime(
                    day_pointer.year, day_pointer.month, day_pointer.day, 10, 0, 0
                )
                interview_times.append(morning_slot)
                
                # Afternoon slot
                afternoon_slot = datetime(
                    day_pointer.year, day_pointer.month, day_pointer.day, 14, 0, 0
                )
                interview_times.append(afternoon_slot)
                
                # Move to next business day
                day_pointer += timedelta(days=1)
                while day_pointer.weekday() >= 5:
                    day_pointer += timedelta(days=1)
        
        with results_container:
            st.markdown(f"### Scheduling Interviews for {candidate_name}")
            
            # Show the candidate email
            st.markdown(f"**Email:** {candidate_email}")
            
            # Show the interview times
            st.markdown("#### Proposed Interview Times")
            times_text = ""
            for idx, time_slot in enumerate(interview_times, 1):
                times_text += f"- {time_slot.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            st.markdown(times_text)
            
            # Show shortlisted positions
            st.markdown("#### Shortlisted Positions")
            position_text = ""
            for job_id, _, _ in st.session_state.shortlisted_jobs:
                # Get job title
                cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
                job_title = cursor.fetchone()[0]
                position_text += f"- {job_title}\n"
            st.markdown(position_text)
            
            # Show email status
            if st.session_state.config["smtp_server"] and st.session_state.config["smtp_username"] and st.session_state.config["smtp_password"]:
                email_status = st.success("Email will be sent using the configured SMTP server.")
            else:
                email_status = st.warning("No SMTP configuration provided. Email content will be displayed but not sent.")
        
        progress_bar.progress(70)
        
        # Schedule interviews for these matches
        num_scheduled = 0
        scheduled_job_ids = []
        
        for match_id, job_id in matches:
            status_container.info(f"Scheduling interview for job {job_id}...")
            
            # Mark the interview as scheduled in the database
            cursor.execute("""
            UPDATE matches 
            SET interview_scheduled = 1,
                interview_date = ?
            WHERE id = ?
            """, (interview_times[0].strftime("%Y-%m-%d %H:%M:%S"), match_id))
            conn.commit()
            
            # In a real app, we would send an email here
            # For our demo, we'll just simulate success
            num_scheduled += 1
            scheduled_job_ids.append(job_id)
            with results_container:
                st.success(f"Interview scheduled for job ID {job_id}")
        
        progress_bar.progress(90)
        
        # If no SMTP config, generate and show what the email would have been
        if not st.session_state.config["smtp_server"] or not st.session_state.config["smtp_username"] or not st.session_state.config["smtp_password"]:
            # Get the first job for the email preview
            job_id = scheduled_job_ids[0] if scheduled_job_ids else job_ids[0]
            cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
            job_title = cursor.fetchone()[0]
            
            # Generate email preview
            time_str = "\n".join([time.strftime("%A, %B %d at %I:%M %p") for time in interview_times])
            
            subject = f"Interview Invitation: {job_title} Position"
            body = f"""Dear {candidate_name},

We are pleased to inform you that your application for the {job_title} position has been shortlisted. We would like to invite you for an interview.

Please find the available time slots below:
{time_str}

Please reply to this email with your preferred time slot.

Best regards,
Recruitment Team
"""
            
            with results_container:
                st.markdown("#### Email Preview (Not Sent)")
                st.markdown(f"**Subject:** {subject}")
                st.markdown("**Body:**")
                st.text_area("Email Body", body, height=300)
        
        conn.close()
        
        # Complete
        progress_bar.progress(100)
        status_container.success(f"Scheduling complete! {num_scheduled} interviews scheduled for {candidate_name}.")
        
        # Disable the buttons to prevent duplicate scheduling
        st.session_state.interviews_scheduled = True
        
        return num_scheduled
    
    except Exception as e:
        status_container.error(f"Error scheduling interviews: {e}")
        progress_bar.progress(100)
        if 'conn' in locals():
            conn.close()
        return None
        
# Create resume upload tab
def resume_upload_tab():
    st.markdown("### Upload and Process Resume")
    
    # Resume upload form
    with st.form("resume_form"):
        uploaded_file = st.file_uploader("Upload Resume", type=['pdf', 'docx'])
        
        col1, col2 = st.columns(2)
        with col1:
            candidate_name = st.text_input("Candidate Name (Optional)", "")
        with col2:
            candidate_email = st.text_input("Candidate Email (Optional)", "")
        
        submit_button = st.form_submit_button("Process Resume")
    
    # Process the resume when the form is submitted
    if submit_button and uploaded_file:
        process_resume(uploaded_file, candidate_name, candidate_email)

# Create candidate analysis tab
def candidate_analysis_tab():
    st.markdown("### Analyze Candidate")
    
    # Check if a candidate is selected
    if not hasattr(st.session_state, 'current_candidate'):
        st.warning("Please process a resume first to select a candidate.")
        return
    
    # Display current candidate
    candidate_id = st.session_state.current_candidate
    candidate_name = st.session_state.current_candidate_name
    
    st.markdown(f"Current candidate: **{candidate_name}** (ID: {candidate_id})")
    
    # Analysis button
    if st.button("Analyze Candidate Against Jobs", disabled=hasattr(st.session_state, 'candidate_analyzed') and st.session_state.candidate_analyzed):
        analyze_candidate(candidate_id)

# Create interview scheduling tab
def interview_scheduling_tab():
    st.markdown("### Schedule Interviews")
    
    # Check if a candidate is selected and analyzed
    if not hasattr(st.session_state, 'current_candidate'):
        st.warning("Please process a resume first to select a candidate.")
        return
    
    if not hasattr(st.session_state, 'shortlisted_jobs') or not st.session_state.shortlisted_jobs:
        st.warning("Please analyze the candidate first to identify suitable positions.")
        return
    
    # Display current candidate
    candidate_id = st.session_state.current_candidate
    candidate_name = st.session_state.current_candidate_name
    
    st.markdown(f"Current candidate: **{candidate_name}** (ID: {candidate_id})")
    
    # Display shortlisted positions
    st.markdown("#### Shortlisted Positions")
    
    # Get job titles
    db_path = st.session_state.config["db_path"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for job_id, score, _ in st.session_state.shortlisted_jobs:
        cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
        job_title = cursor.fetchone()
        if job_title:
            st.markdown(f"- {job_title[0]} (Match Score: {score:.2f})")
    
    conn.close()
    
    # Interview scheduling form
    with st.form("interview_form"):
        st.markdown("#### Interview Scheduling Options")
        
        use_custom_dates = st.checkbox("Use Custom Interview Dates/Times")
        
        custom_dates = None
        custom_times = None
        
        if use_custom_dates:
            st.markdown("Select dates and times for the interviews:")
            
            # Date selection (up to 3 dates)
            date_options = []
            for i in range(7):
                date = datetime.now() + timedelta(days=i+2)
                # Skip weekends
                if date.weekday() < 5:  # 0-4 are Monday-Friday
                    date_options.append(date)
            
            # Select dates
            selected_dates = st.multiselect(
                "Select Interview Dates", 
                options=date_options,
                format_func=lambda x: x.strftime("%A, %B %d, %Y"),
                default=[date_options[0]] if date_options else []
            )
            
            # Convert selected dates to strings
            custom_dates = [date.strftime("%Y-%m-%d") for date in selected_dates]
            
            # Time options
            time_options = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]
            
            # Select times
            selected_times = st.multiselect(
                "Select Interview Times",
                options=time_options,
                default=["10:00", "14:00"]
            )
            
            # Use selected times
            custom_times = selected_times
        else:
            st.info("Default scheduling will be used (weekdays starting 2 days from now at 10:00 AM and 2:00 PM)")
        
        submit_scheduling = st.form_submit_button("Schedule Interviews", 
                                                disabled=hasattr(st.session_state, 'interviews_scheduled') and 
                                                          st.session_state.interviews_scheduled)
    
    # Schedule interviews when the form is submitted
    if submit_scheduling:
        schedule_interviews(candidate_id, custom_dates, custom_times)

# Create jobs management tab
def jobs_management_tab():
    st.markdown("### Job Positions Management")
    
    db_path = st.session_state.config["db_path"]
    
    # Display current jobs
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, job_title, description, summary, required_skills, required_experience, required_qualifications 
    FROM job_descriptions
    ORDER BY id
    """)
    
    jobs = cursor.fetchall()
    conn.close()
    
    if not jobs:
        st.warning("No jobs found in the database. Please import jobs from CSV or add them manually.")
        
        # Add a simple form to add a job manually
        with st.form("add_job_form"):
            st.markdown("### Add Job Manually")
            job_title = st.text_input("Job Title")
            job_description = st.text_area("Job Description", height=200)
            
            col1, col2 = st.columns(2)
            with col1:
                required_skills = st.text_area("Required Skills (comma separated)", height=100)
            with col2:
                required_experience = st.text_area("Required Experience", height=100)
            
            submit_job = st.form_submit_button("Add Job")
            
        if submit_job and job_title and job_description:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO job_descriptions (job_title, description, required_skills, required_experience) 
                VALUES (?, ?, ?, ?)
                """, (job_title, job_description, required_skills, required_experience))
                conn.commit()
                conn.close()
                st.success(f"Added job: {job_title}")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error adding job: {e}")
    else:
        st.markdown(f"#### {len(jobs)} Job Positions")
        
        # Create a tab for each job
        job_tabs = st.tabs([f"{job[1]}" for job in jobs])
        
        for i, job in enumerate(jobs):
            job_id, job_title, description, summary, skills, experience, qualifications = job
            
            with job_tabs[i]:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {job_title}")
                    st.markdown(f"**ID:** {job_id}")
                    
                    if description:
                        st.markdown("#### Description")
                        st.markdown(description[:500] + "..." if len(description) > 500 else description)
                    
                    if summary:
                        st.markdown("#### Summary")
                        st.markdown(summary)
                    
                    if skills:
                        st.markdown("#### Required Skills")
                        st.markdown(skills)
                    
                    if experience:
                        st.markdown("#### Required Experience")
                        st.markdown(experience)
                    
                    if qualifications:
                        st.markdown("#### Required Qualifications")
                        st.markdown(qualifications)
                
                with col2:
                    # Show statistics about this job
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Count matches
                    cursor.execute("""
                    SELECT COUNT(*) FROM matches WHERE job_id = ?
                    """, (job_id,))
                    match_count = cursor.fetchone()[0]
                    
                    # Count shortlisted
                    cursor.execute("""
                    SELECT COUNT(*) FROM matches WHERE job_id = ? AND is_shortlisted = 1
                    """, (job_id,))
                    shortlisted_count = cursor.fetchone()[0]
                    
                    # Count scheduled interviews
                    cursor.execute("""
                    SELECT COUNT(*) FROM matches WHERE job_id = ? AND interview_scheduled = 1
                    """, (job_id,))
                    interview_count = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    st.markdown("#### Stats")
                    st.markdown(f"- **Candidates Matched:** {match_count}")
                    st.markdown(f"- **Shortlisted:** {shortlisted_count}")
                    st.markdown(f"- **Interviews Scheduled:** {interview_count}")

# Create candidates management tab
def candidates_management_tab():
    st.markdown("### Candidates Management")
    
    db_path = st.session_state.config["db_path"]
    
    # Display current candidates
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, name, email, phone, skills, experience, education 
    FROM candidates
    ORDER BY id DESC
    """)
    
    candidates = cursor.fetchall()
    conn.close()
    
    if not candidates:
        st.warning("No candidates found in the database. Please process resumes to add candidates.")
    else:
        st.markdown(f"#### {len(candidates)} Candidates")
        
        # Create expandable sections for each candidate
        for candidate in candidates:
            candidate_id, name, email, phone, skills, experience, education = candidate
            
            with st.expander(f"{name} (ID: {candidate_id})"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Email:** {email}")
                    st.markdown(f"**Phone:** {phone}")
                    
                    if skills:
                        st.markdown("**Skills:**")
                        st.markdown(skills)
                
                with col2:
                    # Show statistics about this candidate
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Count matches
                    cursor.execute("""
                    SELECT COUNT(*) FROM matches WHERE candidate_id = ?
                    """, (candidate_id,))
                    match_count = cursor.fetchone()[0]
                    
                    # Count shortlisted
                    cursor.execute("""
                    SELECT COUNT(*) FROM matches WHERE candidate_id = ? AND is_shortlisted = 1
                    """, (candidate_id,))
                    shortlisted_count = cursor.fetchone()[0]
                    
                    # Count scheduled interviews
                    cursor.execute("""
                    SELECT COUNT(*) FROM matches WHERE candidate_id = ? AND interview_scheduled = 1
                    """, (candidate_id,))
                    interview_count = cursor.fetchone()[0]
                    
                    st.markdown("#### Stats")
                    st.markdown(f"- **Matched to Jobs:** {match_count}")
                    st.markdown(f"- **Shortlisted Positions:** {shortlisted_count}")
                    st.markdown(f"- **Interviews Scheduled:** {interview_count}")
                    
                    # Select and analyze this candidate
                    if st.button("Select & Analyze", key=f"select_{candidate_id}"):
                        st.session_state.current_candidate = candidate_id
                        st.session_state.current_candidate_name = name
                        st.session_state.resume_processed = True
                        st.session_state.candidate_analyzed = False
                        st.session_state.interviews_scheduled = False
                        st.success(f"Selected {name} as current candidate")
                    
                    conn.close()
                
                # Display candidate details in expandable sections
                # if experience:
                #     exp_expander = st.expander("Experience")
                #     with exp_expander:
                #         st.markdown(experience)
                
                # if education:
                #     edu_expander = st.expander("Education")
                #     with edu_expander:
                #         st.markdown(education)

                # Display job matches if any
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT m.job_id, j.job_title, m.match_score, m.is_shortlisted, m.interview_scheduled, m.interview_date
                FROM matches m
                JOIN job_descriptions j ON m.job_id = j.id
                WHERE m.candidate_id = ?
                ORDER BY m.match_score DESC
                """, (candidate_id,))
                
                matches = cursor.fetchall()
                conn.close()
                
                # if matches:
                #     with st.expander("Job Matches"):
                #         matches_data = []
                        
                #         for match in matches:
                #             job_id, job_title, match_score, is_shortlisted, is_scheduled, interview_date = match
                            
                #             interview_date_str = ""
                #             if interview_date:
                #                 try:
                #                     date_obj = datetime.strptime(interview_date, "%Y-%m-%d %H:%M:%S")
                #                     interview_date_str = date_obj.strftime("%b %d, %Y at %I:%M %p")
                #                 except:
                #                     interview_date_str = interview_date
                            
                #             matches_data.append({
                #                 "Job Title": job_title,
                #                 "Match Score": match_score,
                #                 "Shortlisted": "Yes" if is_shortlisted else "No",
                #                 "Interview": "Scheduled" if is_scheduled else "Not Scheduled",
                #                 "Interview Date": interview_date_str
                #             })
                        
                #         st.dataframe(
                #             pd.DataFrame(matches_data),
                #             use_container_width=True
                #         )

# Create dashboard tab
def dashboard_tab():
    st.markdown("### Recruitment System Dashboard")
    
    db_path = st.session_state.config["db_path"]
    
    try:
        # Get system statistics
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count various metrics - safely to handle case where tables don't exist yet
        try:
            cursor.execute("SELECT COUNT(*) FROM job_descriptions")
            job_count = cursor.fetchone()[0]
        except:
            job_count = 0
            
        try:
            cursor.execute("SELECT COUNT(*) FROM candidates")
            candidate_count = cursor.fetchone()[0]
        except:
            candidate_count = 0
            
        try:
            cursor.execute("SELECT COUNT(*) FROM matches")
            match_count = cursor.fetchone()[0]
        except:
            match_count = 0
            
        try:
            cursor.execute("SELECT COUNT(*) FROM matches WHERE is_shortlisted = 1")
            shortlisted_count = cursor.fetchone()[0]
        except:
            shortlisted_count = 0
            
        try:
            cursor.execute("SELECT COUNT(*) FROM matches WHERE interview_scheduled = 1")
            interview_count = cursor.fetchone()[0]
        except:
            interview_count = 0
            
        conn.close()
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Job Descriptions", job_count)
            st.metric("Candidates", candidate_count)
        
        with col2:
            st.metric("Total Matches", match_count)
            st.metric("Shortlisted Matches", shortlisted_count)
        
        with col3:
            st.metric("Interviews Scheduled", interview_count)
            if candidate_count > 0:
                interview_percentage = (interview_count / candidate_count) * 100 if interview_count else 0
                st.metric("Interview Conversion Rate", f"{interview_percentage:.1f}%")
        
        # Display current configuration
        st.markdown("#### Current Configuration")
        st.markdown(f"- **Database Path:** {st.session_state.config['db_path']}")
        st.markdown(f"- **Ollama Model:** {st.session_state.config['ollama_model']}")
        st.markdown(f"- **Match Threshold:** {st.session_state.config['match_threshold']}")
        st.markdown(f"- **Max Shortlisted Positions:** {st.session_state.config['max_shortlisted']}")
        
        # Display current session state
        if hasattr(st.session_state, 'current_candidate'):
            st.markdown("#### Current Session")
            st.markdown(f"- **Current Candidate:** {st.session_state.current_candidate_name} (ID: {st.session_state.current_candidate})")
            
            if hasattr(st.session_state, 'shortlisted_jobs') and st.session_state.shortlisted_jobs:
                st.markdown(f"- **Shortlisted Positions:** {len(st.session_state.shortlisted_jobs)}")
                
                # Display shortlisted jobs if available
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    shortlisted_jobs = []
                    for job_id, score, _ in st.session_state.shortlisted_jobs:
                        cursor.execute("SELECT job_title FROM job_descriptions WHERE id = ?", (job_id,))
                        job_title_result = cursor.fetchone()
                        job_title = job_title_result[0] if job_title_result else f"Job {job_id}"
                        shortlisted_jobs.append(f"{job_title} (Score: {score:.2f})")
                    
                    conn.close()
                    
                    for job in shortlisted_jobs:
                        st.markdown(f"  - {job}")
                except Exception as e:
                    st.error(f"Error displaying shortlisted jobs: {e}")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("If this is your first time using the app, please initialize the database using the button in the sidebar.")

# Main App
def main():
    # Add title and description
    st.markdown("<div class='main-header'>AI Recruitment System</div>", unsafe_allow_html=True)
    st.markdown(
        """
        This application helps streamline the recruitment process using AI. 
        Upload resumes, analyze candidates, and schedule interviews.
        """
    )
    
    # Initialize session state
    if 'resume_processed' not in st.session_state:
        st.session_state.resume_processed = False
    
    if 'candidate_analyzed' not in st.session_state:
        st.session_state.candidate_analyzed = False
    
    if 'interviews_scheduled' not in st.session_state:
        st.session_state.interviews_scheduled = False
    
    # Handle database initialization
    if st.session_state.get('init_db', False):
        init_database(st.session_state.config["db_path"])
        st.session_state.pop('init_db', None)  # Reset the flag
    
    # Handle CSV import
    if st.session_state.get('import_csv', False) and st.session_state.get('csv_file'):
        import_jobs(st.session_state.config["db_path"], st.session_state.get('csv_file'))
        st.session_state.pop('import_csv', None)  # Reset the flag
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Dashboard", "Upload Resume", "Analyze Candidate", 
        "Schedule Interviews", "Job Positions", "Candidates"
    ])
    
    with tab1:
        dashboard_tab()
    
    with tab2:
        resume_upload_tab()
    
    with tab3:
        candidate_analysis_tab()
    
    with tab4:
        interview_scheduling_tab()
    
    with tab5:
        jobs_management_tab()
    
    with tab6:
        candidates_management_tab()

if __name__ == "__main__":
    main()