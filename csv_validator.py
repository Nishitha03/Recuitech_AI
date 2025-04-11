#!/usr/bin/env python3
import pandas as pd
import argparse
import os

def validate_csv(csv_path):
    """Validate and display information about a job descriptions CSV file"""
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return
    
    try:
        # Try to read with different encodings
        encodings = ['cp1252', 'utf-8', 'latin1']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("Error: Could not read CSV file with any of the standard encodings")
            return
        
        # Display basic information
        print(f"\nCSV File: {csv_path}")
        print(f"Encoding: {used_encoding}")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        print("\nColumns:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # Display the first few rows
        print("\nPreview (first 3 rows):")
        print(df.head(3).to_string())
        
        # Check for common column names
        job_title_col = next((col for col in df.columns 
                             if col.lower().strip() in ['job title', 'jobtitle', 'title']), None)
        job_desc_col = next((col for col in df.columns 
                            if col.lower().strip() in ['job description', 'jobdescription', 'description']), None)
        
        print("\nColumn detection:")
        if job_title_col:
            print(f"  Job Title column detected: '{job_title_col}'")
        else:
            print("  No Job Title column detected - will use first column")
            
        if job_desc_col:
            print(f"  Job Description column detected: '{job_desc_col}'")
        else:
            print("  No Job Description column detected - will use second column")
        
        print("\nSuggested import command:")
        print(f"python cli.py import-jobs {csv_path}")
        
    except Exception as e:
        print(f"Error validating CSV: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate a job descriptions CSV file')
    parser.add_argument('csv_path', help='Path to the CSV file')
    args = parser.parse_args()
    
    validate_csv(args.csv_path)