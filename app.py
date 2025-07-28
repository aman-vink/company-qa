"""
This is the main file for the Company Agent application.
It handles the authentication, company list fetching, and the main interface for the user.
"""

import os
import asyncio
import json
import re
from datetime import datetime, timedelta
import requests
import streamlit as st
from dotenv import load_dotenv
import aiohttp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="Company Agent", layout="wide")

# Initialize session state for app mode if not already initialized
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Ask Question"  # Default mode

# Initialize session state for authentication and credentials
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.token_expiry = None
    st.session_state.username = os.getenv("USERNAME", "")
    st.session_state.password = os.getenv("PASSWORD", "")
    st.session_state.base_url = os.getenv("BASE_URL", "https://example.com")
    st.session_state.companies = []  # To store company list
    st.session_state.companies_last_fetched = None
    st.session_state.auth_in_progress = False

# Create sidebar for customization
st.sidebar.header("Configuration")


def validate_url(url):
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_domain(domain):
    """Validate domain format"""
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    return domain_pattern.match(domain) is not None


def is_token_expired():
    """Check if authentication token is expired"""
    if not st.session_state.token_expiry:
        return True
    return datetime.now() >= st.session_state.token_expiry


def clear_auth_state():
    """Clear authentication state"""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.token_expiry = None
    st.session_state.companies = []
    st.session_state.companies_last_fetched = None


# Authentication function
def authenticate():
    """
    Authenticate the user with the given credentials and return the access token
    """
    if st.session_state.auth_in_progress:
        st.sidebar.warning("Authentication in progress...")
        return False
        
    st.session_state.auth_in_progress = True
    
    try:
        # Validate inputs
        if not st.session_state.username or not st.session_state.password:
            st.sidebar.error("Username and password are required")
            return False
            
        if not validate_url(st.session_state.base_url):
            st.sidebar.error("Invalid base URL format")
            return False

        auth_url = f"{st.session_state.base_url}/auth/token/"

        payload = json.dumps(
            {
                "username": st.session_state.username,
                "password": st.session_state.password,
            }
        )

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(auth_url, headers=headers, data=payload, timeout=60)
            if response.status_code == 200:
                try:
                    token_dict = response.json()
                except json.JSONDecodeError:
                    st.sidebar.error("Invalid response format from server")
                    return False
                    
                access_token = token_dict.get("access")
                if not access_token:
                    st.sidebar.error("No access token received")
                    return False
                    
                st.session_state.access_token = access_token
                st.session_state.authenticated = True
                # Set token expiry (assuming 1 hour, adjust as needed)
                st.session_state.token_expiry = datetime.now() + timedelta(hours=1)
                
                # Fetch company list after authentication
                fetch_companies()
                return True
            else:
                st.sidebar.error(
                    f"Authentication failed: {response.status_code} - {response.text[:200]}"
                )
                clear_auth_state()
                return False
        except requests.exceptions.Timeout:
            st.sidebar.error("Authentication request timed out")
            clear_auth_state()
            return False
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Authentication error: {str(e)[:200]}")
            clear_auth_state()
            return False
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        st.sidebar.error(f"Authentication error: {str(e)[:200]}")
        clear_auth_state()
        return False
    finally:
        st.session_state.auth_in_progress = False


# Function to fetch company list
def fetch_companies():
    """Fetch company list with proper error handling and caching"""
    if not st.session_state.authenticated or is_token_expired():
        clear_auth_state()
        return

    # Check if we fetched companies recently (cache for 5 minutes)
    if (st.session_state.companies_last_fetched and 
        datetime.now() - st.session_state.companies_last_fetched < timedelta(minutes=5)):
        return

    try:
        company_url = f"{st.session_state.base_url}/company_list/"
        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(company_url, headers=headers, timeout=60)

        if response.status_code == 200:
            try:
                data = response.json()
            except json.JSONDecodeError:
                st.error("Invalid response format from server")
                return
                
            companies = data.get("companies", [])
            if isinstance(companies, list):
                st.session_state.companies = companies
                st.session_state.companies_last_fetched = datetime.now()
            else:
                st.error("Invalid company data format received")
        elif response.status_code == 401:
            # Token expired
            clear_auth_state()
            st.error("Session expired. Please authenticate again.")
        else:
            st.error(
                f"Failed to fetch companies: {response.status_code} - {response.text[:200]}"
            )
    except requests.exceptions.Timeout:
        st.error("Request timed out while fetching companies")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching companies: {str(e)[:200]}")
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        st.error(f"Error fetching companies: {str(e)[:200]}")


# Check token expiry on app load
if st.session_state.authenticated and is_token_expired():
    clear_auth_state()
    st.warning("Session expired. Please authenticate again.")

# Make user credentials collapsible
with st.sidebar.expander(
    f"User Credentials (is authenticated: {st.session_state.authenticated})",
    expanded=False,
):
    # Use key parameter to store values in session state
    username = st.text_input(
        "Username", value=st.session_state.username, key="username"
    )
    password = st.text_input(
        "Password", value=st.session_state.password, type="password", key="password"
    )
    base_url = st.text_input(
        "Base URL", value=st.session_state.base_url, key="base_url"
    )

    # Authentication button
    if st.button("Authenticate"):
        authenticate()

# Show authentication status
if st.session_state.authenticated and not is_token_expired():
    st.success("✅ Authenticated")
else:
    st.warning("⚠️ Not authenticated")

# App mode selection (add radio buttons)
st.sidebar.header("App Mode")
app_mode = st.sidebar.radio(
    "Select Mode",
    ["Crawl Company Website", "Ask Question"],
    index=0 if st.session_state.app_mode == "Crawl Company Website" else 1,
)

# Check if mode has changed to Ask Question from Crawl Company Website
if (
    app_mode != st.session_state.app_mode
    and app_mode == "Ask Question"
    and st.session_state.authenticated
    and not is_token_expired()
):
    # Refresh company list when switching to Ask Question mode
    fetch_companies()

# Update session state with selected mode
st.session_state.app_mode = app_mode

# Advanced options for LLM and Vector Store configuration
st.sidebar.subheader("Advanced Options")

# LLM Models
llm_models = {
    "GPT-4o": "gpt-4o",
    "GPT-4o mini": "gpt-4o-mini",
    "GPT-o3 mini": "o3-mini",
    "Gemini 1.5 Pro": "gemini-1.5-pro",
    "Gemini 1.5 Flash": "gemini-1.5-flash",
    "Gemini 2 Flash Exp": "gemini-2.0-flash-exp",
    "Claude 3.5 Sonnet": "claude-3-5-sonnet-latest",
    "Claude 3.5 Haiku": "claude-3-5-haiku-latest",
    "Gemini 2 Flash": "gemini-2.0-flash",
    "Claude 3.7 Sonnet": "claude-3-7-sonnet-latest",
    "Gemini 2.5 Pro Preview": "gemini-2.5-pro-preview-03-25",
    "GPT-4.1": "gpt-4.1",
    "GPT-4.1 Mini": "gpt-4.1-mini",
    "GPT-4.1 Nano": "gpt-4.1-nano",
}

# LLM Configuration
with st.sidebar.expander("LLM Configuration", expanded=False):
    model_choice = st.selectbox(
        "LLM Model",
        options=list(llm_models.keys()),
        index=8,  # Default to Gemini 1.5 Flash
        key="llm_model_select",
    )
    selected_model = llm_models[model_choice]

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
        key="temperature_slider",
    )

# Vector Store Configuration
with st.sidebar.expander("Vector Store Configuration", expanded=False):
    k_value = st.number_input(
        "Number of Chunks (k)", min_value=1, max_value=200, value=30, key="k_value"
    )

    use_reranker = st.checkbox("Use Reranker", value=True, key="use_reranker")

    rerank_top_n = st.number_input(
        "Rerank Top N",
        min_value=1,
        max_value=100,
        value=10,
        disabled=not use_reranker,
        key="rerank_top_n",
    )

with st.sidebar.expander("Recursion Limit", expanded=False):
    recursion_limit = st.number_input(
        "Recursion Limit",
        min_value=25,
        max_value=100,
        value=25,
        help="Maximum number of recursive calls for complex queries",
        key="recursion_limit",
    )

# Main app content based on selected mode
if app_mode == "Crawl Company Website":
    st.title("Company Website Crawler")
    st.markdown("Add company domains to crawl and extract information")

    # Company information input form
    with st.form("company_form", clear_on_submit=False):
        company_domains = st.text_area(
            "Company Domains (one per line, e.g., example.com)"
        )

        # Add crawl type selection
        crawl_type = st.radio(
            "Crawl Type", ["Lite Crawl", "Custom Prompt"], index=0, key="crawl_type"
        )

        # Show custom prompt text box if Custom Prompt is selected
        custom_prompt = None
        if crawl_type == "Custom Prompt":
            custom_prompt = st.text_area(
                "Custom Crawling Prompt",
                placeholder="Enter your custom crawling prompt here...",
                help="Specify a custom prompt to guide the crawling process",
            )

        # Submit button
        submit_button = st.form_submit_button("Start Crawling")

        if submit_button:
            if not st.session_state.authenticated or is_token_expired():
                st.error("Please authenticate first!")
            elif not company_domains:
                st.error("Please enter at least one company domain")
            elif crawl_type == "Custom Prompt" and not custom_prompt:
                st.error("Please enter a custom prompt")
            else:
                # Parse domains (one per line)
                domains_list = [
                    domain.strip()
                    for domain in company_domains.split("\n")
                    if domain.strip()
                ]

                # Validate domains
                invalid_domains = [d for d in domains_list if not validate_domain(d)]
                if invalid_domains:
                    st.error(f"Invalid domain format: {', '.join(invalid_domains)}")
                elif domains_list:
                    # Call the API endpoint to start crawling
                    try:
                        crawl_url = f"{st.session_state.base_url}/company_crawl/"
                        headers = {
                            "Authorization": f"Bearer {st.session_state.access_token}",
                            "Content-Type": "application/json",
                        }

                        # Prepare payload based on crawl type
                        payload = {
                            "company_domains": domains_list,
                            "lite_crawl": crawl_type == "Lite Crawl",
                        }

                        # Add custom prompt if provided
                        if crawl_type == "Custom Prompt" and custom_prompt:
                            payload["prompt"] = custom_prompt

                        payload_json = json.dumps(payload)

                        with st.spinner("Submitting crawl request..."):
                            response = requests.post(
                                crawl_url,
                                headers=headers,
                                data=payload_json,
                                timeout=120,  # Increased timeout for crawl requests
                            )

                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                except json.JSONDecodeError:
                                    st.error("Invalid response format from server")
                                else:
                                    st.success("Crawling request submitted successfully!")
                                    st.info(
                                        data.get(
                                            "message",
                                            "You will be notified when crawling is complete.",
                                        )
                                    )

                                    # Display the list of domains being crawled
                                    st.subheader("Domains being crawled:")
                                    for domain in domains_list:
                                        st.write(f"- {domain}")
                            elif response.status_code == 401:
                                clear_auth_state()
                                st.error("Session expired. Please authenticate again.")
                            else:
                                st.error(
                                    f"Failed to submit crawl request: {response.status_code} - {response.text[:200]}"
                                )
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error submitting crawl request: {str(e)[:200]}")
                    except Exception as e:
                        logger.error(f"Error submitting crawl request: {str(e)}")
                        st.error(f"Error submitting crawl request: {str(e)[:200]}")
                else:
                    st.error("No valid domains found")

    # Display list of companies separately from the form
    if st.session_state.authenticated and not is_token_expired() and st.session_state.companies:
        st.subheader("Companies in Database")
        company_data = [
            {
                "Name": company.get("company_name", "N/A"),
                "Domain": company.get("company_domain", "N/A"),
            }
            for company in st.session_state.companies
        ]
        st.table(company_data)

elif app_mode == "Ask Question":  # Ask Question mode
    st.title("Company Domain Chat Interface")
    st.markdown("Chat with your company data")

    if not st.session_state.authenticated or is_token_expired():
        st.warning("Please authenticate first to use the chat feature")
    else:
        # Ensure companies are fetched when switching to this tab
        if not st.session_state.companies:
            fetch_companies()

        # Company domain selection
        if st.session_state.companies:
            domain_options = [
                company.get("company_domain", "")
                for company in st.session_state.companies
                if company.get("company_domain")
            ]

            if domain_options:
                selected_domain = st.selectbox(
                    "Select Company Domain", domain_options, key="domain_select_qa"
                )

                # Find company name for the selected domain
                selected_company = next(
                    (
                        company
                        for company in st.session_state.companies
                        if company.get("company_domain") == selected_domain
                    ),
                    {"company_name": "Unknown"},
                )

                company_name = selected_company.get(
                    "company_name", selected_domain.split(".")[0].capitalize()
                )

                st.subheader(f"Chat with {company_name} assistant")

                # Initialize chat history in session state if not already present
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # Limit chat history to prevent memory issues
                MAX_MESSAGES = 100
                if len(st.session_state.messages) > MAX_MESSAGES:
                    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
                    st.info(f"Chat history limited to last {MAX_MESSAGES} messages for performance")

                # Display chat history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        # Show JSON output in collapsible section if available
                        if message["role"] == "assistant" and "json_output" in message:
                            with st.expander("View Response Details"):
                                st.json(message["json_output"])

                # Chat input
                prompt = st.chat_input(f"Ask a question about {company_name}...")

                # Process the query when submitted
                if prompt:
                    # Validate prompt
                    if len(prompt.strip()) == 0:
                        st.error("Please enter a valid question")
                    elif len(prompt) > 2000:
                        st.error("Question is too long. Please limit to 2000 characters.")
                    else:
                        # Add user message to chat history
                        st.session_state.messages.append(
                            {"role": "user", "content": prompt}
                        )

                        # Display user message
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        # Display assistant response with a spinner while processing
                        with st.chat_message("assistant"):
                            with st.spinner(f"Thinking... (using {model_choice})"):
                                try:
                                    # Validate model selection
                                    if selected_model not in llm_models.values():
                                        st.error("Invalid model selection")
                                        continue

                                    # Create a QA dictionary with advanced configuration
                                    qa_dict = {
                                        "query": prompt,
                                        "llm_kwargs": {
                                            "model_name": selected_model,
                                            "temperature": temperature,
                                        },
                                        "vectorstore_kwargs": {
                                            "k": k_value,
                                            "use_reranker": use_reranker,
                                            "rerank_top_n": (
                                                rerank_top_n if use_reranker else None
                                            ),
                                        },
                                        "recursion_limit": recursion_limit,
                                    }

                                    # Call the company_qa endpoint
                                    qa_url = f"{st.session_state.base_url}/company_qa/"
                                    headers = {
                                        "Authorization": f"Bearer {st.session_state.access_token}",
                                        "Content-Type": "application/json",
                                    }
                                    payload = json.dumps(
                                        {
                                            "company_domain": selected_domain,
                                            "qa_dict": qa_dict,
                                        }
                                    )

                                    response = requests.post(
                                        qa_url, headers=headers, data=payload, timeout=300  # Reduced timeout
                                    )

                                    if response.status_code == 200:
                                        try:
                                            data = response.json()
                                        except json.JSONDecodeError:
                                            st.error("Invalid response format from server")
                                            st.session_state.messages.append(
                                                {
                                                    "role": "assistant",
                                                    "content": "⚠️ Invalid response format from server",
                                                }
                                            )
                                        else:
                                            answer = data.get("output", "No answer available")

                                            # Use answer directly without formatting
                                            formatted_answer = answer

                                            # Display the answer
                                            st.markdown(formatted_answer)

                                            # Create simplified JSON output
                                            json_output = {
                                                "query": prompt,
                                                "response": answer,
                                                "company_domain": selected_domain,
                                                "timestamp": datetime.now().isoformat(),
                                            }

                                            # Add the response data details if available
                                            if isinstance(data, dict):
                                                json_output["full_response"] = data

                                            # Show JSON output in collapsible section
                                            with st.expander("View Response Details"):
                                                st.json(json_output)

                                            # Save to chat history
                                            st.session_state.messages.append(
                                                {
                                                    "role": "assistant",
                                                    "content": formatted_answer,
                                                    "json_output": json_output,
                                                }
                                            )
                                    elif response.status_code == 401:
                                        clear_auth_state()
                                        error_msg = "Session expired. Please authenticate again."
                                        st.error(error_msg)
                                        st.session_state.messages.append(
                                            {
                                                "role": "assistant",
                                                "content": f"⚠️ {error_msg}",
                                            }
                                        )
                                    else:
                                        error_msg = f"Error: {response.status_code} - {response.text[:200]}"
                                        st.error(error_msg)
                                        # Add error message to chat history
                                        st.session_state.messages.append(
                                            {
                                                "role": "assistant",
                                                "content": f"⚠️ {error_msg}",
                                            }
                                        )
                                except requests.exceptions.Timeout:
                                    error_msg = "Request timed out. Please try again."
                                    st.error(error_msg)
                                    st.session_state.messages.append(
                                        {
                                            "role": "assistant",
                                            "content": f"⚠️ {error_msg}",
                                        }
                                    )
                                except requests.exceptions.RequestException as e:
                                    error_msg = f"Network error: {str(e)[:200]}"
                                    st.error(error_msg)
                                    st.session_state.messages.append(
                                        {
                                            "role": "assistant",
                                            "content": f"⚠️ {error_msg}",
                                        }
                                    )
                                except Exception as e:
                                    logger.error(f"Error getting answer: {str(e)}")
                                    error_msg = f"Error getting answer: {str(e)[:200]}"
                                    st.error(error_msg)
                                    # Add error message to chat history
                                    st.session_state.messages.append(
                                        {
                                            "role": "assistant",
                                            "content": f"⚠️ {error_msg}",
                                        }
                                    )

                # Add button to clear chat history
                if st.session_state.messages and st.button("Clear Chat History"):
                    st.session_state.messages = []
                    st.rerun()
            else:
                st.warning("No company domains available in the database.")
        else:
            st.warning(
                "No companies available. Please add companies using the Crawl Company Website feature first."
            )


# Helper functions for QA responses
async def fetch_company_qa_responses(company_domain, qa_list, access_token, base_url):
    """
    Fetch QA responses for a single company domain and a list of QA dictionaries
    """
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for qa_dict in qa_list:
            payload = json.dumps({"company_domain": company_domain, "qa_dict": qa_dict})
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            url = f"{base_url}/company_qa/"
            tasks.append(session.post(url, data=payload, headers=headers))

        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            results = []
            for response in responses:
                if isinstance(response, Exception):
                    logger.error(f"Async request failed: {response}")
                    results.append({"error": f"Request failed: {str(response)}"})
                elif response.status == 200:
                    try:
                        data = await response.json()
                        results.append(data)
                    except (json.JSONDecodeError, aiohttp.ContentTypeError):
                        results.append({"error": "Invalid JSON response"})
                else:
                    results.append({"error": f"HTTP {response.status}: Failed to fetch response"})
            return results
        except Exception as e:
            logger.error(f"Error in fetch_company_qa_responses: {e}")
            return [{"error": f"Failed to fetch responses: {str(e)}"} for _ in qa_list]


async def fetch_qa_responses(domains_list, qa_list, access_token, base_url):
    """
    Fetch QA responses for a list of domains and a list of QA dictionaries
    """
    try:
        qa_tasks = []
        for domain in domains_list:
            qa_tasks.append(
                fetch_company_qa_responses(domain, qa_list, access_token, base_url)
            )
        results = await asyncio.gather(*qa_tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Domain processing failed: {result}")
                processed_results.append([{"error": f"Domain processing failed: {str(result)}"}])
            else:
                processed_results.append(result)
        
        return processed_results
    except Exception as e:
        logger.error(f"Error in fetch_qa_responses: {e}")
        return [[{"error": f"Failed to process domain: {str(e)}"} for _ in qa_list] for _ in domains_list]
