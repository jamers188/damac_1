import os
import streamlit as st
from utils import (
    load_config, verify_password, save_pdf, process_pdf, 
    get_all_pdfs, set_active_pdf, delete_pdf, change_admin_password
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

def login_form():
    """Display the admin login form."""
    st.title("Admin Login 🔐")
    
    with st.form("login_form"):
        password = st.text_input("Enter admin password:", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            config = load_config()
            if verify_password(password, config["admin_password"]):
                st.session_state.admin_authenticated = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password. Please try again.")

def admin_dashboard():
    """Display the admin dashboard."""
    st.title("PDF Chatbot Admin Dashboard 📊")
    
    # Sidebar for navigation
    with st.sidebar:
        st.title("Admin Controls")
        page = st.radio(
            "Select a page:",
            ["Upload PDF", "Manage PDFs", "Change Password", "Logout"]
        )
        
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.experimental_rerun()
    
    if page == "Upload PDF":
        upload_pdf_page()
    elif page == "Manage PDFs":
        manage_pdfs_page()
    elif page == "Change Password":
        change_password_page()

def upload_pdf_page():
    """Display the upload PDF page."""
    st.header("Upload New PDF 📄")
    
    with st.form("upload_form"):
        pdf_name = st.text_input("PDF Name (no spaces):", help="This will be used as the identifier for the PDF")
        description = st.text_area("Description:", help="Brief description of what this PDF contains")
        uploaded_file = st.file_uploader("Upload PDF file:", type="pdf")
        process = st.checkbox("Process PDF after upload", value=True, help="Create vector embeddings for chatbot functionality")
        
        submit = st.form_submit_button("Upload PDF")
        
        if submit:
            if not pdf_name or not uploaded_file:
                st.error("Please provide a name and upload a PDF file.")
                return
            
            # Sanitize PDF name
            pdf_name = pdf_name.replace(" ", "_").lower()
            
            # Save the PDF
            try:
                file_path = save_pdf(uploaded_file, pdf_name, description)
                st.success(f"PDF '{pdf_name}' uploaded successfully!")
                
                # Process the PDF if requested
                if process:
                    with st.spinner("Processing PDF... This may take a few minutes."):
                        if process_pdf(pdf_name):
                            st.success(f"PDF '{pdf_name}' processed successfully!")
                        else:
                            st.error("Error processing PDF. Please check the file format.")
            except Exception as e:
                st.error(f"Error uploading PDF: {str(e)}")

def manage_pdfs_page():
    """Display the manage PDFs page."""
    st.header("Manage PDFs 📚")
    
    pdfs = get_all_pdfs()
    
    if not pdfs:
        st.info("No PDFs uploaded yet. Go to 'Upload PDF' to add documents.")
        return
    
    # Display all PDFs in a table
    st.subheader("Available PDFs")
    
    # Create three columns
    cols = st.columns([3, 1, 1, 1])
    cols[0].write("**PDF Name**")
    cols[1].write("**Status**")
    cols[2].write("**Set Active**")
    cols[3].write("**Delete**")
    
    for pdf_name, pdf_info in pdfs.items():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        # PDF info
        with col1:
            st.write(f"**{pdf_name}**")
            st.caption(pdf_info.get("description", "No description"))
        
        # Status
        with col2:
            if os.path.exists(pdf_info.get("vectorstore", "")):
                st.success("Processed")
            else:
                st.warning("Not processed")
                if st.button(f"Process {pdf_name}", key=f"process_{pdf_name}"):
                    with st.spinner(f"Processing {pdf_name}..."):
                        if process_pdf(pdf_name):
                            st.success(f"PDF '{pdf_name}' processed successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Error processing PDF.")
        
        # Set Active
        with col3:
            if st.button("Set Active", key=f"active_{pdf_name}"):
                if set_active_pdf(pdf_name):
                    st.success(f"'{pdf_name}' set as active PDF.")
                    st.experimental_rerun()
        
        # Delete
        with col4:
            if st.button("Delete", key=f"delete_{pdf_name}"):
                if delete_pdf(pdf_name):
                    st.success(f"PDF '{pdf_name}' deleted successfully.")
                    st.experimental_rerun()
                else:
                    st.error(f"Error deleting PDF '{pdf_name}'.")

def change_password_page():
    """Display the change password page."""
    st.header("Change Admin Password 🔑")
    
    with st.form("change_password_form"):
        new_password = st.text_input("New Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")
        
        submit = st.form_submit_button("Change Password")
        
        if submit:
            if not new_password:
                st.error("Please enter a password.")
                return
            
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            try:
                change_admin_password(new_password)
                st.success("Password changed successfully!")
            except Exception as e:
                st.error(f"Error changing password: {str(e)}")

# Main app logic
def main():
    if not st.session_state.admin_authenticated:
        login_form()
    else:
        admin_dashboard()

if __name__ == "__main__":
    main()
