import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime
from recommendation_model import generate_learning_path, GenerateLearningPathIndexEmbeddings
from assessment_model import generate_assessment  # Import the new assessment model

# Function to check and update the FAISS index
def update_faiss_index(csv_filename):
    faiss_vectorstore_foldername = "faiss_learning_path_index"
    csv_last_modified = datetime.fromtimestamp(os.path.getmtime(csv_filename))
    index_last_modified = None
    if os.path.exists(faiss_vectorstore_foldername):
        index_last_modified = datetime.fromtimestamp(os.path.getmtime(faiss_vectorstore_foldername))
    if not os.path.exists(faiss_vectorstore_foldername) or csv_last_modified > index_last_modified:
        print(' -- Creating a new FAISS vector store from chunked text and Gemini embeddings.')
        GenerateLearningPathIndexEmbeddings(csv_filename)
        print(f' -- Saved the newly created FAISS vector store at "{faiss_vectorstore_foldername}".')
    else:
        print(f' -- Found existing FAISS vector store at "{faiss_vectorstore_foldername}", loading from cache.')

# Function to split response into introduction and table
def process_recommendation(recommendation_text):
    # Look for the table marker
    table_pattern = r'\|\s*Learning Pathway\s*\|\s*duration\s*\|\s*link\s*\|\s*Module\s*\|'
    
    # Check if the pattern exists in the text
    if re.search(table_pattern, recommendation_text):
        # Split the text at the table marker
        parts = re.split(table_pattern, recommendation_text, 1)
        
        path_introduction = parts[0].strip()
        path_content = '| Learning Pathway | duration | link | Module |\n' + parts[1].strip()
        
        return path_introduction, path_content
    else:
        # If table format isn't found, return the whole text as introduction
        return recommendation_text, ""

# Function to parse JSON assessment response
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
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #0070C4 0%, #1E88E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .intro-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .info-box {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E3A8A;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1E293B;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .profile-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .path-introduction {
        background-color: #F0FDF4;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #BBF7D0;
        color: #166534;
    }
    .path-content {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .regenerate-container {
        margin-top: 1.5rem;
        background-color: #F8F5FF;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E9D5FF;
    }
    .regenerate-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6B21A8;
        margin-bottom: 0.8rem;
    }
    .assessment-container {
        margin-top: 1.5rem;
        background-color: #F0FDF4;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #BBF7D0;
    }
    .assessment-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #166534;
        margin-bottom: 0.8rem;
    }
    .assessment-section {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .question {
        margin-bottom: 1.2rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid #F1F5F9;
    }
    .option {
        margin-left: 1.5rem;
        margin-bottom: 0.5rem;
        color: #334155;
    }
    .correct-answer {
        font-weight: 600;
        color: #15803D;
    }
    .save-options {
        margin-top: 2rem;
        background-color: #FFFDF5;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #FEF08A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: transparent;
        border-radius: 6px;
        padding: 8px 16px;
        color: #64748B;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main header with custom styling
st.markdown('<div class="main-header">🎓 EduWay AI Career Planner</div>', unsafe_allow_html=True)

# About section with improved content and styling
st.markdown('<div class="intro-text">Analyze your professional profiles, customize learning paths, and run specialized skill checks instantly. Powered by advanced artificial intelligence.</div>', unsafe_allow_html=True)

# Information box
st.markdown('<div class="info-box">ℹ️ Complete your information parameters below to structure your custom syllabus roadmap. You can regenerate or request localized testing materials anytime.</div>', unsafe_allow_html=True)

# Define the CSV file path
csv_filename = "one.csv"

# Update the FAISS index if necessary
update_faiss_index(csv_filename)

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
                    recommendations = generate_learning_path(format_query())
                    path_introduction, path_content = process_recommendation(recommendations)
                    
                    st.session_state.path_introduction = path_introduction
                    st.session_state.path_content = path_content
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
        if st.session_state.path_content:
            st.markdown('<div class="path-content">', unsafe_allow_html=True)
            st.markdown('### Your Personalized Learning Roadmap', unsafe_allow_html=True)
            st.markdown(f'{st.session_state.path_content}', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add the regeneration feature with enhanced styling
        if st.session_state.show_regenerate:
            st.markdown("### Adjust & Customise")
            
            if st.button("🔄 Customize or Regenerate Roadmap", key="regenerate_button", help="Click to customize your learning path further"):
                st.session_state.regenerate_expanded = True
            
            if 'regenerate_expanded' in st.session_state and st.session_state.regenerate_expanded:
                with st.form("regenerate_form"):
                    updated_requirements = st.text_area(
                        "What updates would you like to make to your learning path?",
                        placeholder="Example: I'd like more focus on practical projects, or I need resources that are free, or I want to learn more about specific technologies like React."
                    )
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        regenerate_submitted = st.form_submit_button("Generate Updated Path", help="Submit to create a new personalized path")
                    
                    if regenerate_submitted and updated_requirements:
                        # Create a new query by combining the original with the update request
                        original_query = st.session_state.user_info["query"]
                        updated_query = f"{original_query} Additional requirements: {updated_requirements}"
                        
                        # Generate new recommendations
                        with st.spinner("Regenerating your personalized learning path..."):
                            new_recommendations = generate_learning_path(updated_query)
                            new_path_introduction, new_path_content = process_recommendation(new_recommendations)
                            
                            # Update session state
                            st.session_state.path_introduction = new_path_introduction
                            st.session_state.path_content = new_path_content
                            st.session_state.regenerate_expanded = False
                            
                            # Store the updated query
                            st.session_state.user_info["query"] = updated_query
                            
                            st.success("Your learning path has been updated successfully!")
                            st.experimental_rerun()
            
            # Add the new "Create Assessment" button below the regeneration container
            st.markdown("---")
            st.markdown("### Skill Assessment")
            
            if st.button("📝 Create Custom Assessment", key="create_assessment", help="Generate an assessment based on your learning path"):
                # Set show_assessment to true to display in the Assessment tab
                st.session_state.show_assessment = True
                
                # Combine path introduction and content for assessment context
                learning_path_data = st.session_state.path_introduction
                if st.session_state.path_content:
                    learning_path_data += "\n\n" + st.session_state.path_content
                
                # Generate the assessment
                with st.spinner("Creating your personalized assessment..."):
                    assessment_text = generate_assessment(learning_path_data, st.session_state.user_info)
                    st.session_state.assessment_text = assessment_text
                    
                    # Try to parse as JSON if possible
                    st.session_state.assessment_data = process_assessment(assessment_text)
                
                st.success("Your assessment has been created! Please go to the 'Assessment' tab to view it.")
        
        # Add download and sharing options with enhanced styling
        st.markdown("---")
        st.markdown("### Save & Share Roadmap")
        
        # Format the text content for plain text export
        text_content = f"EDUWAY AI PERSONALIZED LEARNING ROADMAP\n"
        text_content += f"=======================================\n"
        text_content += f"Profile Name: {st.session_state.user_info['name']}\n"
        text_content += f"Category: {st.session_state.user_info['learning_category']}\n"
        text_content += f"Experience Level: {st.session_state.user_info['experience_level']}\n"
        text_content += f"Time Commitment: {st.session_state.user_info['available_time']} hours/week\n"
        text_content += f"Goals: {st.session_state.user_info['goals']}\n\n"
        text_content += f"OVERVIEW\n--------\n{st.session_state.path_introduction}\n\n"
        if st.session_state.path_content:
            text_content += f"ROADMAP DETAIL\n--------------\n{st.session_state.path_content}\n"
            
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="🔽 Download Roadmap as Text File",
                data=text_content,
                file_name=f"EduWay_Learning_Path_{st.session_state.user_info['name'].replace(' ', '_')}.txt",
                mime="text/plain",
                help="Click to save your customized learning path layout as a local text document."
            )
        
        with col2:
            # Generate email mailto link
            import urllib.parse
            subject = urllib.parse.quote("My EduWay Learning Roadmap")
            body = urllib.parse.quote(text_content[:1000] + "\n\n...[Truncated, download full text to read]")
            mailto_link = f"mailto:{st.session_state.user_info['email']}?subject={subject}&body={body}"
            st.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:0.5rem; background-color:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; color:#1E40AF; cursor:pointer;">📧 Email Learning Path</button></a>', unsafe_allow_html=True)
        
        # Add share buttons
        st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            # WhatsApp share link
            share_text = urllib.parse.quote(f"Hey! Check out my personalized AI Career Roadmap for {st.session_state.user_info['learning_category']} on EduWay!")
            whatsapp_url = f"https://api.whatsapp.com/send?text={share_text}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:0.5rem; background-color:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; color:#166534; cursor:pointer;">📱 Share via WhatsApp</button></a>', unsafe_allow_html=True)
        with col2:
            # JS copy url button
            copy_js = """
            <button onclick="navigator.clipboard.writeText(window.location.href); alert('EduWay Engine link copied to clipboard!');" style="width:100%; padding:0.5rem; background-color:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; color:#475569; cursor:pointer;">🔗 Copy App Link</button>
            """
            st.markdown(copy_js, unsafe_allow_html=True)
        with col3:
            st.download_button(
                label="📋 Export as Raw Markdown",
                data=text_content,
                file_name="roadmap.md",
                mime="text/markdown"
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
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

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #E2E8F0;">
    <p style="color: #64748B; font-size: 0.85rem;">© 2026 EduWay Learning Path Assistant. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
