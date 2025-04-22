# Company Domain Chat Interface

A Streamlit application that allows users to chat with company-specific knowledge by selecting a company domain (e.g., microsoft.com, amazon.com). The application integrates with external APIs to fetch a list of company domains and company-specific knowledge.

## Features

- Connect to external APIs for company domains (e.g., microsoft.com) and knowledge retrieval
- Ask questions about specific companies and get company-specific answers
- Customize JSON output format based on user preferences
- Download chat history as JSON
- Basic and advanced versions available

## API Integration

The application integrates with two external APIs:

1. **Company Domains API**: Provides a list of available company domains
   - Expected response format: JSON array of company domain objects with `domain`, `name`, and optionally other fields
   - Example: `[{"domain": "microsoft.com", "name": "Microsoft", "industry": "Technology"}]`

2. **Company Knowledge API**: Provides company-specific knowledge for answering questions
   - Endpoint format: `{KNOWLEDGE_API_URL}/{company_domain}`
   - Expected response format: JSON array of knowledge strings
   - Example: `["Microsoft was founded in 1975 by Bill Gates and Paul Allen.", "Microsoft's headquarters are in Redmond, Washington."]`

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory using the `.env.example` template
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`
   - Add your Company Domains API URL: `DOMAIN_API_URL=https://your-api.com/company-domains`
   - Add your Company Knowledge API URL: `KNOWLEDGE_API_URL=https://your-api.com/company-knowledge`
   - Alternatively, you can enter these URLs directly in the app's sidebar

## Running the App

### Basic Version
```bash
streamlit run app.py
```

### Advanced Version
```bash
streamlit run advanced_app.py
```

## Basic vs Advanced App

The repository includes two app versions:

### Basic App (`app.py`)
- Simple integration with Company Domains API
- Uses OpenAI API directly for responses
- Basic JSON output customization

### Advanced App (`advanced_app.py`)
- Integration with both Company Domains API and Company Knowledge API
- Enhanced JSON output customization
- Advanced LLM options (model selection, temperature)
- More robust handling of API errors and fallbacks

## Usage

1. Enter the URLs for your Company Domains API and Company Knowledge API (advanced version only)
2. Select a company domain from the dropdown (e.g., microsoft.com)
3. Customize your JSON output by selecting which fields to include
4. Type your question about the selected company in the chat input
5. View the response and the corresponding JSON output
6. Download your chat history as a JSON file using the button in the sidebar

## Fallback Behavior

If the external APIs are unavailable, the application will:
1. Display an error message in the sidebar
2. Fall back to using demo data with well-known company domains
3. Continue functioning with limited capabilities

## Extending the App

To extend this application for production use:

1. Implement authentication for the APIs
2. Add rate limiting and caching for API requests
3. Implement a vector database for more efficient knowledge retrieval
4. Add web scraping capabilities to gather real-time information from company websites
5. Implement proper prompt engineering and system messages

## Architecture

This application follows a architecture similar to what's described in [Basic Architecture of a Domain Specific Custom AI Chatbot](https://focused.io/lab/basic-architecture-of-a-domain-specific-custom-ai-chatbot):

1. **Retrieving external data**: The application connects to:
   - Company Domains API for fetching available company domains
   - Company Knowledge API for retrieving company-specific information

2. **Querying custom data**: When a user asks a question:
   - The query is processed
   - Relevant knowledge is retrieved from the Company Knowledge API
   - The LLM generates a response using the retrieved knowledge
   - The response is formatted according to user preferences

## License

[MIT License](LICENSE) 