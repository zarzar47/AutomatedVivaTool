import streamlit as st
import json
import gspread
import pandas as pd
import random
import time
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / 'questions.json'
NUM_QUESTIONS = 5
TIMER_DURATION_SECONDS = 300  # 5 minutes

# --- Google Sheets Connection ---
def connect_to_gsheet():
    """Connects to the Google Sheet and returns the worksheet."""
    try:
        # Use st.secrets for credentials
        creds = st.secrets["gcp_service_account"]
        sa = gspread.service_account_from_dict(creds)
        
        # Open the Google Sheet using the name from secrets
        sheet_name = st.secrets["gcp_service_account"]["sheet"]
        sh = sa.open(sheet_name)
        
        # Get the first worksheet
        worksheet = sh.get_worksheet(0)
        return worksheet
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        st.error("Please ensure your `secrets.toml` file is configured correctly in Streamlit Cloud.")
        return None

# --- Data Loading ---
def load_all_questions():
    """Loads all questions from the JSON file and flattens them into a single list."""
    try:
        with open(QUESTIONS_FILE, 'r') as f:
            # Handle potential empty file
            content = f.read()
            if not content:
                return []
            question_sets = json.loads(content)
        
        all_questions = []
        for question_list in question_sets.values():
            all_questions.extend(question_list)
        
        random.shuffle(all_questions)
        return all_questions
    except (FileNotFoundError, json.JSONDecodeError):
        st.error("Failed to load questions. Make sure 'questions.json' is present and correctly formatted.")
        return []

# --- State Management ---
def initialize_session():
    """Initializes session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
        st.session_state.erp = ""
        st.session_state.questions = []
        st.session_state.current_q_index = 0
        st.session_state.answers = []
        st.session_state.results_saved = False
        st.session_state.start_time = 0.0

def save_answer(q_index):
    """Callback to save the answer for a given question index."""
    radio_key = f"q_radio_{q_index}"
    user_choice_text = st.session_state.get(radio_key)
    
    if user_choice_text:
        question = st.session_state.questions[q_index]
        option_key = [k for k, v in question['options'].items() if v == user_choice_text][0]
        st.session_state.answers[q_index] = option_key

# --- UI Rendering ---
def render_home_page():
    """Renders the initial page to get student ERP."""
    st.title("Automated PL/SQL Viva System")
    erp = st.text_input("Please enter your ERP ID:", key="erp_input")
    
    if st.button("Start Viva"):
        if not erp.strip():
            st.error("ERP ID cannot be empty.")
            return

        all_questions = load_all_questions()
        if not all_questions or len(all_questions) < NUM_QUESTIONS:
            st.error("Not enough questions to start the viva. Please contact the administrator.")
            return
            
        st.session_state.erp = erp.strip()
        st.session_state.questions = random.sample(all_questions, NUM_QUESTIONS)
        st.session_state.answers = [None] * NUM_QUESTIONS
        st.session_state.page = 'viva'
        st.session_state.start_time = time.time()
        st.rerun()

def render_viva_page():
    """Renders the question and answer page."""
    if st.session_state.start_time == 0.0:
        st.session_state.start_time = time.time()

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = TIMER_DURATION_SECONDS - elapsed_time

    st_autorefresh(interval=1000, key="timer_refresh")

    if remaining_time <= 0:
        st.session_state.page = 'complete'
        st.rerun()

    st.info(f"Time Remaining: {int(remaining_time // 60)} minutes {int(remaining_time % 60)} seconds")

    q_index = st.session_state.current_q_index
    question = st.session_state.questions[q_index]
    
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
    with col1:
        st.header(f"Question {q_index + 1} of {NUM_QUESTIONS}")
    
    with col2:
        if st.session_state.current_q_index > 0:
            if st.button("Back"):
                st.session_state.current_q_index -= 1
                st.rerun()
    
    with col3:
        if st.session_state.current_q_index < NUM_QUESTIONS - 1:
            if st.button("Next"):
                st.session_state.current_q_index += 1
                st.rerun()

    st.subheader(question['question'])
    
    options = list(question['options'].values())
    
    previous_answer_key = st.session_state.answers[q_index]
    pre_selected_index = None
    if previous_answer_key:
        option_keys = list(question['options'].keys())
        if previous_answer_key in option_keys:
            pre_selected_index = option_keys.index(previous_answer_key)

    st.radio(
        "Choose your answer:",
        options,
        key=f"q_radio_{q_index}",
        index=pre_selected_index,
        on_change=save_answer,
        args=(q_index,)
    )

    if q_index == NUM_QUESTIONS - 1:
        if st.button("Finish Viva"):
            st.session_state.page = 'complete'
            st.rerun()

def render_completion_page():
    """Renders the final page and saves results to Google Sheets."""
    st.success(f"Thank you, {st.session_state.erp}. Your answers have been submitted.")
    st.balloons()

    if not st.session_state.results_saved:
        worksheet = connect_to_gsheet()
        if worksheet:
            final_answers = []
            for i, option_key in enumerate(st.session_state.answers):
                question = st.session_state.questions[i]
                final_answers.append({
                    'erp': st.session_state.erp,
                    'question_id': question.get('id', 'N/A'),
                    'selected_option': f'option {option_key.lower()}' if option_key else 'Not Answered'
                })

            if final_answers:
                df = pd.DataFrame(final_answers)
                
                # Check if sheet is empty to add headers
                if not worksheet.get_all_values():
                    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
                else:
                    worksheet.append_rows(df.values.tolist())
            
            st.session_state.results_saved = True

    st.subheader("Your Recorded Answers:")
    for i, option_key in enumerate(st.session_state.answers):
        question = st.session_state.questions[i]
        answer_text = "Not Answered"
        if option_key:
            answer_text = f"option {option_key.lower()}"
        st.text(f"- Question {question.get('id', 'N/A')}: {answer_text}")

    if st.button("Start New Viva"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Main App Logic ---
initialize_session()

if st.session_state.page == 'home':
    render_home_page()
elif st.session_state.page == 'viva':
    render_viva_page()
elif st.session_state.page == 'complete':
    render_completion_page()
