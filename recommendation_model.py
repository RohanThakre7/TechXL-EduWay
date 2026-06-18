import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('new.env')

# Configure Google Generative AI
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_courses_from_csv(domain, csv_filename="one.csv"):
    """
    Reads the CSV and filters courses based on the requested domain.
    """
    try:
        data_path = os.path.join(os.getcwd(), csv_filename)
        if not os.path.exists(data_path):
            print(f"Error: CSV file not found at {data_path}")
            return pd.DataFrame()

        df = pd.read_csv(data_path)
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Check if 'Domain' column exists
        if 'Domain' not in df.columns:
            print("Error: 'Domain' column not found in CSV.")
            return df
            
        # Filter by domain (case-insensitive partial match for safety)
        filtered_df = df[df['Domain'].str.contains(domain, case=False, na=False)]
        
        # Drop the Domain column for display purposes
        if not filtered_df.empty and 'Domain' in filtered_df.columns:
            filtered_df = filtered_df.drop(columns=['Domain'])
            
        return filtered_df
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return pd.DataFrame()

def generate_introduction(user_info):
    """
    Uses Gemini to generate a personalized introductory paragraph.
    """
    try:
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        prompt = f"""
        You are an expert education advisor. A user wants to learn about {user_info['learning_category']}.
        
        User Profile:
        - Experience Level: {user_info['experience_level']}
        - Available Time: {user_info['available_time']} hours per week
        - Goals: {user_info['goals']}
        
        Please provide a short, single 5-6 sentence introductory paragraph that:
        - Introduces the field of {user_info['learning_category']}.
        - Acknowledges their current experience level and goals.
        - Provides general guidance and encouragement on how to approach their learning journey given their available time.
        
        Do not include any lists, tables, or course recommendations in your response. Just the introductory paragraph.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating introduction: {e}")
        return f"Welcome to your learning journey in {user_info['learning_category']}! Based on your profile as a {user_info['experience_level']}, we have curated a specific roadmap for you. Dedicating {user_info['available_time']} hours a week is a great commitment towards achieving your goals. Follow the path below to get started."
