import streamlit as st
import requests
import json
import os
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration & Theme ---
st.set_page_config(
    page_title="DiffusionRAG Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Default the API to the environment variable ---
DEFAULT_API_URL = os.getenv("RAG_API_ENDPOINT", "")

# Use the API URL from environment internally
api_url = DEFAULT_API_URL

# --- Sidebar: Ingestion ---
with st.sidebar:
    st.header("📄 Knowledge Base")
    st.markdown("Upload a document to chat with it.")
    
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        if st.button("Ingest Document", use_container_width=True):
            with st.spinner("Uploading and indexing..."):
                try:
                    # Make the multipart form data request
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    resp = requests.post(f"{api_url}/upload", files=files, timeout=30)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        # Store document_id in session state so the chat can use it
                        st.session_state["document_id"] = data["document_id"]
                        st.success(f"Indexed successfully! (ID: {data['document_id']})")
                    else:
                        st.error(f"Upload failed: {resp.status_code} - {resp.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # Display active document
    if "document_id" in st.session_state:
        st.info(f"**Active Document UUID:**\n`{st.session_state['document_id']}`")
    else:
        st.warning("No document ingested yet.")

# --- Main App Area: Chat Interface ---
st.title("🧠 Serverless DiffusionRAG")
st.markdown("Ask questions about the uploaded document using the **Mercury 2** model.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is this document about?"):
    # Check if we have a document ready
    if "document_id" not in st.session_state:
        st.error("Please upload and ingest a document first using the sidebar.")
        st.stop()
        
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call the API for the answer
    with st.spinner("Thinking..."):
        try:
            payload = {
                "question": prompt,
                "document_id": st.session_state["document_id"]
            }
            resp = requests.post(f"{api_url}/query", json=payload, timeout=60)
            
            if resp.status_code == 200:
                answer = resp.json().get("answer", "No answer received.")
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(answer)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Query failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")
