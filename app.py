import streamlit as st
import openai
import os
import time
from datetime import datetime
import re
from dotenv import load_dotenv
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# Load environment variables from .env file
load_dotenv()

# Streamlit app configuration
st.set_page_config(page_title="Generative AI Assistant Creator", layout="wide")

# Initialize session state variables
if 'api_type' not in st.session_state:
    st.session_state.api_type = 'openai'
if 'client' not in st.session_state:
    st.session_state.client = None
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'thread' not in st.session_state:
    st.session_state.thread = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None

# Function to initialize OpenAI client
def initialize_client(api_type):
    try:
        if api_type == 'azure':
            client = openai.AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-05-01-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        else:
            client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        return client
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
        return None

def how_to_use():
    st.sidebar.header("How to Use")
    st.sidebar.markdown("""
    1. **Configure API Settings**:
       - Select API type (OpenAI or Azure)
       - Enter your API key and other required details
       - Click 'Save Configuration'

    2. **Create an Assistant**:
       - Go to 'Assistant Management'
       - Fill in the assistant details
       - Choose tools (Code Interpreter, File Search)
       - Click 'Create Assistant'

    3. **Update an Assistant**:
       - Select an existing assistant
       - Edit instructions or model as needed
       - Click 'Update Assistant'

    4. **Use Vector Store** (if needed):
       - Expand the 'Vector Store Management' section
       - Create a vector store and upload files
       - Update your assistant to use the vector store

    5. **Start Chatting**:
       - Select an assistant
       - Click 'Start New Chat'
       - Type your message and interact with the assistant

    Remember to update your assistant if you change the vector store or need to modify its behavior.
    """)
    
def format_message(message):
    if isinstance(message, dict):
        content = message.get("content", "")
        role = message.get("role", "")
    elif isinstance(message, str):
        content = message
        role = "assistant"  # Assuming it's an assistant message if it's a string
    else:
        content = str(message)
        role = "unknown"
    
    formatted_content = render_markdown(content)
    return f'<div class="message {role}">{formatted_content}</div>'

# Function to create a new assistant
def create_assistant(name, instructions, model, tools):
    try:
        assistant = st.session_state.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools
        )
        return assistant
    except Exception as e:
        st.error(f"Error creating assistant: {str(e)}")
        return None

# Update the update_assistant function to handle instructions and model updates
def update_assistant(assistant_id, instructions=None, model=None, vector_store_id=None):
    try:
        update_params = {}
        if instructions is not None:
            update_params['instructions'] = instructions
        if model is not None:
            update_params['model'] = model
        if vector_store_id:
            update_params['tool_resources'] = {"file_search": {"vector_store_ids": [vector_store_id]}}
        
        assistant = st.session_state.client.beta.assistants.update(
            assistant_id=assistant_id,
            **update_params
        )
        return assistant
    except Exception as e:
        st.error(f"Error updating assistant: {str(e)}")
        return None

# Function to list assistants
def list_assistants():
    try:
        assistants = st.session_state.client.beta.assistants.list()
        return assistants.data
    except Exception as e:
        st.error(f"Error listing assistants: {str(e)}")
        return []

# Function to create a new thread
def create_thread():
    try:
        thread = st.session_state.client.beta.threads.create()
        return thread
    except Exception as e:
        st.error(f"Error creating thread: {str(e)}")
        return None

# Function to add a message to a thread
def add_message_to_thread(thread_id, content, file_ids=None):
    try:
        message_params = {
            "thread_id": thread_id,
            "role": "user",
            "content": content
        }
        if file_ids:
            message_params["attachments"] = [{"file_id": file_id, "tools": [{"type": "file_search"}]} for file_id in file_ids]
        
        message = st.session_state.client.beta.threads.messages.create(**message_params)
        return message
    except Exception as e:
        st.error(f"Error adding message to thread: {str(e)}")
        return None

# Function to run the assistant
def run_assistant(thread_id, assistant_id):
    try:
        run = st.session_state.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            tools=[{"type": "file_search"}]
        )
        return run
    except Exception as e:
        st.error(f"Error running assistant: {str(e)}")
        return None

# Function to get the run status
def get_run_status(thread_id, run_id):
    try:
        run = st.session_state.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        return run.status
    except Exception as e:
        st.error(f"Error getting run status: {str(e)}")
        return None

# Function to get messages from a thread
def get_messages(thread_id):
    try:
        messages = st.session_state.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages.data
    except Exception as e:
        st.error(f"Error getting messages: {str(e)}")
        return []

# Function to create a vector store
def list_vector_stores():
    try:
        vector_stores = st.session_state.client.beta.vector_stores.list()
        return vector_stores.data
    except Exception as e:
        st.error(f"Error listing vector stores: {str(e)}")
        return []

def create_vector_store(name):
    try:
        vector_store = st.session_state.client.beta.vector_stores.create(name=name)
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None

def get_vector_store_details(vector_store_id):
    try:
        vector_store = st.session_state.client.beta.vector_stores.retrieve(vector_store_id)
        files = st.session_state.client.beta.vector_stores.files.list(vector_store_id)
        return vector_store, files.data
    except Exception as e:
        st.error(f"Error getting vector store details: {str(e)}")
        return None, []

# Function to upload files to a vector store

def upload_files_to_vector_store(vector_store_id, files):
    try:
        file_ids = []
        for file in files:
            uploaded_file = st.session_state.client.files.create(
                file=file,
                purpose='assistants'
            )
            file_ids.append(uploaded_file.id)
        
        file_batch = st.session_state.client.beta.vector_stores.file_batches.create_and_poll(
            vector_store_id=vector_store_id,
            file_ids=file_ids
        )
        return file_batch
    except Exception as e:
        st.error(f"Error uploading files to vector store: {str(e)}")
        return None

# Function to upload files for message attachment
def upload_files_for_message(files):
    try:
        file_ids = []
        for file in files:
            uploaded_file = st.session_state.client.files.create(
                file=file,
                purpose='assistants'
            )
            file_ids.append(uploaded_file.id)
        return file_ids
    except Exception as e:
        st.error(f"Error uploading files for message: {str(e)}")
        return None

# New functions for chat interface
def render_markdown(text):
    return markdown.markdown(text, extensions=['fenced_code', 'codehilite'])

def format_message(message):
    formatted_content = render_markdown(message["content"])
    return f'<div class="message {message["role"]}">{formatted_content}</div>'


# Main app layout
def main():
    st.title("Generative AI Assistant Creator")
    
    # Initialize session state for active assistant if not exists
    if 'active_assistant' not in st.session_state:
        st.session_state.active_assistant = None

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    api_type = st.sidebar.selectbox("API Type", ["openai", "azure"], index=0 if st.session_state.api_type == "openai" else 1)
    
    if st.sidebar.button("Initialize Client"):
        st.session_state.api_type = api_type
        st.session_state.client = initialize_client(api_type)
        if st.session_state.client:
            st.sidebar.success("Client initialized successfully!")
        else:
            st.sidebar.error("Failed to initialize client. Please check your .env file and API keys.")

    # How to Use guide in sidebar
    how_to_use()
    
    # Main content area
    if st.session_state.client:
        # Vector Store Management (in expandable section)
        with st.expander("Vector Store Management"):
            st.header("Vector Store Management")
            vector_store_name = st.text_input("Vector Store Name")
            if st.button("Create Vector Store"):
                vector_store = create_vector_store(vector_store_name)
                if vector_store:
                    st.session_state.vector_store = vector_store
                    st.success(f"Vector Store '{vector_store_name}' created successfully!")

            if st.session_state.vector_store:
                st.write(f"Current Vector Store: {st.session_state.vector_store.name}")
                uploaded_files = st.file_uploader("Upload files to Vector Store", accept_multiple_files=True)
                if uploaded_files and st.button("Upload Files"):
                    file_batch = upload_files_to_vector_store(st.session_state.vector_store.id, uploaded_files)
                    if file_batch:
                        st.success("Files uploaded successfully!")
                        st.write(f"File batch status: {file_batch.status}")
                        st.write(f"File counts: {file_batch.file_counts}")

        # Assistant management
        st.header("Assistant Management")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Create New Assistant")
            new_assistant_name = st.text_input("Assistant Name")
            new_assistant_instructions = st.text_area("Assistant Instructions")
            new_assistant_model = st.text_input("Model (Deployment Name for Azure)")
            use_code_interpreter = st.checkbox("Use Code Interpreter")
            use_file_search = st.checkbox("Use File Search")
            
            if st.button("Create Assistant"):
                tools = []
                if use_code_interpreter:
                    tools.append({"type": "code_interpreter"})
                if use_file_search:
                    tools.append({"type": "file_search"})
                
                vector_store_id = st.session_state.vector_store.id if st.session_state.vector_store else None
                new_assistant = create_assistant(new_assistant_name, new_assistant_instructions, new_assistant_model, tools, vector_store_id)
                if new_assistant:
                    st.success(f"Assistant '{new_assistant_name}' created successfully!")
                    st.write(f"Assistant tools: {new_assistant.tools}")
                    st.write(f"Assistant tool_resources: {new_assistant.tool_resources}")
                    # Set the newly created assistant as the active assistant
                    st.session_state.active_assistant = new_assistant
                    st.success(f"'{new_assistant_name}' is now the active assistant for chat.")

        with col2:
            st.subheader("Select and Update Assistant")
            assistants = list_assistants()
            assistant_names = [assistant.name for assistant in assistants]
            selected_assistant = st.selectbox("Choose an Assistant", assistant_names)
            if selected_assistant:
                selected_assistant_obj = next((a for a in assistants if a.name == selected_assistant), None)
                st.session_state.assistant = selected_assistant_obj
                st.write(f"Selected Assistant: {st.session_state.assistant.name}")
                st.write(f"Assistant tools: {st.session_state.assistant.tools}")
                st.write(f"Assistant tool_resources: {st.session_state.assistant.tool_resources}")

                # Set the selected assistant as the active assistant
                st.session_state.active_assistant = selected_assistant_obj
                st.success(f"'{selected_assistant}' is now the active assistant for chat.")

                st.subheader("Update Assistant Details")
                current_instructions = st.session_state.assistant.instructions
                new_instructions = st.text_area("Edit Instructions", value=current_instructions, height=150)
                
                current_model = st.session_state.assistant.model
                new_model = st.text_input("Edit Model (Deployment Name for Azure)", value=current_model)
                
                if st.button("Update Assistant"):
                    updated_assistant = update_assistant(
                        st.session_state.assistant.id,
                        instructions=new_instructions,
                        model=new_model,
                        vector_store_id=st.session_state.vector_store.id if st.session_state.vector_store else None
                    )
                    if updated_assistant:
                        st.session_state.assistant = updated_assistant
                        st.session_state.active_assistant = updated_assistant
                        st.success("Assistant updated successfully!")
                        st.write(f"Updated Assistant Instructions: {updated_assistant.instructions}")
                        st.write(f"Updated Assistant Model: {updated_assistant.model}")
                        st.write(f"Updated Assistant tool_resources: {updated_assistant.tool_resources}")
                        st.rerun()

        # Chat interface
        st.header("Chat Interface")
        if st.session_state.active_assistant:
            st.info(f"Active Assistant: {st.session_state.active_assistant.name}")
            
            if st.button("Start New Chat"):
                st.session_state.thread = create_thread()
                st.session_state.messages = []

            if st.session_state.thread:
                # Display chat messages
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        if message["role"] == "assistant":
                            st.markdown(format_message(message), unsafe_allow_html=True)
                        else:
                            st.write(message["content"])

                # Chat input
                user_input = st.chat_input("Type your message here...")
                if user_input:
                    # Add user message to thread and display it
                    add_message_to_thread(st.session_state.thread.id, user_input)
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    with st.chat_message("user"):
                        st.write(user_input)

                    # Run the active assistant
                    run = run_assistant(st.session_state.thread.id, st.session_state.active_assistant.id)
                    if run:
                        # Wait for the run to complete
                        status = get_run_status(st.session_state.thread.id, run.id)
                        while status not in ["completed", "failed"]:
                            time.sleep(1)
                            status = get_run_status(st.session_state.thread.id, run.id)

                        # Get the assistant's response
                        messages = get_messages(st.session_state.thread.id)
                        if messages:
                            assistant_message = messages[0].content[0].text.value
                            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                            with st.chat_message("assistant"):
                                st.markdown(format_message({"role": "assistant", "content": assistant_message}), unsafe_allow_html=True)

            else:
                st.warning("Please start a new chat to begin the conversation.")
        else:
            st.warning("Please select or create an assistant to start chatting.")
    else:
        st.warning("Please configure your API settings in the sidebar to get started.")

if __name__ == "__main__":
    main()
   
