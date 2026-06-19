import json

def generate_assessment(learning_path_data, user_info):
    """
    Returns a static assessment bypassing any AI generation to avoid rate limits.
    """
    category = user_info.get("learning_category", "Technology")
    experience = user_info.get("experience_level", "Beginner")
    
    # Create a static 5-question multiple choice assessment based on the category
    assessment = {
        "multiple_choice": [
            {
                "question": f"Which of the following is a fundamental concept in {category}?",
                "options": ["Version Control", "Variables & Functions", "Data Structures", "All of the above"],
                "correct_answer": "All of the above"
            },
            {
                "question": f"As a {experience} learner, what is the best way to practice {category} skills?",
                "options": ["Reading books only", "Watching tutorials without coding", "Building hands-on projects", "Memorizing syntax"],
                "correct_answer": "Building hands-on projects"
            },
            {
                "question": "What is the primary purpose of writing clean, well-documented code?",
                "options": ["To make the code run faster", "To make it easier for humans to read and maintain", "To pass compiler checks", "To save disk space"],
                "correct_answer": "To make it easier for humans to read and maintain"
            },
            {
                "question": "Which tool is essential for collaborative software development?",
                "options": ["Git / GitHub", "Photoshop", "Microsoft Word", "Calculator"],
                "correct_answer": "Git / GitHub"
            },
            {
                "question": f"When encountering a bug or error in {category}, what is the first step you should take?",
                "options": ["Give up", "Read the error message carefully", "Delete the code", "Ask someone else to fix it immediately"],
                "correct_answer": "Read the error message carefully"
            }
        ]
    }
    
    return assessment

def evaluate_user_answers(assessment, user_answers):
    """
    Not used dynamically anymore since UI evaluates multiple choice answers directly,
    but kept for API compatibility.
    """
    return "Evaluation complete."