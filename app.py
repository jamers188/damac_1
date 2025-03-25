import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Property Information Chatbot",
    page_icon="🏢",
    layout="centered"
)

def main():
    st.title("🏢 Property Information Chatbot")
    
    st.markdown("""
    ## Welcome to the Property Information Chatbot
    
    This application lets you chat with property documents to get instant information.
    
    ### Choose an option:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 User Mode", use_container_width=True):
            import simplified_user
            streamlit_dir = os.path.dirname(st.__file__)
            import_path = os.path.join(streamlit_dir, "simplified_user.py")
            if os.path.exists("simplified_user.py"):
                st.switch_page("simplified_user.py")
            else:
                st.error("User page not found. Please ensure simplified_user.py exists.")
    
    with col2:
        if st.button("🔐 Admin Mode", use_container_width=True):
            import simplified_admin
            streamlit_dir = os.path.dirname(st.__file__)
            import_path = os.path.join(streamlit_dir, "simplified_admin.py")
            if os.path.exists("simplified_admin.py"):
                st.switch_page("simplified_admin.py")
            else:
                st.error("Admin page not found. Please ensure simplified_admin.py exists.")
    
    st.markdown("""
    ### About
    
    This chatbot is designed to help you find information about real estate properties quickly and easily:
    
    - **User Mode**: Ask questions about property listings
    - **Admin Mode**: Upload and manage property documents
    
    Get started by selecting a mode above.
    """)
    
    # Footer
    st.divider()
    st.caption("© 2025 Property Information Chatbot | Powered by AI")

if __name__ == "__main__":
    main()
