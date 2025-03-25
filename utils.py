import os
import json
import hashlib
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI

# File paths
DATA_DIR = "data"
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
VECTOR_DIR = os.path.join(DATA_DIR, "vectorstores")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# Create necessary directories
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def hash_password(password):
    """Create a SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_hash):
    """Verify if the input password matches the stored hash."""
    input_hash = hash_password(input_password)
    return input_hash == stored_hash

def load_config():
    """Load the configuration file."""
    if not os.path.exists(CONFIG_FILE):
        # Create default config
        config = {
            "admin_password": hash_password("admin"),  # Default password: "admin"
            "pdfs": {},
            "active_pdf": None
        }
        save_config(config)
        return config
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    """Save the configuration file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def save_pdf(uploaded_file, pdf_name, description):
    """Save an uploaded PDF file."""
    # Create file path
    file_path = os.path.join(PDF_DIR, f"{pdf_name}.pdf")
    
    # Save the file
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    # Update config
    config = load_config()
    config["pdfs"][pdf_name] = {
        "path": file_path,
        "description": description,
        "vectorstore": os.path.join(VECTOR_DIR, pdf_name)
    }
    config["active_pdf"] = pdf_name
    save_config(config)
    
    return file_path

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    pdf_reader = PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def create_vectorstore(text, pdf_name):
    """Create a vector store from text."""
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    if not chunks:
        st.error("Could not extract text from PDF. Please check if the PDF contains selectable text.")
        return None
    
    # Create embeddings and store in vector database
    embeddings = OpenAIEmbeddings()
    vectorstore_path = os.path.join(VECTOR_DIR, pdf_name)
    
    # Create and persist the vectorstore
    vectorstore = Chroma.from_texts(
        chunks, 
        embeddings, 
        persist_directory=vectorstore_path
    )
    vectorstore.persist()
    
    return vectorstore_path

def setup_conversation_chain(vectorstore_path):
    """Set up the conversation chain for a PDF."""
    # Load the vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embeddings)
    
    # Create language model
    llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")
    
    # Create memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create conversation chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        verbose=True
    )
    
    return conversation_chain

def process_pdf(pdf_name):
    """Process a PDF file and create a vector store."""
    config = load_config()
    pdf_info = config["pdfs"].get(pdf_name)
    
    if not pdf_info:
        st.error(f"PDF '{pdf_name}' not found in configuration.")
        return False
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_info["path"])
    
    # Create vector store
    vectorstore_path = create_vectorstore(pdf_text, pdf_name)
    
    if not vectorstore_path:
        return False
    
    # Update config with vectorstore path
    config["pdfs"][pdf_name]["vectorstore"] = vectorstore_path
    save_config(config)
    
    return True

def get_all_pdfs():
    """Get all available PDFs."""
    config = load_config()
    return config["pdfs"]

def get_active_pdf():
    """Get the currently active PDF."""
    config = load_config()
    active_pdf = config.get("active_pdf")
    if active_pdf and active_pdf in config["pdfs"]:
        return active_pdf, config["pdfs"][active_pdf]
    return None, None

def set_active_pdf(pdf_name):
    """Set the active PDF."""
    config = load_config()
    if pdf_name in config["pdfs"]:
        config["active_pdf"] = pdf_name
        save_config(config)
        return True
    return False

def delete_pdf(pdf_name):
    """Delete a PDF and its vector store."""
    config = load_config()
    if pdf_name not in config["pdfs"]:
        return False
    
    # Delete PDF file
    pdf_path = config["pdfs"][pdf_name]["path"]
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    
    # Delete vector store
    vectorstore_path = config["pdfs"][pdf_name]["vectorstore"]
    if os.path.exists(vectorstore_path):
        import shutil
        shutil.rmtree(vectorstore_path)
    
    # Update config
    del config["pdfs"][pdf_name]
    if config["active_pdf"] == pdf_name:
        if config["pdfs"]:
            config["active_pdf"] = list(config["pdfs"].keys())[0]
        else:
            config["active_pdf"] = None
    
    save_config(config)
    return True

def change_admin_password(new_password):
    """Change the admin password."""
    config = load_config()
    config["admin_password"] = hash_password(new_password)
    save_config(config)
