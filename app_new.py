import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime
from recommendation_model import get_courses_from_csv, generate_introduction
from assessment_model import generate_assessment  # Import the new assessment model

def process_assessment(assessment_text):
    if isinstance(assessment_text, list):
        assessment_text = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in assessment_text])
    elif not isinstance(assessment_text, str):
        assessment_text = str(assessment_text)

    # Try to extract JSON if it's embedded in markdown or text
    json_pattern = r'```json\s*([\s\S]*?)\s*```'
    json_match = re.search(json_pattern, assessment_text)
    
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass
    
    # Try to directly parse as JSON
    try:
        return json.loads(assessment_text)
    except:
        # If not valid JSON, return the raw text
        return {"raw_text": assessment_text}

# Set the title of the app with improved styling
st.set_page_config(page_title="EduWay AI Engine", layout="wide", page_icon="🎓")

# Custom CSS for better styling with hover effects and improved view learning path section
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Force light theme always — override dark mode ── */
    :root,
    [data-theme="dark"],
    [data-theme="light"] {
        --bg-primary:       #F8FAFC;
        --bg-card:          #FFFFFF;
        --bg-tab-list:      #F1F5F9;
        --bg-tab-active:    #FFFFFF;
        --bg-info:          #EFF6FF;
        --bg-path-intro:    #F0FDF4;
        --bg-regen:         #F8F5FF;
        --bg-assess:        #F0FDF4;
        --bg-save:          #FFFDF5;
        --border-main:      #E2E8F0;
        --border-info:      #BFDBFE;
        --border-path:      #BBF7D0;
        --border-regen:     #E9D5FF;
        --border-save:      #FEF08A;
        --text-primary:     #0F172A;
        --text-secondary:   #475569;
        --text-muted:       #64748B;
        --text-info:        #1E3A8A;
        --text-path:        #166534;
        --text-regen:       #6B21A8;
        --text-sub:         #1E293B;
        --text-option:      #334155;
        --shadow-sm:        rgba(0,0,0,0.05);
        --shadow-md:        rgba(0,0,0,0.08);
    }

    /* Force light background on all Streamlit containers regardless of theme */
    html, body, [class*="css"], .stApp,
    .stApp > div, section[data-testid="stSidebar"],
    div[data-testid="stAppViewContainer"],
    div[data-testid="stHeader"],
    div[data-testid="block-container"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Force Streamlit's own dark-mode text resets */
    p, span, label, div, h1, h2, h3, h4, li {
        color: #0F172A !important;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QS1h {display: none !important;}

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* ── Header ── */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.25rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-main);
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }
    .header-logo {
        height: 56px;
        width: 56px;
        object-fit: contain;
    }
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #0070C4 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .home-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.55rem 1.2rem;
        background: linear-gradient(135deg, #0070C4, #1E88E5);
        color: #FFFFFF !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        transition: opacity 0.2s ease, transform 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,112,196,0.35);
        white-space: nowrap;
    }
    .home-btn:hover {
        opacity: 0.88;
        transform: translateY(-1px);
    }

    /* ── Text & cards ── */
    .intro-text {
        font-size: 1rem;
        line-height: 1.6;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }
    .info-box {
        background-color: var(--bg-info);
        border: 1px solid var(--border-info);
        color: var(--text-info);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-sub);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .profile-card {
        background-color: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-main);
        box-shadow: 0 1px 3px var(--shadow-sm);
    }
    .path-introduction {
        background-color: var(--bg-path-intro);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-path);
        color: var(--text-path);
    }
    .path-content {
        background-color: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-main);
        box-shadow: 0 4px 6px -1px var(--shadow-sm);
    }
    .regenerate-container {
        margin-top: 1.5rem;
        background-color: var(--bg-regen);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border-regen);
    }
    .regenerate-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-regen);
        margin-bottom: 0.8rem;
    }
    .assessment-container {
        margin-top: 1.5rem;
        background-color: var(--bg-assess);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border-path);
    }
    .assessment-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-path);
        margin-bottom: 0.8rem;
    }
    .assessment-section {
        background-color: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-main);
        box-shadow: 0 1px 3px var(--shadow-sm);
    }
    .question {
        margin-bottom: 1.2rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--border-main);
    }
    .option {
        margin-left: 1.5rem;
        margin-bottom: 0.5rem;
        color: var(--text-option);
    }
    .correct-answer {
        font-weight: 600;
        color: #15803D;
    }
    .save-options {
        margin-top: 2rem;
        background-color: var(--bg-save);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border-save);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-tab-list);
        padding: 6px;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        color: var(--text-muted);
        font-weight: 500;
        transition: all 0.2s ease;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--bg-tab-active) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 1px 3px var(--shadow-md);
    }
</style>
""", unsafe_allow_html=True)

# Main header with logo and Back-to-Website button
st.markdown("""
<div class="header-container">
    <div class="header-left">
        <img src="https://raw.githubusercontent.com/RohanThakre7/eduway_AI_career_path/main/public/assets/logo1.png" class="header-logo" alt="EDUWAY Logo">
        <h1 class="main-header">EDUWAY AI Engine</h1>
    </div>
    <a href="https://eduway-ai-career-path.vercel.app" target="_blank" class="home-btn">
        &#8592; Back to Website
    </a>
</div>
""", unsafe_allow_html=True)

# About section with improved content and styling
st.markdown('<div class="intro-text">Welcome to the AI career assessment module. Analyze your current competencies, design tailored roadmaps, and assess specialized knowledge domains.</div>', unsafe_allow_html=True)

# Information box
st.markdown('<div class="info-box">ℹ️ Complete your information parameters below to structure your custom syllabus roadmap. You can regenerate or request localized testing materials anytime.</div>', unsafe_allow_html=True)

# Map UI categories to CSV domains
category_to_domain = {
    "Web Development": "Web Development",
    "Data Science": "Data Science",
    "Mobile Development": "Android Development",
    "AI/Machine Learning": "Machine Learning",
    "Cybersecurity": "Cybersecurity",
    "Cloud Computing": "Cloud Computing",
    "Game Development": "Game Development",
    "Other": "Web Development" # Fallback
}

# Initialize session state variables if they don't exist
if 'show_regenerate' not in st.session_state:
    st.session_state.show_regenerate = False
if 'show_assessment' not in st.session_state:
    st.session_state.show_assessment = False

# Create a cleaner form with tabs
tab1, tab2, tab3 = st.tabs(["Your Information", "View Learning Path", "Assessment"])

with tab1:
    st.markdown('<div class="sub-header">Personal Information</div>', unsafe_allow_html=True)
    
    with st.form("user_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
        
        with col2:
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            education_level = st.selectbox(
                "Education Level", 
                ["High School", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD", "Self-taught", "Other"]
            )
        
        st.markdown('<div class="sub-header">Learning Objectives</div>', unsafe_allow_html=True)
        
        learning_category = st.selectbox(
            "Category of Interest",
            ["Web Development", "Data Science", "Mobile Development", "AI/Machine Learning", 
             "Cybersecurity", "Cloud Computing", "Game Development", "Other"]
        )
        
        experience_level = st.select_slider(
            "Experience Level",
            options=["Beginner", "Intermediate", "Advanced", "Expert"]
        )
        
        available_time = st.slider(
            "Hours available per week for learning",
            min_value=1, max_value=40, value=10
        )
        
        goals = st.text_area(
            "Describe your specific learning goals and what you hope to achieve",
            placeholder="Example: I want to learn web development to build a personal portfolio website and eventually work as a frontend developer."
        )
        
        # Format the query to include all relevant information
        def format_query():
            return f"Generate a learning path for {learning_category} for a {experience_level.lower()} with {available_time} hours per week available. Goals: {goals}"
        
        # Add a submit button
        submitted = st.form_submit_button("Generate Learning Path")
        
        if submitted:
            if not name or not email or not goals:
                st.error("Please fill out all required fields marked with *")
            else:
                # Store the user information in session state
                st.session_state.user_info = {
                    "name": name,
                    "email": email,
                    "age": age,
                    "education_level": education_level,
                    "learning_category": learning_category,
                    "experience_level": experience_level,
                    "available_time": available_time,
                    "goals": goals,
                    "query": format_query()
                }
                
                # Generate recommendations and store in session state
                with st.spinner("Generating your personalized learning path..."):
                    # 1. Get AI Intro
                    path_introduction = generate_introduction(st.session_state.user_info)
                    
                    # 2. Get Deterministic Courses from CSV
                    csv_domain = category_to_domain.get(learning_category, "Web Development")
                    user_goals = st.session_state.user_info.get('goals', '')
                    courses_df = get_courses_from_csv(csv_domain, user_goals)
                    
                    st.session_state.path_introduction = path_introduction
                    st.session_state.courses_df = courses_df
                    st.session_state.show_regenerate = True
                
                # Show a success message and instruct to go to the next tab
                st.success("Your learning path has been generated successfully! Please go to the 'View Learning Path' tab to see your results.")

with tab2:
    st.markdown('<div class="sub-header">Your Personalized Learning Path</div>', unsafe_allow_html=True)
    
    if 'user_info' in st.session_state and 'path_introduction' in st.session_state:
        # Display user info in a cleaner format with hover effects
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header" style="margin-top:0">Learning Profile</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {st.session_state.user_info['name']}")
            st.write(f"**Education:** {st.session_state.user_info['education_level']}")
            st.write(f"**Category:** {st.session_state.user_info['learning_category']}")
        
        with col2:
            st.write(f"**Experience:** {st.session_state.user_info['experience_level']}")
            st.write(f"**Available Time:** {st.session_state.user_info['available_time']} hours/week")
            st.write(f"**Email:** {st.session_state.user_info['email']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Introduction Section with enhanced styling
        st.markdown('<div class="path-introduction">', unsafe_allow_html=True)
        st.markdown('### Your Learning Journey Overview', unsafe_allow_html=True)
        st.markdown(f'{st.session_state.path_introduction}', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Suggested Path Section with enhanced styling
        if 'courses_df' in st.session_state and not st.session_state.courses_df.empty:
            st.markdown('<div class="path-content">', unsafe_allow_html=True)
            st.markdown('### Your Personalized Learning Roadmap', unsafe_allow_html=True)
            
            # Display the dataframe with clickable links
            st.dataframe(
                st.session_state.courses_df,
                column_config={
                    "Link": st.column_config.LinkColumn("Course Link", display_text="Open Link"),
                    "Learning Pathway": st.column_config.TextColumn("Course Name", width="medium"),
                    "Duration": st.column_config.TextColumn("Duration"),
                    "Module": st.column_config.TextColumn("Module", width="medium")
                },
                hide_index=True,
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        elif 'courses_df' in st.session_state:
            st.warning("We currently don't have structured courses for this exact category in our database, but stay tuned as we expand our catalog!")
        

            
            # Add the new "Create Assessment" button below the regeneration container
            st.markdown("---")
            st.markdown("### Skill Assessment")
            
            if st.button("📝 Create Custom Assessment", key="create_assessment", help="Generate an assessment based on your learning path"):
                # Set show_assessment to true to display in the Assessment tab
                st.session_state.show_assessment = True
                
                # Pass empty string since the new static assessment ignores this anyway
                learning_path_data = ""
                
                # Generate the assessment
                with st.spinner("Creating your personalized assessment..."):
                    assessment_text = generate_assessment(learning_path_data, st.session_state.user_info)
                    st.session_state.assessment_text = assessment_text
                    
                    # Try to parse as JSON if possible
                    st.session_state.assessment_data = process_assessment(assessment_text)
                
                st.success("Your assessment has been created! Please go to the 'Assessment' tab to view it.")
        

        
    else:
        st.info("Please fill out the form in the 'Your Information' tab to generate your personalized learning path.")

# New Assessment Tab
with tab3:
    st.markdown('<div class="sub-header">Knowledge Assessment</div>', unsafe_allow_html=True)
    
    if 'show_assessment' in st.session_state and st.session_state.show_assessment and 'assessment_data' in st.session_state:
        # Display user info in the assessment tab as well
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-header" style="margin-top:0">Assessment Summary</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Candidate:** {st.session_state.user_info['name']}")
            st.write(f"**Topic Focus:** {st.session_state.user_info['learning_category']}")
        with col2:
            st.write(f"**Difficulty Level:** {st.session_state.user_info['experience_level']}")
            st.write(f"**Target Goal:** {st.session_state.user_info['goals'][:50]}...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        assessment_data = st.session_state.assessment_data
        
        # Interactive Quiz Implementation
        if "multiple_choice" in assessment_data:
            st.markdown("### 📝 Interactive Practice Quiz")
            user_answers = {}
            
            for i, q in enumerate(assessment_data["multiple_choice"]):
                st.markdown(f"**Question {i+1}**: {q['question']}")
                options = q['options']
                # Create radio selection for each question
                selected_opt = st.radio(
                    f"Select your answer for Question {i+1}:", 
                    options, 
                    key=f"q_radio_{i}",
                    index=None
                )
                user_answers[i] = selected_opt
                st.write("")
                
            if st.button("Submit Assessment & Verify Answers", type="primary"):
                score = 0
                total = len(assessment_data["multiple_choice"])
                
                st.markdown("---")
                st.markdown("### 📊 Quiz Results & Feedback")
                for i, q in enumerate(assessment_data["multiple_choice"]):
                    user_ans = user_answers.get(i)
                    correct_ans = q.get('correct_answer')
                    
                    st.write(f"**Question {i+1}**: {q['question']}")
                    st.write(f"- Your Answer: `{user_ans}`")
                    st.write(f"- Correct Answer: `{correct_ans}`")
                    
                    if user_ans == correct_ans:
                        st.success("✅ Correct!")
                        score += 1
                    else:
                        st.error("❌ Incorrect")
                    st.write("")
                
                percentage = int((score / total) * 100)
                if percentage >= 70:
                    st.balloons()
                    st.success(f"Excellent Job! You scored {score}/{total} ({percentage}%)!")
                else:
                    st.warning(f"Keep learning! You scored {score}/{total} ({percentage}%). Review the roadmap details to improve.")
                    
        # Check if we have raw text or other sections and print them below
        if "raw_text" in assessment_data:
            st.markdown(assessment_data["raw_text"])
            
        if "short_answer" in assessment_data:
            st.markdown("### Short Answer Questions (Self-Review)")
            for i, q in enumerate(assessment_data["short_answer"]):
                st.info(f"**Q{i+1}:** {q['question']}")
                if "guidance" in q:
                    st.write(f"*Expected Criteria:* {q['guidance']}")
                st.write("")
                
        if "practical_exercises" in assessment_data:
            st.markdown("### Practical Tasks & Exercises")
            for i, exercise in enumerate(assessment_data["practical_exercises"]):
                with st.expander(f"Task {i+1}: {exercise.get('title', 'Practical Lab')}"):
                    st.write(exercise.get('description', ''))
                    if "steps" in exercise:
                        st.write("**Suggested Workflow:**")
                        for idx, step in enumerate(exercise['steps']):
                            st.write(f"{idx+1}. {step}")
                    if "criteria" in exercise:
                        st.write("**Evaluation Criteria:**")
                        for crit in exercise['criteria']:
                            st.write(f"- {crit}")

    else:
        st.info("No assessment created yet. Please go to the 'View Learning Path' tab and click on 'Create Assessment'.")

# Footer with clean corporate design and links, set to stick to the bottom naturally
st.markdown("""
<div style="text-align: center; margin-top: 60px; padding: 24px; border-top: 1px solid #E2E8F0; width: 100%;">
    <p style="color: #475569; font-size: 0.9rem; font-weight: 500; margin: 0 0 8px 0;">EDUWAY AI Personalized Career & Skill Architecture</p>
    <p style="color: #94A3B8; font-size: 0.8rem; margin: 0;">© 2026 EduWay Platform. Designed for professional competency assessment. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
