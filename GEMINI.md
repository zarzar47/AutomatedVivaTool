
# Project Overview

This project is an automated technical viva system built with Python and the Streamlit framework. It provides a web-based interface for students to take a viva (oral examination) consisting of multiple-choice questions. The system presents a random set of questions to each student, records their answers, and saves them to a CSV file.

The project also includes a separate script for marking the vivas. This script reads the recorded answers, compares them with the correct answers, calculates the total marks for each student, and generates a new CSV file with the results. Additionally, it provides statistics on question difficulty, helping to identify the hardest questions for the students.

## Key Features

-   **Automated Viva:** A web-based interface for students to take a viva.
-   **Randomized Questions:** Each student receives a random set of questions.
-   **Timed Viva:** The viva is timed, and it ends automatically when the time is up.
-   **Answer Recording:** Student answers are saved to a CSV file for later processing.
-   **Automated Marking:** A script to automatically mark the vivas and calculate scores.
-   **Question Statistics:** The marking script provides statistics on question difficulty.
-   **Adjustable Question Weights:** The marking script allows for adjusting the weight of each question.

# Building and Running

This project uses a Python virtual environment to manage its dependencies. The following instructions assume you have Python 3 and `pip` installed.

## 1. Setup the Virtual Environment

If you haven't already, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install Dependencies

Install the required Python packages using `pip`:

```bash
.venv/bin/pip install -r requirements.txt
```

## 3. Running the Viva Application

To start the main viva application, run the following command:

```bash
streamlit run viva.py
```

This will start a local web server, and you can access the application in your browser at the URL provided in the terminal.

## 4. Running the Marking Script

To mark the vivas and generate the `marked_results.csv` file, run the following command:

```bash
python3 marker.py
```

This script will read the `results.csv` file, calculate the scores, and create a new `marked_results.csv` file. It will also print the question difficulty statistics to the console.

# Development Conventions

-   **Virtual Environment:** All dependencies are managed within a Python virtual environment located in the `.venv` directory.
-   **Separation of Concerns:** The project is divided into two main scripts:
    -   `viva.py`: The main Streamlit application for conducting the viva.
    -   `marker.py`: The script for marking the vivas and generating reports.
-   **Configuration:** Key parameters, such as the number of questions and the timer duration, are defined as constants at the beginning of the `viva.py` script, making them easy to adjust.
-   **Data Storage:**
    -   `questions.json`: Stores the viva questions, options, and correct answers.
    -   `results.csv`: Stores the raw results of the vivas taken by students.
    -   `marked_results.csv`: Stores the final marks for each student after running the marking script.
