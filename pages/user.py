import os
import streamlit as st
from utils import (
    get_active_pdf, get_all_pdfs, set_active_pdf, 
    setup_conversation_chain
)

# Page configuration
st.set_page_config(
    page_title="Real Estate Property Chatbot",
    page_icon="🏢",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for conversation
if "conversation" not in st.session_state:
    st.session_state.conversation = None

# Initialize OpenAI API key
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None

def setup_sidebar():
    """Setup the sidebar with PDF selection and API key input."""
    with st.sidebar:
        st.title("Document Settings")
        
        # OpenAI API key input
        openai_api_key = st.text_input(
            "OpenAI API Key:", 
            type="password",
            help="Enter your OpenAI API key to enable the chatbot.",
            value=st.session_state.openai_api_key or ""
        )
        
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        st.divider()
        
        # Get all available PDFs
        pdfs = get_all_pdfs()
        active_pdf_name, active_pdf_info = get_active_pdf()
        
        if not pdfs:
            st.info("No documents available. Please contact the administrator.")
            return None, None
        
        # PDF selection
        selected_pdf = st.selectbox(
            "Select Document:",
            options=list(pdfs.keys()),
            index=list(pdfs.keys()).index(active_pdf_name) if active_pdf_name else 0,
            format_func=lambda x: f"{x} - {pdfs[x].get('description', 'No description')[:50]}...",
            help="Select the property document to chat with"
        )
        
        if selected_pdf != active_pdf_name:
            set_active_pdf(selected_pdf)
            st.experimental_rerun()
        
        return selected_pdf, pdfs.get(selected_pdf, {})

def initialize_chat(pdf_info):
    """Initialize the chat with the selected PDF."""
    if not pdf_info:
        return False
    
    vectorstore_path = pdf_info.get("vectorstore")
    if not vectorstore_path or not os.path.exists(vectorstore_path):
        st.sidebar.warning("This document hasn't been processed yet. Please contact the administrator.")
        return False
    
    if not st.session_state.openai_api_key:
        st.sidebar.warning("Please enter your OpenAI API key to start chatting.")
        return False
    
    # Setup conversation chain
    st.session_state.conversation = setup_conversation_chain(vectorstore_path)
    return True

def display_chat_interface():
    """Display the chat interface."""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_question = st.chat_input(
        "Ask anything about the properties...",
        disabled=not st.session_state.conversation
    )
    
    if user_question:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_question})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_question)
        
        if st.session_state.conversation:
            # Get response from chatbot
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.conversation.run(user_question)
                        st.markdown(response)
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
                        if "API key" in str(e).lower():
                            st.warning("Please check your OpenAI API key.")

def main():
    """Main application."""
    st.title("🏢 Real Estate Property Information Chatbot")
    
    # Setup sidebar and get selected PDF
    selected_pdf, pdf_info = setup_sidebar()
    
    # Introduction text
    st.markdown("""
    ### Welcome to the Property Information Assistant
    
    This chatbot can answer questions about property listings, including:
    - Location details
    - Unit types and sizes
    - Pricing and payment plans
    - Amenities and features
    - Project timelines
    
    Simply select a document from the sidebar and start asking questions!
    """)
    
    # Display property info if available
    if pdf_info and "description" in pdf_info:
        st.info(f"**Currently viewing:** {selected_pdf} - {pdf_info['description']}")
    
    st.divider()
    
    # Initialize chat if not already initialized or if PDF changed
    if selected_pdf and (not st.session_state.conversation or 
                        "current_pdf" not in st.session_state or 
                        st.session_state.current_pdf != selected_pdf):
        st.session_state.current_pdf = selected_pdf
        if not initialize_chat(pdf_info):
            st.session_state.conversation = None
    
    # Display chat interface
    display_chat_interface()
    
    # Reset chat button
    if st.session_state.messages:
        if st.button("Start New Chat", key="reset_chat"):
            st.session_state.messages = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
