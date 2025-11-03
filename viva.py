import streamlit as st
import json
import csv
import random
import os
import time
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / 'questions.json'
RESULTS_FILE = BASE_DIR / 'results.csv'
NUM_QUESTIONS = 5
TIMER_DURATION_SECONDS = 300  # 5 minutes

# --- Data Loading ---
def load_all_questions():
    """Loads all questions from the JSON file and flattens them into a single list."""
    with open(QUESTIONS_FILE, 'r') as f:
        question_sets = json.load(f)
    
    all_questions = []
    for question_list in question_sets.values():
        all_questions.extend(question_list)
    return all_questions

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

# --- UI Rendering ---
def render_home_page():
    """Renders the initial page to get student ERP."""
    st.title("Automated PL/SQL Viva System")
    erp = st.text_input("Please enter your ERP ID:", key="erp_input")
    
    if st.button("Start Viva"):
        if erp.strip():
            st.session_state.erp = erp.strip()
            all_questions = load_all_questions()
            st.session_state.questions = random.sample(all_questions, NUM_QUESTIONS)
            st.session_state.page = 'viva'
            st.session_state.start_time = time.time()
            st.rerun()
        else:
            st.error("ERP ID cannot be empty.")

def render_viva_page():
    """Renders the question and answer page."""
    # Timer logic
    if st.session_state.start_time == 0.0:
        st.session_state.start_time = time.time()

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = TIMER_DURATION_SECONDS - elapsed_time

    st_autorefresh(interval=1000, key="timer_refresh")

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = TIMER_DURATION_SECONDS - elapsed_time

    st.info(f"Time Remaining: {int(remaining_time // 60)} minutes {int(remaining_time % 60)} seconds")

    if remaining_time <= 0:
        st.session_state.page = 'complete'
        st.rerun()

    q_index = st.session_state.current_q_index
    question = st.session_state.questions[q_index]
    
    st.header(f"Question {q_index + 1} of {NUM_QUESTIONS}")
    st.subheader(question['question'])
    
    options = list(question['options'].values())
    # Use a form to prevent rerun on radio button selection
    with st.form(key=f"q_form_{q_index}"):
        user_choice = st.radio("Choose your answer:", options, key=f"q_radio_{q_index}")
        submitted = st.form_submit_button("Submit Answer")

        if submitted:
            # Find the option key (A, B, C, D) corresponding to the chosen text
            option_key = [k for k, v in question['options'].items() if v == user_choice][0]
            
            st.session_state.answers.append({
                'erp': st.session_state.erp,
                'question_id': question['id'],
                'selected_option': f'option {option_key.lower()}'
            })
            
            if st.session_state.current_q_index < NUM_QUESTIONS - 1:
                st.session_state.current_q_index += 1
            else:
                st.session_state.page = 'complete'
            st.rerun()

def render_completion_page():
    """Renders the final page after the viva is complete."""
    st.success(f"Thank you, {st.session_state.erp}. Your answers have been submitted.")
    st.balloons()

    # Save results to CSV
    if not st.session_state.results_saved:
        file_exists = os.path.isfile(RESULTS_FILE)
        with open(RESULTS_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['erp', 'question_id', 'selected_option'])
            if not file_exists:
                writer.writeheader()
            writer.writerows(st.session_state.answers)
        st.session_state.results_saved = True

    st.subheader("Your Recorded Answers:")
    for ans in st.session_state.answers:
        st.text(f"- Question {ans['question_id']}: {ans['selected_option']}")

    if st.button("Start New Viva"):
        # Clear session state to allow a new user to start
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
