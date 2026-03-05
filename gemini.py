import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="LuminaChat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    h1 {
        color: #1f77b4;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Check if API key is provided
if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found! Please set it in your environment variables.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel("gemini-pro")

# Sidebar configuration
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Select model
    model_option = st.selectbox(
        "Select Model:",
        ["gemini-3-flash-preview","gemini-3.1-pro-preview","gemini-3-flash-preview","gemini-2.5-pro","gemini-2.5-flash"],
        help="Choose the Gemini model to use"
    )
    
    # Update model if changed
    if model_option:
        st.session_state.model = genai.GenerativeModel(model_option)
    

    
    system_prompt = "You are a helpful, friendly, and knowledgeable AI assistant. Provide clear, concise, and accurate responses to user queries."

    # Temperature control
    temperature = st.slider(
        "Creativity Level:",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )
    
    # Clear conversation button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()
    
    st.divider()
    
    # About section
    with st.expander("ℹ️ About LuminaChat", expanded=False):
        st.markdown("""
        ### 🤖 LuminaChat - AI Powered Conversations
        
        **Welcome to LuminaChat**, your intelligent conversational assistant powered by Google's advanced Gemini API.
        
        #### Features
        - 💬 **Real-time Chat** - Instant responses to your queries
        - 🧠 **Advanced AI Models** - Access to latest Gemini models
        - 🎯 **Customizable Behavior** - Adjust creativity level for different responses
        - 💾 **Chat History** - Full conversation context
        - 🚀 **Fast & Reliable** - Powered by Google's infrastructure
        
        #### How to Use
        1. Select your preferred AI model from the dropdown
        2. Adjust creativity level with the slider
        3. Type your message and press Enter
        4. Get instant AI-powered responses
        5. Clear history anytime with one click
        
        #### Available Models
        - **Gemini 3-Flash Preview** - Fast and efficient
        - **Gemini 3.1-Pro Preview** - Most capable
        - **Gemini 2.5-Pro** - Balanced performance
        - **Gemini 2.5-Flash** - Ultra-fast responses
        
        #### Settings Explained
        **Creativity Level**: Controls response variability
        - 0.0 = Very focused and deterministic
        - 0.7 = Balanced (recommended)
        - 2.0 = Very creative and random
        
        #### Tips & Tricks
        • Be specific in your prompts for better results
        • Use clear language and proper grammar
        • Ask follow-up questions for more details
        • Clear history to start fresh conversations
        
        #### About
        - **App**: LuminaChat v1.0
        - **Platform**: Streamlit
        - **AI Engine**: Google Gemini API
        - **Developer**: Hardik
        - **Year**: 2026
        
        ---
        **Enjoy your conversations with LuminaChat!** 🌟
        """)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 11px; padding: 10px;">
    Developed by [Hardik] | © 2026 All rights reserved.
    </div>
    """, unsafe_allow_html=True)


# Main title
st.title("LuminaChat")


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Type your message here...", key="chat_input"):
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Prepare messages for API
            conversation = []
            for msg in st.session_state.messages[:-1]:  # Exclude current user message
                role = "model" if msg["role"] == "assistant" else "user"
                conversation.append({
                    "role": role,
                    "parts": [msg["content"]]
                })
            
            # Create chat session
            chat_session = st.session_state.model.start_chat(history=conversation)
            
            # Send message with system prompt
            full_prompt = f"{system_prompt}\n\nUser: {user_input}"
            response = chat_session.send_message(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            
            # Get response text
            assistant_response = response.text
            message_placeholder.markdown(assistant_response)
            
            # Add assistant message to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response
            })
            
       
        except Exception as e:
            error_message = f"❌ Error: {str(e)}"
            message_placeholder.error(error_message)
            # Remove the failed user message
            st.session_state.messages.pop()
