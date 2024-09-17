# Generative AI Assistant Creator

This project is a Streamlit-based application that allows you to create and manage generative AI assistants using OpenAI or Azure OpenAI APIs. The app also provides a chat interface for interacting with your AI assistant, and it integrates features like vector stores and file uploads for enhanced AI responses.

## Features

- **Initialize OpenAI Client**: Connect to OpenAI or Azure OpenAI using your API keys.
- **Create and Manage Assistants**: Build custom assistants with specific instructions and models, including optional tools like code interpreters or file search.
- **Chat Interface**: Start a conversation with your AI assistant, attach files, and view responses in real-time.
- **Vector Store Management**: Associate vector stores with your assistants and upload files to enhance their capabilities.
- **Upload and Manage Files**: Upload files for assistant processing, either for direct message attachments or for vector store indexing.

## Installation

### Prerequisites

- Python 3.10 or higher
- [Streamlit](https://streamlit.io/)
- [OpenAI Python SDK](https://beta.openai.com/docs/libraries-and-tools) or [Azure OpenAI](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- `python-dotenv` for environment variables management

### Clone the repository

```bash
git clone https://github.com/otey247/genai-assistant-creator.git
cd generative-ai-assistant-creator
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root of the project with the following contents:

```
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
```

### Run the Application

After setting up your environment, run the Streamlit app with:

```bash
streamlit run app.py
```

## Usage

1. **Initialize Client**: Choose the API type (OpenAI or Azure) and initialize the client using your API keys.
2. **Create Assistant**: Provide a name, model, and instructions for your AI assistant. Optionally, enable tools like the code interpreter or file search.
3. **Manage Assistants**: Update instructions, models, or vector stores associated with your assistants.
4. **Vector Stores**: Create and manage vector stores, and upload files for improved AI responses.
5. **Chat Interface**: Start a chat session with your assistant and interact using natural language. Attach files if needed for more contextual responses.

## Screenshots



## Future Improvements

- Expand assistant customization options.
- Add more tools for enhancing AI capabilities.
- Improve UI/UX for managing assistants and vector stores.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.