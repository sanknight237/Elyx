# Elyx
Health care

This project is a Streamlit web application designed to visualize the 8-month health journey of a member, Rohan Patel. It provides an interactive timeline of key health events and decisions, and uses the conversation log to trace back to the specific discussions that provided the rationale for each action.

 ****Running the Application Locally****
Follow these steps to set up and run the project on your local machine.

Prerequisites
Before you begin, ensure you have the following installed on your system:

Python (version 3.8 or higher)

pip (Python's package installer)

Step 1: Clone the Repository
First, clone this repository to your local machine using the following command in your terminal or command prompt:

git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name

(Replace your-username and your-repository-name with your actual GitHub details)

Step 2: Set Up a Virtual Environment (Recommended)
It is highly recommended to create a virtual environment to keep the project's dependencies isolated from your system's Python installation.

On Windows:

python -m venv venv
.\venv\Scripts\activate

On macOS / Linux:

python3 -m venv venv
source venv/bin/activate

Step 3: Install Required Packages
With your virtual environment activated, install all the necessary Python libraries using the requirements.txt file. This file contains the exact versions of the packages needed to run the app.

pip install -r requirements.txt

Step 4: Run the Streamlit App
You are now ready to launch the application. Run the following command from the root directory of the project (the elyx_visualization folder):

******(streamlit run app.py)******

Your web browser should automatically open a new tab with the application running. If it doesn't, the terminal will provide a Local URL (usually http://localhost:8501) that you can copy and paste into your browser's address bar.
