import json
import asyncio
import time
from config import Config
from utils.ai_foundry import get_ai_client

class AgentManager:
    """Manages creation and coordination of specialized agents"""
    
    def __init__(self):
        """Initialize the agent manager"""
        self.project_client = get_ai_client()
        self.setup_agents()
    
    def setup_agents(self):
        """Set up agent IDs from configuration"""
        self.evidence_agent_id = Config.EVIDENCE_AGENT_ID
        self.side_effects_agent_id = Config.SIDE_EFFECTS_AGENT_ID
        self.lifestyle_agent_id = Config.LIFESTYLE_AGENT_ID
        self.cost_agent_id = Config.COST_AGENT_ID
        self.values_agent_id = Config.VALUES_AGENT_ID
        self.orchestrator_agent_id = Config.ORCHESTRATOR_AGENT_ID
        
        # Create agents if they don't exist yet
        if not all([
            self.evidence_agent_id,
            self.side_effects_agent_id,
            self.lifestyle_agent_id,
            self.cost_agent_id,
            self.values_agent_id,
            self.orchestrator_agent_id
        ]):
            self._create_specialized_agents()
    
    def _create_specialized_agents(self):
        """Create the specialized treatment agents if they don't exist yet"""
        # Create evidence analysis agent if needed
        if not self.evidence_agent_id:
            evidence_agent = self.project_client.agents.create_agent(
                model="gpt-4o",
                name="evidence-analysis-agent",
                instructions="""You are an evidence analysis agent specialized in evaluating research support for medical treatments.
                Analyze medical literature, clinical trials, and meta-analyses to determine the strength of evidence for different treatment approaches.
                Focus on evidence quality, consistency of findings, recency of research, and applicability to the patient's condition.
                Rate evidence strength on a scale from 1-5 and explain your reasoning.""",
                tools=[
                    {"type": "azure_ai_search", "config": {"name": "medical_research_db"}}
                ]
            )
            self.evidence_agent_id = evidence_agent.id
        
        # Create side effect assessment agent if needed
        if not self.side_effects_agent_id:
            side_effect_agent = self.project_client.agents.create_agent(
                model="gpt-4o",
                name="side-effect-assessment-agent",
                instructions="""You are a side effect assessment agent specialized in comparing risks of different treatments.
                Analyze and report potential side effects, their severity, frequency, and how they might affect patient quality of life.
                Consider both common and rare side effects, with particular attention to the patient's specific risk factors.
                Rate side effect burden on a scale from 1-5 and explain your reasoning.""",
                tools=[
                    {"type": "azure_ai_search", "config": {"name": "medical_research_db"}}
                ]
            )
            self.side_effects_agent_id = side_effect_agent.id
        
        # Create lifestyle compatibility agent if needed
        if not self.lifestyle_agent_id:
            lifestyle_agent = self.project_client.agents.create_agent(
                model="gpt-4o",
                name="lifestyle-compatibility-agent",
                instructions="""You are a lifestyle compatibility agent specialized in evaluating how treatments impact daily life.
                Consider factors like treatment schedule, mobility requirements, dietary restrictions, and impact on work and social activities.
                Analyze how each treatment option might disrupt or complement the patient's current lifestyle based on their profile.
                Rate lifestyle compatibility on a scale from 1-5 and explain your reasoning.""",
                tools=[
                    {"type": "azure_ai_search", "config": {"name": "medical_research_db"}}
                ]
            )
            self.lifestyle_agent_id = lifestyle_agent.id
        
        # Create cost analysis agent if needed
        if not self.cost_agent_id:
            cost_agent = self.project_client.agents.create_agent(
                model="gpt-4o",
                name="cost-analysis-agent",
                instructions="""You are a cost analysis agent specialized in considering financial implications of treatments.
                Analyze direct costs, insurance coverage, long-term expenses, and potential financial assistance programs.
                Consider both immediate and ongoing costs, as well as potential financial impacts of treatment success or failure.
                Rate cost burden on a scale from 1-5 and explain your reasoning.""",
                tools=[
                    {"type": "azure_ai_search", "config": {"name": "medical_research_db"}}
                ]
            )
            self.cost_agent_id = cost_agent.id
        
        # Create personal value alignment agent if needed
        if not self.values_agent_id:
            value_agent = self.project_client.agents.create_agent(
                model="gpt-4o",
                name="personal-value-alignment-agent",
                instructions="""You are a personal value alignment agent specialized in reflecting patient priorities.
                Consider patient-specific factors like personal health goals, treatment preferences, cultural considerations, and comfort with different approaches.
                Analyze how each treatment aligns with the patient's stated values and preferences.
                Rate value alignment on a scale from 1-5 and explain your reasoning.""",
                tools=[
                    {"type": "azure_ai_search", "config": {"name": "medical_research_db"}}
                ]
            )
            self.values_agent_id = value_agent.id
        
        # Create orchestrator agent if needed
        if not self.orchestrator_agent_id:
            orchestrator_agent = self.project_client.agents.create_agent(
                model="gpt-4o",
                name="treatment-recommendation-orchestrator",
                instructions="""You are a treatment recommendation orchestrator that synthesizes analyses from multiple specialized agents.
                Consider all the analyses provided and generate a comprehensive treatment recommendation.
                Weigh the different factors based on the patient's specific situation and values.
                Present a clear recommendation with justification and address any potential concerns or trade-offs."""
            )
            self.orchestrator_agent_id = orchestrator_agent.id
    
    def analyze_treatments(self, condition, treatment_options, patient_data):
        """
        Analyze multiple treatment options for a specific condition
        
        Args:
            condition (str): The medical condition to analyze
            treatment_options (list): List of treatment options to analyze
            patient_data (dict): Patient information for personalized analysis
            
        Returns:
            dict: Analysis results for each treatment and recommendation
        """
        # Create an analysis session thread
        thread = self.project_client.agents.create_thread()
        thread_id = thread.id
        
        # Results dictionary
        results = {"treatment_analyses": {}}
        
        # Process each treatment option
        for treatment in treatment_options:
            results["treatment_analyses"][treatment] = {}
            
            # Evidence analysis
            evidence_result = self._run_agent_analysis(
                thread_id,
                self.evidence_agent_id,
                f"Analyze the evidence support for {treatment} in treating {condition}. Patient data: {json.dumps(patient_data)}"
            )
            results["treatment_analyses"][treatment]["evidence"] = evidence_result
            
            # Side effects analysis
            side_effect_result = self._run_agent_analysis(
                thread_id,
                self.side_effects_agent_id,
                f"Analyze the potential side effects of {treatment} for {condition}. Patient data: {json.dumps(patient_data)}"
            )
            results["treatment_analyses"][treatment]["side_effects"] = side_effect_result
            
            # Lifestyle compatibility analysis
            lifestyle_result = self._run_agent_analysis(
                thread_id,
                self.lifestyle_agent_id,
                f"Analyze the lifestyle compatibility of {treatment} for {condition}. Patient data: {json.dumps(patient_data)}"
            )
            results["treatment_analyses"][treatment]["lifestyle"] = lifestyle_result
            
            # Cost analysis
            cost_result = self._run_agent_analysis(
                thread_id,
                self.cost_agent_id,
                f"Analyze the cost implications of {treatment} for {condition}. Patient data: {json.dumps(patient_data)}"
            )
            results["treatment_analyses"][treatment]["cost"] = cost_result
            
            # Value alignment analysis
            value_result = self._run_agent_analysis(
                thread_id,
                self.values_agent_id,
                f"Analyze how {treatment} for {condition} aligns with the patient's values. Patient data: {json.dumps(patient_data)}"
            )
            results["treatment_analyses"][treatment]["values"] = value_result
        
        # Generate final recommendation
        analyses_summary = json.dumps(results["treatment_analyses"], indent=2)
        recommendation_prompt = f"""
        Generate a comprehensive treatment recommendation for {condition} based on the following analyses:
        
        Patient Data:
        {json.dumps(patient_data, indent=2)}
        
        Treatment Analyses:
        {analyses_summary}
        
        Please provide:
        1. A ranked recommendation of treatments
        2. Justification for the ranking
        3. Key considerations for the patient
        4. Potential next steps
        """
        
        recommendation = self._run_agent_analysis(
            thread_id,
            self.orchestrator_agent_id,
            recommendation_prompt
        )
        
        results["recommendation"] = recommendation
        
        return results
    
    def _run_agent_analysis(self, thread_id, agent_id, prompt):
        """
        Run a specific agent analysis and return the result
        
        Args:
            thread_id (str): ID of the thread for this analysis
            agent_id (str): ID of the agent to run
            prompt (str): Prompt for the agent
            
        Returns:
            str: Agent's response
        """
        # Add the message to the thread
        message = self.project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=prompt
        )
        
        # Run the agent
        run = self.project_client.agents.create_run(
            thread_id=thread_id,
            assistant_id=agent_id
        )
        
        # Poll for completion
        completed = False
        result = None
        
        while not completed:
            run_status = self.project_client.agents.get_run(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run_status.status == "completed":
                completed = True
                
                # Get the assistant's response
                messages = self.project_client.agents.list_messages(
                    thread_id=thread_id,
                    after=message.id,
                    limit=1
                )
                
                if messages.data:
                    result = messages.data[0].content[0].text
            elif run_status.status == "failed":
                raise Exception(f"Agent run failed: {run_status.error or 'Unknown error'}")
            
            # Wait a bit before polling again
            if not completed:
                time.sleep(1)
        
        return result