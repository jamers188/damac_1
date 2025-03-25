import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Property Information Chatbot",
    page_icon="🏢",
    layout="wide"
)

# Main app
st.title("🏢 Property Information Chatbot")

st.markdown("""
## Welcome to the Property Information Chatbot

This application allows you to chat with your real estate property documents.

### Available Options:

1. **User Chat** - Ask questions about property listings, including details on locations, unit types, prices, and amenities
2. **Admin Portal** - For administrators to manage PDF documents and system settings

Select an option below to get started:
""")

# Create two columns for the buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("📱 User Chat", use_container_width=True):
        st.switch_page("pages/user.py")

with col2:
    if st.button("🔐 Admin Portal", use_container_width=True):
        st.switch_page("pages/admin.py")

# Information section
st.markdown("""
---

### About this Application

This chatbot is designed to answer questions about real estate property listings by analyzing uploaded PDF documents. It uses AI to understand your questions and provide accurate, relevant information about properties.

#### Features:

- Chat with property documents to get instant answers
- Ask about unit types, prices, payment plans, amenities, and more
- Explore multiple property listings in a conversational interface
- Get accurate information without having to manually search through documents

**Note:** Administrators can upload and manage PDF documents through the Admin Portal.
""")

# Footer
st.markdown("---")
st.caption("© 2025 Property Information Chatbot | Powered by AI")
