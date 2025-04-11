# Multi-Agent Recruitment System

This system automates the recruitment process by using AI agents to:
1. Summarize job descriptions
2. Extract information from candidate resumes
3. Match candidates to jobs
4. Schedule interviews with qualified candidates

## Prerequisites

- Python 3.8 or higher
- Ollama installed locally with a suitable LLM model (llama3 by default)
- PyPDF2, python-docx, and other required Python libraries

## Installation

1. Clone this repository
2. Install the required packages:
   
   pip install pandas PyPDF2 python-docx
   
3. Install Ollama following instructions at [https://ollama.ai/](https://ollama.ai/)
4. Pull the required model:
   
   ollama pull llama3
   

## Usage

### Setting up the database

Initialize the SQLite database:


python cli.py setup-db


### Importing job descriptions

First, you can validate your CSV file to ensure it's properly formatted:


python csv_validator.py path/to/job_descriptions.csv


This will show you a preview of your data and which columns will be used for job titles and descriptions.

Then, import job descriptions from the CSV file:


python cli.py import-jobs path/to/job_descriptions.csv


The system will automatically detect columns containing job titles and descriptions. Your CSV file should have:
- A column for job titles
- A column for job descriptions 
- Optionally, a third column for additional data

### Summarizing job descriptions

Summarize all job descriptions in the database:


python cli.py summarize


Or summarize a specific job:


python cli.py summarize --job-id 1


### Processing resumes

Process a resume without matching:


python cli.py process-resume path/to/resume.pdf --name "John Doe" --email "john@example.com"


Process a resume, match with jobs, and schedule interviews (if qualified):


python cli.py process-resume path/to/resume.pdf --name "John Doe" --email "john@example.com" --analyze


### Listing data

List all jobs:


python cli.py list-jobs


List all candidates:


python cli.py list-candidates


List all matches:


python cli.py list-matches


### Scheduling interviews

Schedule interviews for all shortlisted candidates who haven't been scheduled yet:


python cli.py schedule


### Configuration

Configure system settings:


python cli.py config --ollama-model llama3 --smtp-server smtp.gmail.com --smtp-port 587 --smtp-username "your-email@gmail.com" --smtp-password "your-app-password" --save


## System Architecture

The system consists of several AI agents that work together:

1. *Job Description Summarizer*: Extracts key elements from job descriptions
2. *Resume Processor*: Extracts data from candidate resumes
3. *Candidate Matcher*: Compares candidates against job requirements
4. *Interview Scheduler*: Sends personalized interview requests

All data is stored in a SQLite database for persistence.

## Email Configuration

To send actual emails, you need to configure SMTP settings:


python cli.py config --smtp-server smtp.gmail.com --smtp-username "your-email@gmail.com" --smtp-password "your-app-password" --save


For Gmail, you'll need to use an app password, not your regular password.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.