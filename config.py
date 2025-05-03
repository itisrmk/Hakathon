import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the Flask application"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Azure AI Foundry configuration
    AI_FOUNDRY_CONNECTION_STRING = os.getenv('AI_FOUNDRY_CONNECTION_STRING')
    AI_FOUNDRY_SUBSCRIPTION_ID = os.getenv('AI_FOUNDRY_SUBSCRIPTION_ID')
    AI_FOUNDRY_RESOURCE_GROUP = os.getenv('AI_FOUNDRY_RESOURCE_GROUP')
    AI_FOUNDRY_PROJECT_NAME = os.getenv('AI_FOUNDRY_PROJECT_NAME')
    
    # Agent IDs
    EVIDENCE_AGENT_ID = os.getenv('EVIDENCE_AGENT_ID')
    SIDE_EFFECTS_AGENT_ID = os.getenv('SIDE_EFFECTS_AGENT_ID')
    LIFESTYLE_AGENT_ID = os.getenv('LIFESTYLE_AGENT_ID')
    COST_AGENT_ID = os.getenv('COST_AGENT_ID')
    VALUES_AGENT_ID = os.getenv('VALUES_AGENT_ID')
    ORCHESTRATOR_AGENT_ID = os.getenv('ORCHESTRATOR_AGENT_ID')
    
    # Azure OpenAI configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15')
    AZURE_OPENAI_DEPLOYMENT_ID = os.getenv('AZURE_OPENAI_DEPLOYMENT_ID', 'gpt-4')
    
    # Azure AI Search configuration
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY')
    AZURE_SEARCH_INDEX = os.getenv('AZURE_SEARCH_INDEX', 'medical-treatments-index')
    
    # Bing Search API configuration
    BING_SEARCH_API_KEY = os.getenv('BING_SEARCH_API_KEY')