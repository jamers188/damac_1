import os
import streamlit as st
from utils import (
    load_config, save_config, verify_password, hash_password,
    save_pdf, process_pdf, get_all_pdfs, delete_pdf
)

# Page configuration
st.set_page_config(
    page_title="PDF Chatbot Admin",
    page_icon="🔐",
    layout="wide"
)

# Initialize session state
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# Initialize OpenAI API key
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None

def login_form():
    st.title("Admin Login 🔐")
    
    with st.form("login_form"):
        password = st.text_input("Enter admin password:", type="password", 
                                help="Default password is 'admin'")
        submit = st.form_submit_button("Login")
        
        if submit:
            config = load_config()
            if verify_password(password, config["admin_password"]):
                st.session_state.admin_authenticated = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password. Please try again.")

def admin_panel():
    st.title("PDF Chatbot Admin Panel 📊")
    
    # Sidebar with API key input
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input(
            "OpenAI API Key:", 
            type="password",
            value=st.session_state.openai_api_key or "",
            help="Required for processing PDFs"
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API key set")
        else:
            st.warning("⚠️ API key required")
        
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.experimental_rerun()
    
    # Main panel with tabs
    tab1, tab2, tab3 = st.tabs(["Upload PDF", "Manage PDFs", "Change Password"])
    
    # Tab 1: Upload PDF
    with tab1:
        st.header("Upload New PDF")
        
        with st.form("upload_form"):
            pdf_name = st.text_input("PDF Name (no spaces):", 
                                   help="This will be used as identifier")
            description = st.text_area("Description:", 
                                     help="Brief description of the document")
            uploaded_file = st.file_uploader("Upload PDF:", type="pdf")
            process = st.checkbox("Process after upload", value=True, 
                                help="Create AI embeddings for the document")
            
            submit = st.form_submit_button("Upload PDF")
            
            if submit:
                if not pdf_name or not uploaded_file:
                    st.error("Please provide a name and upload a PDF file.")
                    return
                
                if not st.session_state.openai_api_key and process:
                    st.error("OpenAI API key is required to process the PDF.")
                    return
                
                # Clean name
                pdf_name = pdf_name.replace(" ", "_").lower()
                
                try:
                    # Save PDF
                    file_path = save_pdf(uploaded_file, pdf_name, description)
                    st.success(f"PDF '{pdf_name}' uploaded successfully!")
                    
                    # Process if requested
                    if process:
                        with st.spinner("Processing PDF... This may take a few minutes."):
                            if process_pdf(pdf_name):
                                st.success(f"PDF '{pdf_name}' processed successfully!")
                            else:
                                st.error("Error processing PDF. Please check the logs.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Tab 2: Manage PDFs
    with tab2:
        st.header("Manage PDFs")
        
        pdfs = get_all_pdfs()
        if not pdfs:
            st.info("No PDFs uploaded yet.")
            return
        
        for pdf_name, pdf_info in pdfs.items():
            with st.expander(f"📄 {pdf_name}"):
                st.write(f"**Description:** {pdf_info.get('description', 'No description')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Status
                    if os.path.exists(pdf_info.get("vectorstore", "")):
                        st.success("Status: Processed ✅")
                    else:
                        st.warning("Status: Not processed ⚠️")
                        if st.button(f"Process now", key=f"process_{pdf_name}"):
                            if not st.session_state.openai_api_key:
                                st.error("OpenAI API key required!")
                            else:
                                with st.spinner(f"Processing {pdf_name}..."):
                                    if process_pdf(pdf_name):
                                        st.success("Processed successfully!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("Processing failed.")
                with col2:
                    # Delete
                    if st.button(f"Delete PDF", key=f"delete_{pdf_name}"):
                        if delete_pdf(pdf_name):
                            st.success(f"PDF '{pdf_name}' deleted.")
                            st.experimental_rerun()
                        else:
                            st.error(f"Error deleting PDF.")
    
    # Tab 3: Change Password
    with tab3:
        st.header("Change Admin Password")
        
        with st.form("password_form"):
            new_password = st.text_input("New Password:", type="password")
            confirm_password = st.text_input("Confirm Password:", type="password")
            
            submit = st.form_submit_button("Change Password")
            
            if submit:
                if not new_password:
                    st.error("Please enter a password.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        config = load_config()
                        config["admin_password"] = hash_password(new_password)
                        save_config(config)
                        st.success("Password changed successfully!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def main():
    if not st.session_state.admin_authenticated:
        login_form()
    else:
        admin_panel()

if __name__ == "__main__":
    main()
