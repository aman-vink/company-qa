# Company Agent

A powerful Streamlit-based application for crawling company websites and chatting with company data using advanced AI models. This application provides two main functionalities: crawling company websites to extract information and querying the extracted data using various LLM models.

## 🚀 Features

### Website Crawling
- **Lite Crawl**: Quick extraction of essential company information
- **Custom Prompt Crawling**: Use custom prompts to guide the crawling process
- **Domain Validation**: Automatic validation of company domain formats
- **Batch Processing**: Crawl multiple company websites simultaneously

### AI-Powered Chat Interface
- **Multi-Model Support**: Integration with GPT-4, Claude, Gemini, and other LLM models
- **Smart Retrieval**: Vector store with reranking capabilities
- **Company-Specific Chat**: Chat with data specific to each company
- **Chat History Management**: Persistent chat history with automatic cleanup

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Automatic token expiry handling and refresh
- **Input Validation**: Comprehensive validation for URLs, domains, and user inputs
- **Error Handling**: Robust error handling with user-friendly messages
- **Caching**: Smart caching to reduce API calls and improve performance

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Access to the Company Agent backend API

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd company-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   USERNAME=your_username
   PASSWORD=your_password
   BASE_URL=https://your-api-endpoint.com
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📋 Requirements

The application requires the following Python packages:

```
aiohttp>=3.11.18
streamlit>=1.24.0
openai>=0.27.0
requests>=2.28.0
python-dotenv>=1.0.0
```

## 🎯 Usage

### Getting Started

1. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

2. **Authentication**
   - Open the "User Credentials" section in the sidebar
   - Enter your username, password, and API base URL
   - Click "Authenticate" to log in

### Crawling Company Websites

1. **Navigate to "Crawl Company Website" mode**
2. **Enter Company Domains**
   - Add one domain per line (e.g., `example.com`)
   - Domains are automatically validated
3. **Choose Crawl Type**
   - **Lite Crawl**: Quick extraction of basic company information
   - **Custom Prompt**: Specify custom instructions for targeted data extraction
4. **Submit and Monitor**
   - Click "Start Crawling" to begin the process
   - Monitor the progress and view crawled domains

### Chatting with Company Data

1. **Switch to "Ask Question" mode**
2. **Select Company Domain** from the dropdown
3. **Configure AI Settings** (optional)
   - Choose LLM model (GPT-4o, Claude, Gemini, etc.)
   - Adjust temperature for response creativity
   - Set vector store parameters
4. **Start Chatting**
   - Type questions about the selected company
   - View detailed response information
   - Clear chat history when needed

## ⚙️ Configuration

### LLM Models

The application supports multiple AI models:

| Model | Provider | Best For |
|-------|----------|----------|
| GPT-4o | OpenAI | General queries, detailed analysis |
| GPT-4o mini | OpenAI | Quick responses, cost-effective |
| Claude 3.5 Sonnet | Anthropic | Complex reasoning, safety |
| Gemini 1.5 Pro | Google | Multimodal capabilities |
| Gemini 1.5 Flash | Google | Fast responses |

### Vector Store Settings

- **k**: Number of document chunks to retrieve (1-200)
- **Reranker**: Improves relevance of retrieved documents
- **Rerank Top N**: Number of documents to rerank (1-100)

### Advanced Options

- **Temperature**: Controls response creativity (0.0-1.0)
- **Recursion Limit**: Maximum recursive calls for complex queries (25-100)

## 🔧 API Endpoints

The application interacts with the following backend endpoints:

- `POST /auth/token/` - User authentication
- `POST /company_list/` - Fetch company list
- `POST /company_crawl/` - Start website crawling
- `POST /company_qa/` - Query company data

## 🛡️ Security Features

### Authentication
- JWT token-based authentication
- Automatic token expiry detection
- Secure credential storage in session state

### Input Validation
- URL format validation using regex patterns
- Domain name validation
- Query length limits (max 2000 characters)
- Model name validation

### Error Handling
- Comprehensive exception handling
- Network timeout protection
- JSON parsing error handling
- User-friendly error messages

## 🚨 Error Handling

The application includes robust error handling for:

- **Network Issues**: Timeout handling, connection errors
- **Authentication**: Token expiry, invalid credentials
- **API Errors**: Invalid responses, server errors
- **Input Validation**: Malformed URLs, invalid domains
- **Memory Management**: Chat history limits, session cleanup

## 📊 Performance Features

### Caching
- Company list caching (5-minute intervals)
- Session state optimization
- Reduced API calls through smart caching

### Memory Management
- Chat history limited to 100 messages
- Automatic cleanup of expired sessions
- Efficient state management

### Timeouts
- Authentication: 60 seconds
- Company crawling: 120 seconds
- Chat queries: 300 seconds

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check username and password
   - Verify API base URL format
   - Ensure network connectivity

2. **No Companies Available**
   - Complete authentication first
   - Use "Crawl Company Website" to add companies
   - Check API permissions

3. **Chat Not Working**
   - Verify authentication status
   - Select a valid company domain
   - Check LLM model availability

4. **Slow Response Times**
   - Reduce vector store k value
   - Lower recursion limit
   - Check network connection

### Debug Information

Enable debug mode by checking the "View Response Details" expander in chat responses to see:
- Full API responses
- Query parameters
- Timing information
- Error details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review error messages in the application
- Contact the development team

## 🔄 Version History

### v1.0.0
- Initial release with crawling and chat functionality
- Multi-model LLM support
- JWT authentication
- Vector store integration

### v1.1.0 (Current)
- Enhanced error handling and validation
- Improved session management
- Performance optimizations
- Security improvements
- Better user experience
