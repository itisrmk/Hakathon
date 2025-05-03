from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import re
from datetime import datetime
from models.agent_manager import AgentManager
from utils.ai_foundry import get_ai_client
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize the agent manager
agent_manager = AgentManager()

# Custom template filters
@app.template_filter('extract_rating')
def extract_rating(text):
    """
    Extract a numeric rating (1-5) from text.
    Default to 3 if no rating is found.
    """
    if not text:
        return 3
        
    # Look for a numeric rating pattern
    patterns = [
        r'rating[:\s]+([1-5])(\/5)?',
        r'([1-5])(\/5)?[\s]+out of[\s]+5',
        r'score[\s]*[:\s]+([1-5])',
        r'rated[\s]*[:\s]+([1-5])',
        r'([1-5])[\s]*stars?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            for group in match.groups():
                if group and group.isdigit():
                    return int(group)
    
    # Default rating if none found
    return 3

@app.template_filter('now')
def now_filter():
    """Return the current datetime"""
    return datetime.now()

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')