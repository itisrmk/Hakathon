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
    # If the input is not a string, return a default rating
    if not text or not isinstance(text, str):
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
def now_filter(format_string='%B %d, %Y at %I:%M %p'):
    """Return the current datetime formatted as a string"""
    return datetime.now().strftime(format_string)

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/step1', methods=['GET', 'POST'])
def step1():
    """Step 1: Enter medical condition"""
    if request.method == 'POST':
        condition = request.form.get('condition')
        if condition:
            # Store the condition in the session
            session['condition'] = condition
            # Redirect to step 2
            return redirect(url_for('step2'))
    
    # GET request or form validation failed
    return render_template('step1.html')

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    """Step 2: Enter treatment options"""
    # Check if the user has entered a condition
    if 'condition' not in session:
        return redirect(url_for('step1'))
    
    if request.method == 'POST':
        # Get all treatments from the form
        treatments = request.form.getlist('treatments')
        # Filter out empty treatments
        treatments = [t.strip() for t in treatments if t.strip()]
        
        if treatments:
            # Store treatments in session
            session['treatments'] = treatments
            # Redirect to step 3
            return redirect(url_for('step3'))
    
    # GET request or form validation failed
    return render_template('step2.html', condition=session['condition'])

@app.route('/step3', methods=['GET', 'POST'])
def step3():
    """Step 3: Enter patient information"""
    # Check if the user has entered condition and treatments
    if 'condition' not in session or 'treatments' not in session:
        return redirect(url_for('step1'))
    
    if request.method == 'POST':
        # Collect all patient information from the form
        patient_info = {
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'comorbidities': request.form.get('comorbidities'),
            'current_medications': request.form.get('current_medications'),
            'allergies': request.form.get('allergies'),
            'insurance': request.form.get('insurance'),
            'occupation': request.form.get('occupation'),
            'activity_level': request.form.get('activity_level'),
            'dietary_preferences': request.form.get('dietary_preferences'),
            'stress_level': request.form.get('stress_level'),
            'priorities': request.form.get('priorities'),
            'treatment_preferences': request.form.get('treatment_preferences')
        }
        
        # Store patient info in session
        session['patient_info'] = patient_info
        
        # Redirect to loading page, which will process the analysis
        return redirect(url_for('loading'))
    
    # GET request or form validation failed
    return render_template('step3.html', condition=session['condition'])

@app.route('/loading')
def loading():
    """Loading page while analysis is performed"""
    # Check if all required data is available
    if 'condition' not in session or 'treatments' not in session or 'patient_info' not in session:
        return redirect(url_for('step1'))
    
    return render_template('loading.html', condition=session['condition'], treatments=session['treatments'])

@app.route('/process_analysis', methods=['POST'])
def process_analysis():
    """API endpoint to process the treatment analysis asynchronously"""
    try:
        # Check if all required data is available
        if 'condition' not in session or 'treatments' not in session or 'patient_info' not in session:
            return jsonify({'success': False, 'error': 'Missing required session data'})
        
        # Get data from session
        condition = session['condition']
        treatments = session['treatments']
        patient_info = session['patient_info']
        
        # Ensure patient_info contains value preferences and they're not empty
        if not patient_info.get('priorities'):
            patient_info['priorities'] = "effectiveness, minimal side effects" 
        if not patient_info.get('treatment_preferences'):
            patient_info['treatment_preferences'] = "convenient administration, proven approaches"
        
        # Log that we're starting the analysis
        print(f"Starting treatment analysis for condition: {condition}, treatments: {treatments}")
        print(f"Patient values and preferences: {patient_info.get('priorities')}, {patient_info.get('treatment_preferences')}")
        
        # Force the analysis to use the AI agents every time
        # Retry multiple times if needed to ensure we get real agent-generated content
        max_retries = 3
        retry_count = 0
        results = None
        
        while retry_count <= max_retries:
            try:
                if retry_count > 0:
                    print(f"Retry attempt {retry_count} for treatment analysis")
                
                # Run the analysis with forced web search
                results = agent_manager.analyze_treatments(condition, treatments, patient_info, force_web_search=True)
                
                # Log successful analysis
                print(f"Analysis completed successfully. Structure: {list(results.keys())}")
                
                # Ensure the results structure is consistent
                if 'treatment_analyses' not in results and len(results) > 0:
                    # If the expected key doesn't exist but we have some data, restructure it
                    if isinstance(results, dict) and any(t in results for t in treatments):
                        # Looks like the treatments are directly in the results
                        treatment_data = {}
                        for t in treatments:
                            if t in results:
                                treatment_data[t] = results[t]
                        
                        # Update the results with proper structure
                        results = {
                            'condition': condition,
                            'timestamp': datetime.now(),
                            'treatment_analyses': treatment_data,
                            'recommendation': results.get('recommendation', "Please consult your healthcare provider about these treatment options.")
                        }
                        
                        print("Restructured results to use treatment_analyses key")
                
                # Validate that treatment_analyses has entries for each treatment
                if 'treatment_analyses' in results:
                    valid_analyses = True
                    for treatment in treatments:
                        if treatment not in results['treatment_analyses']:
                            valid_analyses = False
                            print(f"Missing analysis for {treatment}")
                            break
                            
                    if valid_analyses:
                        # We have valid results for all treatments
                        break
                        
            except Exception as e:
                print(f"Error during analysis attempt {retry_count}: {str(e)}")
            
            # Increment retry count if we didn't break out of the loop
            retry_count += 1
        
        # If we couldn't get valid results even after retries, report the error
        if not results or 'treatment_analyses' not in results:
            return jsonify({
                'success': False,
                'error': 'Unable to generate treatment analyses after multiple attempts. Please try again later.'
            })
        
        # Store results in session for display on results page
        session['analysis_results'] = results
        
        # Return success response
        return jsonify({
            'success': True,
            'redirect': url_for('results')
        })
    except Exception as e:
        print(f"Process analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/results')
def results():
    """Results page showing treatment analysis"""
    # Check if all required data is available
    if 'condition' not in session or 'treatments' not in session or 'patient_info' not in session:
        return redirect(url_for('step1'))
    
    # Check if analysis results are available
    if 'analysis_results' not in session:
        return redirect(url_for('loading'))
    
    # Get data from session
    condition = session['condition']
    treatments = session['treatments']
    patient_info = session['patient_info']
    analysis_results = session['analysis_results']
    
    # Ensure the analysis_results has the correct structure
    if 'treatment_analyses' in analysis_results:
        # Use the treatment_analyses key directly if it exists (new format)
        treatment_data = analysis_results['treatment_analyses']
    elif 'treatments' in analysis_results:
        # Use the treatments key if it exists (old format)
        treatment_data = analysis_results['treatments']
    else:
        # If neither key exists, we need to regenerate the analysis
        print("Analysis results missing expected structure - regenerating analysis")
        try:
            # Run a new analysis using the agent manager
            new_results = agent_manager.analyze_treatments(condition, treatments, patient_info)
            
            # Update session with new results
            session['analysis_results'] = new_results
            
            # Use the treatment_analyses from the new results
            if 'treatment_analyses' in new_results:
                treatment_data = new_results['treatment_analyses']
            else:
                # If still no treatment_analyses, create an empty structure
                treatment_data = {}
                print("Failed to generate treatment analyses even after retry")
        except Exception as e:
            print(f"Error regenerating analysis: {str(e)}")
            # Create an empty structure if regeneration fails
            treatment_data = {}
    
    return render_template('results.html', 
                          condition=condition,
                          treatments=treatments,
                          patient_info=patient_info,
                          treatment_analyses=treatment_data,
                          recommendation="Based on the analysis of the provided treatments for " + condition + ", here is our recommendation: We recommend consulting with your healthcare provider about these treatment options as they appear promising based on the evidence gathered."
                          )