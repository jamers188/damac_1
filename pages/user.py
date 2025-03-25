import os
import streamlit as st
from utils import (
    get_all_pdfs, setup_conversation_chain
)

# Page configuration
st.set_page_config(
    page_title="Property PDF Chatbot",
    page_icon="🏢",
    layout="wide"
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation" not in st.session_state:
    st.session_state.conversation = None
    
if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None

def main():
    st.title("🏢 Property Information Chatbot")
    
    # Sidebar setup
    with st.sidebar:
        st.title("Settings")
        
        # API key input
        api_key = st.text_input(
            "OpenAI API Key:", 
            type="password",
            value=st.session_state.openai_api_key or "",
            help="Required for chat functionality"
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API key set")
        else:
            st.warning("⚠️ API key required")
        
        st.divider()
        
        # Get available PDFs
        pdfs = get_all_pdfs()
        
        if not pdfs:
            st.info("No documents available. Please ask an administrator to upload documents.")
            return
        
        # PDF selection
        pdf_names = list(pdfs.keys())
        selected_pdf = st.selectbox(
            "Select document:",
            options=pdf_names,
            index=0 if st.session_state.current_pdf not in pdf_names else pdf_names.index(st.session_state.current_pdf),
            format_func=lambda x: f"{x} - {pdfs[x].get('description', '')[:30]}..."
        )
        
        # PDF info
        if selected_pdf:
            pdf_info = pdfs[selected_pdf]
            
            # Show if processed
            if os.path.exists(pdf_info.get("vectorstore", "")):
                st.success("Document ready ✅")
            else:
                st.error("Document not processed ❌")
                st.info("Please ask an administrator to process this document.")
                return
            
            # Initialize conversation if needed
            if (st.session_state.current_pdf != selected_pdf or 
                not st.session_state.conversation):
                
                if not st.session_state.openai_api_key:
                    st.warning("Please enter your OpenAI API key to chat.")
                else:
                    with st.spinner("Loading document..."):
                        conversation = setup_conversation_chain(pdf_info["vectorstore"])
                        if conversation:
                            st.session_state.conversation = conversation
                            st.session_state.current_pdf = selected_pdf
                            st.session_state.messages = []
                            st.success("Ready to chat!")
                        else:
                            st.error("Error loading document.")
    
    # Display intro text
    st.markdown("""
    ### Welcome to the Property Information Assistant
    
    This chatbot can answer questions about property listings in the selected document, including:
    - Location details and unit types
    - Pricing and payment plans
    - Amenities and features
    - And more...
    
    Select a document from the sidebar and start asking questions!
    """)
    
    # Display property info
    if st.session_state.current_pdf:
        pdf_info = pdfs[st.session_state.current_pdf]
        st.info(f"**Currently viewing:** {st.session_state.current_pdf} - {pdf_info.get('description', '')}")
    
    st.divider()
    
    # Display chat interface
    if not st.session_state.conversation:
        st.warning("Please select a document and provide an OpenAI API key to start chatting.")
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        user_question = st.chat_input("Ask about the properties...")
        
        if user_question:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_question})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_question)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.conversation.run(user_question)
                        st.markdown(response)
                        
                        # Add assistant message to history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        if "api key" in str(e).lower():
                            st.warning("Please check your OpenAI API key.")
        
        # Reset chat button
        if st.session_state.messages and st.button("Start New Chat"):
            st.session_state.messages = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
