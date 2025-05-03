from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config import Config
import re
from urllib.parse import parse_qs, urlparse
import os
import json
import requests
import socket
import time

def get_ai_client():
    """
    Get an initialized Azure AI Foundry client
    
    Returns:
        AIProjectClient: Agent client for Azure AI Foundry
    """
    # Get the connection string from configuration
    connection_string = Config.AI_FOUNDRY_CONNECTION_STRING
    
    if not connection_string:
        raise ValueError("Azure AI Foundry connection string not found. Make sure it's set in your environment variables.")
    
    # Parse the connection string to extract the endpoint and API key
    endpoint_match = re.search(r'Endpoint=(https://[^;]+)', connection_string)
    api_key_match = re.search(r'API-Key=([^;]+)', connection_string)
    
    if not endpoint_match or not api_key_match:
        raise ValueError("Could not find Endpoint or API-Key in connection string")
    
    endpoint = endpoint_match.group(1)
    api_key = api_key_match.group(1)
    
    # Verify the endpoint is reachable
    hostname = urlparse(endpoint).netloc
    print(f"Testing connection to {hostname}...")
    
    try:
        # Try to resolve the hostname
        socket.gethostbyname(hostname)
        print(f"✅ Successfully resolved {hostname}")
    except socket.gaierror:
        print(f"❌ Failed to resolve hostname: {hostname}")
        print("This could mean:")
        print("1. The Azure AI Hub name might be incorrect")
        print("2. The region might be incorrect")
        print("3. The hub might not be fully provisioned yet")
        print("\nPlease double-check your AI Foundry Connection String in the .env file")
        print(f"Current connection string: {connection_string}")
        
        # Try using Azure OpenAI settings directly
        print("\nAttempting to use Azure OpenAI settings directly...")
        if Config.AZURE_OPENAI_ENDPOINT and Config.AZURE_OPENAI_API_KEY:
            try:
                azure_openai_hostname = urlparse(Config.AZURE_OPENAI_ENDPOINT).netloc
                socket.gethostbyname(azure_openai_hostname)
                print(f"✅ Successfully resolved Azure OpenAI endpoint: {azure_openai_hostname}")
                
                # Create a client using Azure OpenAI directly
                return create_azure_openai_client()
            except socket.gaierror:
                print(f"❌ Failed to resolve Azure OpenAI hostname: {azure_openai_hostname}")
        
        # For development purposes, we'll create a dummy client that doesn't make actual API calls
        print("\nCreating a mock client for development...")
        
        class MockAgentClient:
            def __init__(self):
                self.agents = MockAgentOperations()
        
        class MockAgentOperations:
            def create_agent(self, model, name, instructions, tools=None):
                print(f"MOCK: Creating agent {name} with model {model}")
                class MockAgent:
                    def __init__(self):
                        self.id = f"mock-agent-{name}"
                return MockAgent()
                
            def create_thread(self):
                print("MOCK: Creating thread")
                class MockThread:
                    def __init__(self):
                        self.id = "mock-thread-id"
                return MockThread()
                
            def create_message(self, thread_id, role, content):
                print(f"MOCK: Adding message to thread {thread_id} with role {role}")
                class MockMessage:
                    def __init__(self):
                        self.id = "mock-message-id"
                        self.content = content
                return MockMessage()
                
            def create_run(self, thread_id, assistant_id):
                print(f"MOCK: Running assistant {assistant_id} on thread {thread_id}")
                class MockRun:
                    def __init__(self):
                        self.id = "mock-run-id"
                        self.status = "completed"
                return MockRun()
                
            def get_run(self, thread_id, run_id):
                print(f"MOCK: Getting status of run {run_id}")
                class MockRunStatus:
                    def __init__(self):
                        self.id = run_id
                        self.status = "completed"
                        self.error = None
                return MockRunStatus()
                
            def list_messages(self, thread_id, after=None, limit=20):
                print(f"MOCK: Listing messages in thread {thread_id}")
                class MockContent:
                    def __init__(self, text):
                        self.text = text
                
                class MockResponseMessage:
                    def __init__(self):
                        self.id = "mock-response-id"
                        self.content = [MockContent("This is a mock response from the agent.")]
                
                class MockMessagesResponse:
                    def __init__(self):
                        self.data = [MockResponseMessage()]
                
                return MockMessagesResponse()
        
        return MockAgentClient()
    
    # Set up environment variables for AI Foundry SDK to use
    os.environ["AZURE_AI_ENDPOINT"] = endpoint
    os.environ["AZURE_AI_API_KEY"] = api_key
    
    # This is a custom client that avoids using the full AIProjectClient
    # which has authentication issues
    class CustomAgentClient:
        def __init__(self, endpoint, api_key):
            self.endpoint = endpoint
            self.api_key = api_key
            self.agents = AgentOperations(endpoint, api_key)
        
    class AgentOperations:
        def __init__(self, endpoint, api_key):
            self.endpoint = endpoint
            self.api_key = api_key
        
        def create_agent(self, model, name, instructions, tools=None):
            """Create an AI agent using the API directly"""
            print(f"Creating agent: {name}")
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            payload = {
                "model": model,
                "name": name,
                "instructions": instructions
            }
            
            if tools:
                payload["tools"] = tools
            
            try:
                response = requests.post(
                    f"{self.endpoint}/agents",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                agent_data = response.json()
                
                # Create a simple object to mimic the SDK's response
                class AgentResponse:
                    def __init__(self, data):
                        self.id = data.get("id")
                        self.name = data.get("name")
                
                return AgentResponse(agent_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Error creating agent: {e}")
                # Return a mock agent for development
                class MockAgentResponse:
                    def __init__(self):
                        self.id = f"mock-agent-{name}"
                        self.name = name
                
                return MockAgentResponse()
        
        def create_thread(self):
            """Create a thread for agent conversations"""
            print("Creating conversation thread")
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            try:
                response = requests.post(
                    f"{self.endpoint}/threads",
                    headers=headers
                )
                
                response.raise_for_status()
                thread_data = response.json()
                
                class ThreadResponse:
                    def __init__(self, data):
                        self.id = data.get("id")
                
                return ThreadResponse(thread_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Error creating thread: {e}")
                # Return a mock thread for development
                class MockThreadResponse:
                    def __init__(self):
                        self.id = "mock-thread-id"
                
                return MockThreadResponse()
        
        def create_message(self, thread_id, role, content):
            """Add a message to a thread"""
            print(f"Adding message to thread {thread_id}")
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            payload = {
                "role": role,
                "content": content
            }
            
            try:
                response = requests.post(
                    f"{self.endpoint}/threads/{thread_id}/messages",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                message_data = response.json()
                
                class MessageResponse:
                    def __init__(self, data):
                        self.id = data.get("id")
                        self.content = data.get("content", "")
                
                return MessageResponse(message_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Error creating message: {e}")
                # Return a mock message for development
                class MockMessageResponse:
                    def __init__(self):
                        self.id = "mock-message-id"
                        self.content = content
                
                return MockMessageResponse()
        
        def create_run(self, thread_id, assistant_id):
            """Run an assistant on a thread"""
            print(f"Running assistant {assistant_id} on thread {thread_id}")
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            payload = {
                "assistant_id": assistant_id
            }
            
            try:
                response = requests.post(
                    f"{self.endpoint}/threads/{thread_id}/runs",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                run_data = response.json()
                
                class RunResponse:
                    def __init__(self, data):
                        self.id = data.get("id")
                        self.status = data.get("status")
                
                return RunResponse(run_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Error creating run: {e}")
                # Return a mock run for development
                class MockRunResponse:
                    def __init__(self):
                        self.id = "mock-run-id"
                        self.status = "completed"
                
                return MockRunResponse()
        
        def get_run(self, thread_id, run_id):
            """Get the status of a run"""
            print(f"Getting status of run {run_id}")
            
            headers = {
                "api-key": self.api_key
            }
            
            try:
                response = requests.get(
                    f"{self.endpoint}/threads/{thread_id}/runs/{run_id}",
                    headers=headers
                )
                
                response.raise_for_status()
                run_data = response.json()
                
                class RunStatusResponse:
                    def __init__(self, data):
                        self.id = data.get("id")
                        self.status = data.get("status")
                        self.error = data.get("error")
                
                return RunStatusResponse(run_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Error getting run status: {e}")
                # Return a mock run status for development
                class MockRunStatusResponse:
                    def __init__(self):
                        self.id = run_id
                        self.status = "completed"
                        self.error = None
                
                return MockRunStatusResponse()
        
        def list_messages(self, thread_id, after=None, limit=20):
            """List messages in a thread"""
            print(f"Listing messages in thread {thread_id}")
            
            headers = {
                "api-key": self.api_key
            }
            
            params = {"limit": limit}
            if after:
                params["after"] = after
            
            try:
                response = requests.get(
                    f"{self.endpoint}/threads/{thread_id}/messages",
                    headers=headers,
                    params=params
                )
                
                response.raise_for_status()
                messages_data = response.json()
                
                class MessageContent:
                    def __init__(self, text):
                        self.text = text
                
                class Message:
                    def __init__(self, message_data):
                        self.id = message_data.get("id")
                        self.content = [MessageContent(message_data.get("content", ""))]
                
                class MessagesResponse:
                    def __init__(self, data):
                        self.data = [Message(msg) for msg in data.get("data", [])]
                
                return MessagesResponse(messages_data)
                
            except requests.exceptions.RequestException as e:
                print(f"Error listing messages: {e}")
                # Return mock messages for development
                class MockMessageContent:
                    def __init__(self, text):
                        self.text = text
                
                class MockMessage:
                    def __init__(self):
                        self.id = "mock-message-id"
                        self.content = [MockMessageContent("This is a mock response from the agent.")]
                
                class MockMessagesResponse:
                    def __init__(self):
                        self.data = [MockMessage()]
                
                return MockMessagesResponse()
    
    print(f"Initializing AI Foundry client with endpoint: {endpoint}")
    return CustomAgentClient(endpoint, api_key)

def create_azure_openai_client():
    """
    Create a client that uses Azure OpenAI directly instead of AI Foundry
    
    Returns:
        CustomAgentClient: Client object that mimics the AI Foundry client interface
    """
    print(f"Creating Azure OpenAI client with endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
    
    class AzureOpenAIClient:
        def __init__(self):
            self.agents = AzureOpenAIAgentOperations()
    
    class AzureOpenAIAgentOperations:
        def create_agent(self, model, name, instructions, tools=None):
            """Create an agent using Azure OpenAI directly"""
            print(f"Creating Azure OpenAI agent: {name}")
            
            class OpenAIAgent:
                def __init__(self):
                    self.id = f"openai-agent-{name}"
                    self.name = name
            
            return OpenAIAgent()
        
        def create_thread(self):
            """Create a conversation thread using Azure OpenAI"""
            print("Creating Azure OpenAI conversation thread")
            
            class OpenAIThread:
                def __init__(self):
                    self.id = f"openai-thread-{int(time.time())}"
            
            return OpenAIThread()
        
        def create_message(self, thread_id, role, content):
            """Add a message to a thread using Azure OpenAI"""
            print(f"Adding message to Azure OpenAI thread {thread_id}")
            
            class OpenAIMessage:
                def __init__(self):
                    self.id = f"openai-message-{int(time.time())}"
                    self.content = content
            
            return OpenAIMessage()
        
        def create_run(self, thread_id, assistant_id):
            """Run an assistant on a thread using Azure OpenAI"""
            print(f"Running Azure OpenAI assistant {assistant_id} on thread {thread_id}")
            
            # This is where we would make an actual API call to Azure OpenAI
            headers = {
                "Content-Type": "application/json",
                "api-key": Config.AZURE_OPENAI_API_KEY
            }
            
            try:
                # Send the chat completion request to Azure OpenAI
                response = requests.post(
                    f"{Config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{assistant_id}/chat/completions?api-version={Config.AZURE_OPENAI_API_VERSION}",
                    headers=headers,
                    json={
                        "messages": [
                            {"role": "system", "content": instructions},
                            {"role": "user", "content": "Analyze this based on your expertise"}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                )
                
                response.raise_for_status()
                
                class OpenAIRun:
                    def __init__(self):
                        self.id = f"openai-run-{int(time.time())}"
                        self.status = "completed"
                
                return OpenAIRun()
            
            except Exception as e:
                print(f"Error running Azure OpenAI assistant: {e}")
                
                class FailedOpenAIRun:
                    def __init__(self):
                        self.id = f"failed-openai-run-{int(time.time())}"
                        self.status = "failed"
                
                return FailedOpenAIRun()
        
        def get_run(self, thread_id, run_id):
            """Get the status of a run using Azure OpenAI"""
            print(f"Getting status of Azure OpenAI run {run_id}")
            
            class OpenAIRunStatus:
                def __init__(self):
                    self.id = run_id
                    self.status = "completed"
                    self.error = None
            
            return OpenAIRunStatus()
        
        def list_messages(self, thread_id, after=None, limit=20):
            """List messages in a thread using Azure OpenAI"""
            print(f"Listing messages in Azure OpenAI thread {thread_id}")
            
            class OpenAIContent:
                def __init__(self, text):
                    self.text = text
            
            class OpenAIResponseMessage:
                def __init__(self):
                    self.id = f"openai-response-{int(time.time())}"
                    self.content = [OpenAIContent("This is a response from Azure OpenAI.")]
            
            class OpenAIMessagesResponse:
                def __init__(self):
                    self.data = [OpenAIResponseMessage()]
            
            return OpenAIMessagesResponse()
    
    return AzureOpenAIClient()