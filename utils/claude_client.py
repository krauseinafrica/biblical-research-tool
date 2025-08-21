import anthropic
import streamlit as st
from typing import Optional

class ClaudeClient:
    def __init__(self):
        self.client = None
        self.api_key = None
    
    def set_api_key(self, api_key: str):
        """Set the API key and initialize the client"""
        self.api_key = api_key
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            st.error(f"Failed to initialize Claude client: {str(e)}")
            self.client = None
    
    def generate_research(self, prompt: str) -> str:
        """Generate biblical research using Claude"""
        if not self.client:
            return "Error: Claude client not initialized. Please check your API key."
        
        try:
            # Prepare the system message with theological guidelines
            system_message = """
            You are a biblical research assistant operating within a conservative, doctrinally sound theological framework consistent with the Southern Baptist Faith and Message. 

            GUIDELINES:
            - Provide scripturally based, theologically sound responses
            - Use only well-established, vetted theological resources
            - Avoid controversial topics like abortion, politics, or theologically divisive issues
            - Focus on facilitating study rather than providing complete answers
            - Include relevant cross-references and connections
            - Cite sources when possible with suggestions for further study
            - Ask thought-provoking questions to encourage deeper study
            - Use the English Standard Version (ESV) as primary translation
            - Maintain a tone that encourages personal Bible study and application

            AVOID:
            - Single pastor perspectives or influencer theology
            - Divisive denominational issues
            - Political commentary
            - Speculative or non-biblical content
            - Complete study conclusions (encourage personal discovery)
            """
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                system=system_message,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error generating research: {str(e)}"
