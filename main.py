import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq

def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


# Streamlit page configuration
st.set_page_config(
    page_title="Sports Analysis AI",
    page_icon="🏆",
    layout="centered",
)

# Load environment variables
try:
    secrets = dotenv_values(".env")  # for dev env
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except:
    secrets = st.secrets  # for streamlit deployment
    GROQ_API_KEY = secrets["GROQ_API_KEY"]

# Save the api_key to environment variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initial messages and context
INITIAL_RESPONSE = "Hello! I'm your Sports Analysis AI. I can help with equipment suggestions, diet plans, and pro player stats. Let's get started!"
INITIAL_MSG = "Welcome to the Sports Analysis AI. How can I assist you today? I can give you suggestions about your sport, equipment, and diet or show you stats of pro players."
CHAT_CONTEXT = "You're a sports analysis assistant. You help users with equipment, diet suggestions, and displaying pro player stats. When the user provides their sport, you ask for equipment and diet details. If the user wants to see pro player stats, you provide those as well."

client = Groq()

# Initialize the chat history if present as streamlit session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE},
    ]

# Page header
st.title("Welcome to Sports Analysis AI!")
st.caption("Helping You Improve Your Game 🏅")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar='🤖' if message["role"] == "assistant" else "🗨️"):
        st.markdown(message["content"])

# Sidebar for navigation (sport selection, diet, equipment)
with st.sidebar:
    st.header("Sports Assistant Options")
    
    # Radio buttons to choose between sports analysis or pro player stats
    choice = st.radio("What would you like to know?", ["Sport Analysis", "Pro Player Stats"])
    
    if choice == "Sport Analysis":
        sport = st.selectbox("Select your sport", ["Football", "Basketball", "Tennis", "Baseball", "Other"])
        equipment = st.text_input("What equipment do you need?")
        diet = st.text_area("What is your current diet or dietary requirements?")
        
    if choice == "Pro Player Stats":
        player_name = st.text_input("Enter the player's name:")
        sport_for_stats = st.selectbox("Select the sport for player stats", ["Football", "Basketball", "Tennis", "Baseball"])

# User input field for prompt
user_prompt = st.chat_input("Ask me about sports, equipment, diet, or pro player stats!")

if user_prompt:
    with st.chat_message("user", avatar="🗨️"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Get a response from the LLM
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history,
    ]

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar='🤖'):
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            stream=True  # for streaming the message
        )
        response = st.write_stream(parse_groq_stream(stream))
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Dynamic Responses based on User Input
if choice == "Sport Analysis":
    if sport and equipment and diet:
        st.write(f"Based on your sport: {sport}, here are some equipment suggestions: {equipment}")
        st.write(f"Suggested Diet Plan: {diet}")
    else:
        st.write("Please provide details about your sport, equipment, and diet.")

if choice == "Pro Player Stats":
    if player_name and sport_for_stats:
        st.write(f"Fetching stats for {player_name} in {sport_for_stats}...")
        # You can call an API to fetch player stats here
    else:
        st.write("Please enter the player's name and select a sport.")


