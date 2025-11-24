import google.generativeai as genai
import json
import re
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()

class ResearchGenerator:
    """
    Handles all AI model interactions and account plan generation.
    Uses Google's Gemini API with built-in grounding (FREE tier available).
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the generator with API key."""
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("No API key found. Set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=self.api_key)
        
        # Use Gemini Pro (free tier) - correct model name
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.conversation_history = []
    
    def research_company(self, query: str) -> str:
        """
        Perform comprehensive research on a company using Gemini's knowledge.
        
        Args:
            query: User's research query
            
        Returns:
            Comprehensive research findings as formatted text
        """
        try:
            company_name = self._extract_company_name(query)
            
            # Use Gemini to research with its built-in knowledge + reasoning
            prompt = f"""You are a professional company research analyst. Conduct comprehensive research on {company_name} and provide a detailed analysis.

Please structure your research report with the following sections:

1. **Company Overview & Business Model**
   - What does the company do?
   - What industry are they in?
   - What's their market position?

2. **Recent News & Developments**
   - What are the latest developments (last 6-12 months)?
   - Any major announcements or changes?

3. **Financial Performance**
   - Revenue trends
   - Profitability
   - Market cap or valuation (if public)

4. **Products & Services**
   - Main product lines
   - Key offerings
   - Innovation areas

5. **Key Competitors & Market Position**
   - Who are their main competitors?
   - What's their competitive advantage?
   - Market share position

6. **Leadership Team**
   - CEO and key executives
   - Notable board members
   - Leadership changes

7. **Challenges & Pain Points**
   - Current business challenges
   - Industry headwinds
   - Operational issues

8. **Growth Initiatives & Strategic Priorities**
   - Expansion plans
   - New market entries
   - Strategic partnerships

Provide specific, factual information based on your knowledge. If certain information is not available in your training data, clearly state that recent data may need to be verified. Be professional, detailed, and actionable."""

            response = self.model.generate_content(prompt)
            research_content = response.text
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": research_content
            })
            
            return research_content
            
        except Exception as e:
            return f"Error during research: {str(e)}\n\nPlease check your API key and try again."
    
    def generate_account_plan(self, research_data: str) -> Optional[Dict[str, str]]:
        """
        Generate a structured account plan based on research data.
        
        Args:
            research_data: The research findings about the company
            
        Returns:
            Dictionary containing account plan sections, or None if generation fails
        """
        try:
            prompt = f"""Based on the following research data, generate a comprehensive account plan in JSON format.

Research Data:
{research_data}

Generate ONLY valid JSON with these exact keys (no additional text, explanation, or markdown):

{{
  "company_overview": "Brief 2-3 sentence overview of the company, their industry, and current market position",
  "key_stakeholders": "List of decision makers, influencers, and key contacts with their roles and relevance. Include names if available from research.",
  "pain_points": "3-5 major business challenges or pain points the company is facing based on the research",
  "value_proposition": "How we can help address their pain points and add value to their business. Be specific and actionable.",
  "engagement_strategy": "Recommended approach for engaging with this account, including timing, channels, and key messaging",
  "success_metrics": "Key performance indicators and metrics to track success of the engagement. Include specific, measurable goals.",
  "next_steps": "Specific action items with timeline for next 30-60-90 days. Be concrete and actionable."
}}

CRITICAL: Respond with ONLY the JSON object. No markdown code blocks, no explanations, just pure JSON."""

            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse JSON response
            plan_data = self._parse_json_response(response_text)
            
            # Validate required sections
            required_sections = [
                'company_overview', 'key_stakeholders', 'pain_points',
                'value_proposition', 'engagement_strategy', 'success_metrics',
                'next_steps'
            ]
            
            if plan_data and all(section in plan_data for section in required_sections):
                return plan_data
            else:
                print("Generated plan missing required sections")
                return None
                
        except Exception as e:
            print(f"Error generating account plan: {str(e)}")
            return None
    
    def regenerate_section(self, section_name: str, current_content: str, 
                          instruction: str, research_data: str) -> str:
        """
        Regenerate a specific section of the account plan.
        
        Args:
            section_name: Name of the section to regenerate
            current_content: Current content of the section
            instruction: User's instruction for how to modify it
            research_data: Original research data for context
            
        Returns:
            New content for the section
        """
        try:
            prompt = f"""Update this section of an account plan.

Section Name: {section_name}
Current Content: {current_content}

User's Instruction: {instruction}

Research Context: {research_data[:1000]}...

Provide ONLY the updated section content, no formatting or explanation."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error regenerating section: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """
        Handle general conversational queries.
        
        Args:
            user_message: User's message
            
        Returns:
            Assistant's response
        """
        try:
            system_context = """You are a helpful company research assistant. Your role is to:
            1. Help users research companies
            2. Generate comprehensive account plans
            3. Answer questions about the research process
            4. Guide users through using the system
            
            Be friendly, professional, and concise."""
            
            prompt = f"{system_context}\n\nUser: {user_message}\n\nAssistant:"
            
            response = self.model.generate_content(prompt)
            reply = response.text
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": reply
            })
            
            return reply
            
        except Exception as e:
            return f"I encountered an error: {str(e)}\n\nPlease try again."
    
    def _extract_company_name(self, query: str) -> str:
        """Extract company name from user query."""
        keywords = ['research', 'tell me about', 'find information', 'search', 'about', 'on']
        company_name = query.lower()
        
        for keyword in keywords:
            company_name = company_name.replace(keyword, '')
        
        return company_name.strip()
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse JSON from response text, handling markdown code blocks.
        
        Args:
            response_text: Raw response text that may contain JSON
            
        Returns:
            Parsed JSON as dictionary, or None if parsing fails
        """
        try:
            # Remove markdown code blocks
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response_text)
            cleaned_text = cleaned_text.strip()
            
            # Try to parse JSON
            return json.loads(cleaned_text)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            
            # Try to find JSON object in the text
            try:
                start = cleaned_text.find('{')
                end = cleaned_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = cleaned_text[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            return None
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []