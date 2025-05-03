from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config import Config

def get_ai_client():
    """
    Get an initialized Azure AI Foundry client
    
    Returns:
        AIProjectClient: Initialized client for Azure AI Foundry
    """
    # Get the connection string from configuration
    connection_string = Config.AI_FOUNDRY_CONNECTION_STRING
    
    if not connection_string:
        raise ValueError("Azure AI Foundry connection string not found. Make sure it's set in your environment variables.")
    
    # Initialize Azure credentials
    credential = DefaultAzureCredential()
    
    # Create and return the client
    return AIProjectClient(connection_string=connection_string, credential=credential)