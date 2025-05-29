import os
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime
import google.generativeai as genai
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Fetch Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ Gemini API Key missing! Please add it to the .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"❌ Gemini Initialization Error: {str(e)}")
    st.stop()

# Define workout plan prompt template
workout_prompt = PromptTemplate(
    input_variables=["fitness_level", "goal", "duration", "equipment"],
    template=(
        "Create a personalized workout plan for a {fitness_level} individual "
        "whose goal is {goal}. The workout should last {duration} minutes "
        "and use {equipment} equipment. Provide step-by-step exercises with "
        "sets, reps, and rest intervals."
    ),
)

# Generate workout using Gemini
def generate_workout(fitness_level, goal, duration, equipment):
    prompt = workout_prompt.format(
        fitness_level=fitness_level,
        goal=goal,
        duration=duration,
        equipment=equipment,
    )
    try:
        response = model.generate_content(prompt)
        return response.text  # Gemini returns .text
    except Exception as e:
        st.error(f"❌ Error generating workout: {str(e)}")
        return f"An error occurred: {str(e)}"

# Function to create a PDF
def create_pdf(workout_plan, fitness_level, goal, duration, equipment):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Personalized Workout Plan", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fitness Level: {fitness_level}", ln=True)
    pdf.cell(200, 10, txt=f"Goal: {goal}", ln=True)
    pdf.cell(200, 10, txt=f"Duration: {duration} minutes", ln=True)
    pdf.cell(200, 10, txt=f"Equipment: {equipment}", ln=True)
    pdf.ln(10)
    
    pdf.multi_cell(0, 10, workout_plan)
    
    filename = f"Workout_Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# Streamlit App
def main():
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
        }
        .stSelectbox, .stNumberInput {
            background-color: white;
            border-radius: 5px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏋️‍♀️ Personalized Workout Planner")
    st.markdown("Generate a custom workout plan tailored to your needs!")

    with st.sidebar:
        st.header("Workout Preferences")
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
        goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Endurance", "General Fitness"])
        duration = st.number_input("Duration (minutes)", min_value=10, max_value=120, value=30, step=5)
        equipment = st.selectbox("Equipment Available", ["Bodyweight", "Dumbbells", "Gym Equipment", "Resistance Bands"])
        generate_button = st.button("Generate Workout Plan")

    if "workout_history" not in st.session_state:
        st.session_state.workout_history = []

    if generate_button:
        with st.spinner("Generating your workout plan..."):
            workout_plan = generate_workout(fitness_level, goal, duration, equipment)
            st.session_state.workout_history.append({
                "plan": workout_plan,
                "fitness_level": fitness_level,
                "goal": goal,
                "duration": duration,
                "equipment": equipment,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success("✅ Workout plan generated successfully!")

        st.subheader("Your Workout Plan")
        st.markdown(workout_plan)

        pdf_file = create_pdf(workout_plan, fitness_level, goal, duration, equipment)
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Download as PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )

    if st.session_state.workout_history:
        st.subheader("Workout History")
        for i, entry in enumerate(st.session_state.workout_history):
            with st.expander(f"Workout {i+1} - {entry['date']}"):
                st.write(f"**Fitness Level:** {entry['fitness_level']}")
                st.write(f"**Goal:** {entry['goal']}")
                st.write(f"**Duration:** {entry['duration']} minutes")
                st.write(f"**Equipment:** {entry['equipment']}")
                st.markdown(entry['plan'])

if __name__ == "__main__":
    main()
