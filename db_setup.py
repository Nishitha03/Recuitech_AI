import sqlite3
import pandas as pd
import os

def setup_database():
    """Create SQLite database and required tables"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    # Create job_descriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT NOT NULL,
        description TEXT NOT NULL,
        extra_field TEXT,                  /* For the third column in your CSV */
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        candidate_id INTEGER,
        match_score REAL,
        is_shortlisted BOOLEAN DEFAULT 0,
        interview_scheduled BOOLEAN DEFAULT 0,
        interview_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES job_descriptions (id),
        FOREIGN KEY (candidate_id) REFERENCES candidates (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database setup complete!")

def import_jobs_from_csv(csv_path):
    """Import job descriptions from CSV file into the database"""
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    try:
        # Read CSV file with explicit encoding
        df = pd.read_csv(csv_path, encoding='cp1252')
        
        # Check if the expected columns exist
        # Normalize column names to account for case differences
        columns = {col.lower().strip(): col for col in df.columns}
        
        job_title_col = next((col for key, col in columns.items() 
                             if 'job title' in key or 'jobtitle' in key), None)
        job_desc_col = next((col for key, col in columns.items() 
                            if 'job description' in key or 'jobdescription' in key or 'description' in key), None)
        
        if not job_title_col or not job_desc_col:
            print("Warning: Expected columns not found. Using the first two columns as Job Title and Job Description.")
            job_title_col = df.columns[0]
            job_desc_col = df.columns[1]
            
        print(f"Using '{job_title_col}' as Job Title column")
        print(f"Using '{job_desc_col}' as Job Description column")
        
        # Connect to database
        conn = sqlite3.connect('recruitment.db')
        
        # Import data
        for _, row in df.iterrows():
            cursor = conn.cursor()
            
            # Check if there's a third column to import
            if len(df.columns) >= 3:
                extra_field = row[df.columns[2]] if not pd.isna(row[df.columns[2]]) else None
                cursor.execute('''
                INSERT INTO job_descriptions (job_title, description, extra_field)
                VALUES (?, ?, ?)
                ''', (row[job_title_col], row[job_desc_col], extra_field))
            else:
                cursor.execute('''
                INSERT INTO job_descriptions (job_title, description)
                VALUES (?, ?)
                ''', (row[job_title_col], row[job_desc_col]))
        
        conn.commit()
        conn.close()
        
        print(f"Successfully imported {len(df)} job descriptions into the database")
    
    except Exception as e:
        print(f"Error importing CSV data: {str(e)}")

if __name__ == "__main__":
    setup_database()
    
    # Replace with your actual CSV path
    csv_path = "job_descriptions.csv"
    import_jobs_from_csv(csv_path)