import os
import time
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
    st.header("🏅 Sports Assistant Options")
    st.divider()
    
    # Use session state to manage the selected choice
    if "selected_choice" not in st.session_state:
        st.session_state.selected_choice = "Sport Analysis"
    
    # Radio buttons to choose between sports analysis or pro player stats
    choice = st.radio(
        "What would you like to know?",
        ["Sport Analysis", "Pro Player Stats"],
        index=0 if st.session_state.selected_choice == "Sport Analysis" else 1,
        key="choice_radio",
        help="Choose between analyzing your sport or fetching pro player stats."
    )
    
    # Update session state when the choice changes
    if choice != st.session_state.selected_choice:
        st.session_state.selected_choice = choice
        st.rerun()  # Rerun the app to reflect the new choice
    
    st.divider()
    
    if st.session_state.selected_choice == "Sport Analysis":
        st.subheader("Sport Analysis 🏀")
        
        # Use session state to manage sport selection
        if "selected_sport" not in st.session_state:
            st.session_state.selected_sport = "Football"
        
        # Sport selection
        sport = st.selectbox(
            "Select your sport",
            ["Football", "Basketball", "Tennis", "Baseball", "Other"],
            index=["Football", "Basketball", "Tennis", "Baseball", "Other"].index(st.session_state.selected_sport),
            key="sport_selectbox",
            help="Select the sport you want to analyze."
        )
        
        # Update session state when the sport changes
        if sport != st.session_state.selected_sport:
            st.session_state.selected_sport = sport
        
        # Equipment input
        equipment = st.text_input(
            "What equipment do you need?",
            placeholder="e.g., shoes, racket, gloves",
            key="equipment_input",
            help="Enter the equipment you need for your sport."
        )
        
        # Diet input
        diet = st.text_area(
            "What is your current diet or dietary requirements?",
            placeholder="e.g., high protein, low carb",
            key="diet_input",
            help="Describe your diet or any specific dietary requirements."
        )
        
        # Add a button to submit sport analysis details
        if st.button("Get Sport Analysis"):
            if sport and equipment and diet:
                st.session_state.sport_analysis = {
                    "sport": sport,
                    "equipment": equipment,
                    "diet": diet
                }
                st.success("Details submitted! Ask me about your sport analysis.")
            else:
                st.warning("Please fill in all the details.")
    
    if st.session_state.selected_choice == "Pro Player Stats":
        st.subheader("Pro Player Stats 🏆")
        
        # Player name input
        player_name = st.text_input(
            "Enter the player's name:",
            placeholder="e.g., Lionel Messi",
            key="player_name_input",
            help="Enter the name of the player you want to analyze."
        )
        
        # Use session state to manage sport selection for stats
        if "selected_sport_stats" not in st.session_state:
            st.session_state.selected_sport_stats = "Football"
        
        # Sport selection for player stats
        sport_for_stats = st.selectbox(
            "Select the sport for player stats",
            ["Football", "Basketball", "Tennis", "Baseball"],
            index=["Football", "Basketball", "Tennis", "Baseball"].index(st.session_state.selected_sport_stats),
            key="sport_stats_selectbox",
            help="Select the sport to fetch player stats."
        )
        
        # Update session state when the sport for stats changes
        if sport_for_stats != st.session_state.selected_sport_stats:
            st.session_state.selected_sport_stats = sport_for_stats
        
        # Add a button to fetch player stats
        if st.button("Fetch Player Stats"):
            if player_name and sport_for_stats:
                with st.spinner(f"Fetching stats for {player_name} in {sport_for_stats}..."):
                    time.sleep(2)  # Simulate API call delay
                    # Placeholder for stats
                    st.session_state.player_stats = f"Stats for {player_name} in {sport_for_stats} will be displayed here."
                    st.success("Stats fetched! Ask me about the player stats.")
            else:
                st.warning("Please enter the player's name and select a sport.")
    
    st.divider()
    
    # Add a reset button to clear session state
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# User input field for prompt
user_prompt = st.chat_input("Ask me about sports, equipment, diet, or pro player stats!")

# Show spinner while fetching
if user_prompt:
    with st.spinner("Fetching your results..."):
        time.sleep(1)  # Simulate delay for demonstration
    
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
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                stream=True  # for streaming the message
            )
            response = st.write_stream(parse_groq_stream(stream))
        except Exception as e:
            st.error(f"An error occurred: {e}")
            response = "Sorry, I couldn't process your request. Please try again."
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# Dynamic Responses based on User Input
if st.session_state.selected_choice == "Sport Analysis":
    if sport and equipment and diet:
        st.write(f"Based on your sport: {sport}, here are some equipment suggestions: {equipment}")
        st.write(f"Suggested Diet Plan: {diet}")
    else:
        st.write("Please provide details about your sport, equipment, and diet.")

if st.session_state.selected_choice == "Pro Player Stats":
    if player_name and sport_for_stats:
        with st.spinner("Fetching player stats..."):
            time.sleep(1)  # Simulate delay for demonstration
            st.write(f"Fetching stats for {player_name} in {sport_for_stats}...")
            # Display the fetched stats (replace with actual logic)
            if "player_stats" in st.session_state:
                st.write(st.session_state.player_stats)
    else:
        st.write("Please enter the player's name and select a sport.")

