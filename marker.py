
import json
import csv
from collections import defaultdict

# --- Configuration ---
QUESTIONS_FILE = 'questions.json'
RESULTS_FILE = 'results.csv'
MARKED_RESULTS_FILE = 'marked_results.csv'

def get_question_weights():
    """
    This function defines the weight for each question.
    By default, all questions are weighted equally (1 point).
    You can adjust the weights here to make some questions worth more or less.
    For example, to make question 'A1' worth 2 points, change its value to 2.
    """
    # To adjust weights, modify the values in the dictionary below
    # e.g., return {'A1': 2, 'A2': 1, 'A3': 1, ...}
    return defaultdict(lambda: 1)

def load_questions():
    """Loads all questions from the JSON file and creates a lookup dictionary."""
    with open(QUESTIONS_FILE, 'r') as f:
        question_sets = json.load(f)
    
    all_questions = {}
    for question_list in question_sets.values():
        for question in question_list:
            all_questions[question['id']] = question
    return all_questions

def mark_vivas(questions, weights):
    """Marks the viva results and calculates question difficulty."""
    student_scores = defaultdict(float)
    question_stats = defaultdict(lambda: {'correct': 0, 'incorrect': 0})

    with open(RESULTS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            erp = row['erp']
            question_id = row['question_id']
            selected_option_str = row['selected_option'] # e.g., "option c"
            
            # Extract the letter from "option c" -> "c"
            selected_option_letter = selected_option_str.split(' ')[-1].upper()
            
            question = questions.get(question_id)
            if question:
                correct_answer = question['answer']
                weight = weights[question_id]
                
                if selected_option_letter == correct_answer:
                    student_scores[erp] += weight
                    question_stats[question_id]['correct'] += 1
                else:
                    question_stats[question_id]['incorrect'] += 1
            else:
                print(f"Warning: Question ID '{question_id}' from results not found in questions file.")

    return student_scores, question_stats

def write_marked_results(student_scores):
    """Writes the final scores to the marked results CSV file."""
    with open(MARKED_RESULTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['erp', 'total_marks'])
        for erp, score in sorted(student_scores.items()):
            writer.writerow([erp, score])

def print_difficulty_stats(question_stats, questions):
    """Prints statistics about question difficulty."""
    print("\n--- Question Difficulty Statistics ---")
    print("The following questions are sorted from hardest to easiest.\n")
    
    difficulty_list = []
    for q_id, stats in question_stats.items():
        total_attempts = stats['correct'] + stats['incorrect']
        if total_attempts > 0:
            correct_percentage = (stats['correct'] / total_attempts) * 100
            difficulty_list.append({
                'id': q_id,
                'percentage': correct_percentage,
                'correct': stats['correct'],
                'incorrect': stats['incorrect'],
                'total': total_attempts
            })

    # Sort by the percentage of correct answers (ascending)
    sorted_difficulty = sorted(difficulty_list, key=lambda x: x['percentage'])

    for item in sorted_difficulty:
        question_text = questions.get(item['id'], {}).get('question', 'N/A')
        print(f"Question ID: {item['id']} - '{question_text}'")
        print(f"  - Correct Answers: {item['correct']}/{item['total']} ({item['percentage']:.2f}%)")
        print("-" * 20)

def main():
    """Main function to run the marking process."""
    print("Starting the marking process...")
    
    # 1. Define question weights
    question_weights = get_question_weights()
    
    # 2. Load questions
    questions = load_questions()
    
    # 3. Mark vivas
    student_scores, question_stats = mark_vivas(questions, question_weights)
    
    # 4. Write results to a new CSV
    write_marked_results(student_scores)
    print(f"\nSuccessfully created '{MARKED_RESULTS_FILE}' with student scores.")
    
    # 5. Display difficulty statistics
    print_difficulty_stats(question_stats, questions)

if __name__ == "__main__":
    main()
