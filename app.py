# Clean app.py - Remove duplicate prompts, import from prompts.py

import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from urllib.parse import quote

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0

# Import ALL prompts from consolidated prompts.py
try:
    from utils.prompts import get_research_prompt, get_verse_enhancement_prompt, get_system_message
except ImportError:
    st.error("Could not import prompts. Please ensure utils/prompts.py exists.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Biblical Research Tool",
    page_icon="📖",
    layout="wide"
)

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on token usage for Claude 3.5 Haiku"""
    input_cost_per_1k = 0.00025  # $0.25 per 1K input tokens
    output_cost_per_1k = 0.00125  # $1.25 per 1K output tokens
    
    input_cost = (input_tokens / 1000) * input_cost_per_1k
    output_cost = (output_tokens / 1000) * output_cost_per_1k
    
    return input_cost + output_cost

def generate_research_with_claude(prompt: str, api_key: str):
    """Generate biblical research using Claude API"""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Use system message from prompts.py
        system_message = get_system_message()
        
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            system=system_message,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        # Calculate cost based on token usage
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = calculate_cost(input_tokens, output_tokens)
        
        return response.content[0].text, cost
        
    except Exception as e:
        return f"Error generating research: {str(e)}", 0.0

# ===== REMOVE THIS SECTION FROM YOUR APP.PY =====
# def get_research_prompt(...):  <-- DELETE THIS ENTIRE FUNCTION
# Your app.py should NOT have any prompt functions anymore

# ===== API FUNCTIONS FOR CROSS-REFERENCE LOOKUP =====
def search_bible_api(query, bible_version="ESV", limit=50):
    """Universal Bible search function"""
    try:
        url = "https://api.biblesupersearch.com/api"
        params = {
            'query': query,
            'bible': bible_version,
            'format': 'json',
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            st.warning(f"Bible API returned status {response.status_code}")
            return []
            
    except requests.RequestException as e:
        st.warning(f"Could not connect to Bible API: {e}")
        return []

def extract_keywords_from_json(json_data):
    """Extract cross-reference keywords from JSON response"""
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        return data.get('cross_reference_keywords', [])
    except (json.JSONDecodeError, KeyError):
        return []

def display_cross_reference_section(keywords, research_type, user_input):
    """Display cross-reference lookup section"""
    if not keywords:
        return
    
    st.divider()
    st.subheader("🔍 Explore Scripture Cross-References")
    st.markdown("*See how these key concepts appear throughout the Bible:*")
    
    # Show keywords as tags
    st.markdown("**Key words from this study:**")
    keyword_tags = " • ".join([f"`{word}`" for word in keywords])
    st.markdown(keyword_tags)
    
    if st.button("📖 Find Cross-References in Scripture", type="secondary"):
        with st.spinner("Searching Scripture for cross-references..."):
            
            for word in keywords:
                with st.expander(f"📚 '{word}' throughout Scripture", expanded=False):
                    # Search for this word in the Bible
                    results = search_bible_api(f'"{word}"', limit=20)
                    
                    if results:
                        # Separate Old and New Testament
                        ot_books = {
                            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
                            "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
                            "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther",
                            "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Songs",
                            "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
                            "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
                            "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"
                        }
                        
                        ot_verses = [r for r in results if r.get('book_name', '') in ot_books]
                        nt_verses = [r for r in results if r.get('book_name', '') not in ot_books]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if ot_verses:
                                st.markdown("**📜 Old Testament:**")
                                for verse in ot_verses[:5]:
                                    reference = f"{verse.get('book_name', '')} {verse.get('chapter', '')}:{verse.get('verse', '')}"
                                    text = verse.get('text', '')
                                    if len(text) > 100:
                                        text = text[:100] + "..."
                                    
                                    st.markdown(f"""
                                    <div style="margin: 5px 0; padding: 8px; border-left: 3px solid #8B4513; background-color: rgba(139, 69, 19, 0.1);">
                                    <strong>{reference}</strong><br>
                                    <em>"{text}"</em>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        with col2:
                            if nt_verses:
                                st.markdown("**✝️ New Testament:**")
                                for verse in nt_verses[:5]:
                                    reference = f"{verse.get('book_name', '')} {verse.get('chapter', '')}:{verse.get('verse', '')}"
                                    text = verse.get('text', '')
                                    if len(text) > 100:
                                        text = text[:100] + "..."
                                    
                                    st.markdown(f"""
                                    <div style="margin: 5px 0; padding: 8px; border-left: 3px solid #4169E1; background-color: rgba(65, 105, 225, 0.1);">
                                    <strong>{reference}</strong><br>
                                    <em>"{text}"</em>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Bible Gateway search link
                        search_url = f"https://www.biblegateway.com/quicksearch/?search={quote(word)}&version=ESV"
                        st.markdown(f"🔍 [Search all '{word}' references on Bible Gateway]({search_url})")
                    else:
                        st.info(f"No results found for '{word}' - try a Bible Gateway search instead.")
                        search_url = f"https://www.biblegateway.com/quicksearch/?search={quote(word)}&version=ESV"
                        st.markdown(f"🔍 [Search '{word}' on Bible Gateway]({search_url})")

# ===== KEEP ALL YOUR EXISTING WORD STUDY FUNCTIONS =====
# load_bible_word_data()
# create_word_study_interface() 
# etc. - these stay the same

# ===== YOUR MAIN FUNCTION WITH CLEAN PROMPT IMPORTS =====
def main():
    st.title("📖 Biblical Research Tool")
    st.markdown("*A resource for deeper theological understanding and personal study*")
    
    # Get API key from secrets
    try:
        claude_api_key = st.secrets["CLAUDE_API_KEY"]
    except KeyError:
        claude_api_key = None
        st.error("⚠️ API Key not found in secrets. Please add CLAUDE_API_KEY to your Streamlit app settings.")
        st.stop()
    
    # Create two columns for better layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Research Options")
        
        # Research type selection
        research_type = st.selectbox(
            "Select Research Type:",
            [
                "Topical Study",
                "Verse Analysis", 
                "Study Guide Builder",
                "Cross-Reference Explorer",
                "Word Study"
            ]
        )
        
        # Input based on research type
        if research_type == "Word Study":
            user_input = None
        elif research_type == "Topical Study":
            user_input = st.text_input(
                "Enter topic or theme:",
                placeholder="e.g., faith, prayer, salvation"
            )
        elif research_type == "Verse Analysis":
            user_input = st.text_area(
                "Enter Bible verse or passage:",
                placeholder="e.g., John 3:16 or Romans 8:28-30"
            )
        elif research_type == "Study Guide Builder":
            user_input = st.text_area(
                "Enter verse or passage for study guide:",
                placeholder="e.g., Ephesians 2:8-10"
            )
        else:  # Cross-Reference Explorer
            user_input = st.text_input(
                "Enter verse for cross-references:",
                placeholder="e.g., 1 Corinthians 13:4"
            )
        
        # Handle Word Study separately - no user input needed initially
        if research_type != "Word Study":
            # Additional options
            st.subheader("Options")
            depth_level = st.radio(
                "Study Depth:",
                ["Basic", "Intermediate", "Deep Theological"]
            )
            
            include_greek_hebrew = st.checkbox(
                "Include Greek/Hebrew insights",
                value=False
            )
            
            # Generate button for regular research
            if st.button("🔍 Generate Research", type="primary"):
                if user_input:
                    with st.spinner("Generating biblical research..."):
                        try:
                            # Get prompt from prompts.py (clean import)
                            prompt = get_research_prompt(
                                research_type, 
                                user_input, 
                                depth_level, 
                                include_greek_hebrew
                            )
                            
                            # Generate research using Claude
                            result, cost = generate_research_with_claude(prompt, claude_api_key)
                            st.session_state.results = result
                            st.session_state.total_cost += cost
                            st.session_state.request_count += 1
                            
                        except Exception as e:
                            st.error(f"Error generating research: {str(e)}")
                else:
                    st.warning("Please enter your research topic or verse.")
    
    with col2:
        # Handle Word Study differently
        if research_type == "Word Study":
            create_word_study_interface()  # Your existing word study function
        else:
            st.header("Research Results")
            
            if st.session_state.results:
                # Parse and display JSON results (your existing function)
                parse_and_display_json_results(st.session_state.results)
                
                # NEW: Add cross-reference section
                try:
                    # Extract keywords from JSON for cross-reference lookup
                    json_start = st.session_state.results.find('{')
                    json_end = st.session_state.results.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        clean_json = st.session_state.results[json_start:json_end]
                        data = json.loads(clean_json)
                        keywords = data.get('cross_reference_keywords', [])
                        
                        if keywords:
                            display_cross_reference_section(keywords, research_type, user_input)
                            
                except (json.JSONDecodeError, KeyError):
                    pass  # Fail silently if JSON parsing fails
                
                # Your existing refinement section stays the same
                # ...
            
            # Only show this message if no results for non-Word Study types
            if not st.session_state.results:
                st.info("👈 Select a research type and enter your topic or verse to begin.")
    
    # Your existing cost tracker section stays the same
    # ...

if __name__ == "__main__":
    main()
