import streamlit as st

# Import prompts from separate module
try:
    from utils.prompts import get_research_prompt, get_verse_enhancement_prompt
except ImportError:
    # Fallback if utils not available - define locally
    def get_research_prompt(research_type: str, user_input: str, depth_level: str, include_greek_hebrew: bool) -> str:
        # Simplified fallback prompt
        return f"Please provide a {depth_level.lower()} {research_type.lower()} on: {user_input}"
    
    def get_verse_enhancement_prompt(content: str, research_context: str) -> str:
        return f"Please enhance this content with Bible verse references: {content}"

# Page configuration
st.set_page_config(
    page_title="Biblical Research Tool",
    page_icon="📖",
    layout="wide"
)

def enhance_questions_with_verses_ai(content: str, research_context: str, claude_api_key: str) -> tuple[str, float]:
    """Use AI to enhance questions with relevant Bible verse references"""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        enhancement_prompt = get_verse_enhancement_prompt(content, research_context)
        
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1500,
            system="""You are a biblical research assistant. Enhance study questions by adding specific, 
            relevant Bible verse references that help answer each question. Be conservative and theologically sound.""",
            messages=[
                {
                    "role": "user", 
                    "content": enhancement_prompt
                }
            ]
        )
        
        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = calculate_cost(input_tokens, output_tokens)
        
        return response.content[0].text, cost
        
    except Exception as e:
        # If AI enhancement fails, return original content with no cost
        return content, 0.0

def get_research_prompt(research_type: str, user_input: str, depth_level: str, include_greek_hebrew: bool) -> str:
    """Generate appropriate prompt based on research type and parameters"""
    
    # Base prompt components
    depth_instruction = {
        "Basic": "Provide clear, accessible insights suitable for general Bible study.",
        "Intermediate": "Include moderate theological depth with some technical terms explained.",
        "Deep Theological": "Provide thorough theological analysis with detailed cross-references and doctrinal implications."
    }
    
    greek_hebrew_addon = """
    Include relevant Greek or Hebrew word insights where applicable, explaining:
    - Original word meanings
    - How the word is used elsewhere in Scripture
    - Theological significance of the original language
    """ if include_greek_hebrew else ""
    
    # Research type specific prompts
    if research_type == "Topical Study":
        return f"""
        Conduct a topical Bible study on: {user_input}
        
        Please provide:
        1. KEY BIBLE VERSES: List relevant verses with full text (ESV)
        2. CONTEXT: Brief context for each key verse
        3. CONNECTIONS: How these verses connect to each other thematically
        4. REFLECTION QUESTIONS: Thoughtful questions that include specific Bible verse references for further study (format: "Question? (See [verse reference] for insights)")
        5. PRACTICAL APPLICATION: Concrete application points with supporting verses
        6. ADDITIONAL VERSES FOR STUDY: Suggested verses for deeper exploration
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Format your response with clear section headers. For reflection questions, always include specific Bible verse references that help answer each question.
        """
    
    elif research_type == "Verse Analysis":
        return f"""
        Provide a detailed analysis of: {user_input}
        
        Please include:
        1. VERSE IN CONTEXT: The verse(s) with surrounding context (ESV)
        2. HISTORICAL BACKGROUND: Historical and cultural background
        3. THEOLOGICAL THEMES: Key theological themes and doctrines
        4. CROSS-REFERENCES: Related passages with explanations
        5. REFLECTION QUESTIONS: Personal study questions with specific verse references for answers (format: "Question? (See [verse reference] for insights)")
        6. APPLICATION PRINCIPLES: How to apply this passage today
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Help the reader understand both the immediate context and broader biblical connections. Include specific verse references with all reflection questions.
        """
    
    elif research_type == "Study Guide Builder":
        return f"""
        Create a study guide for: {user_input}
        
        Structure the guide with:
        1. OPENING QUESTIONS: Questions to engage with the text initially
        2. OBSERVATION QUESTIONS: What does the text say? (Include verse references for answers)
        3. INTERPRETATION QUESTIONS: What does it mean? (Include verse references for insights)
        4. APPLICATION QUESTIONS: How should I respond? (Include verse references for guidance)
        5. CROSS-REFERENCE PASSAGES: Related passages to explore with explanations
        6. DISCUSSION QUESTIONS: Questions for group study with supporting verses
        7. PRAYER POINTS: Prayer topics based on the passage
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Make it suitable for both individual and group Bible study. Format questions as: "Question? (See [verse reference] for insights)"
        """
    
    else:  # Cross-Reference Explorer
        return f"""
        Explore cross-references for: {user_input}
        
        Please provide:
        1. The main verse in context (ESV)
        2. 5-7 key cross-references with brief explanations
        3. Thematic connections between passages
        4. Questions about how these passages relate
        5. Suggested study path through the references
        6. Key theological themes that emerge
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Help the reader see the interconnected nature of Scripture.
        """

def calculate_cost(input_tokens: int, output_tokens: int, model: str = "claude-3-5-haiku-20241022") -> float:
    """Calculate cost based on token usage"""
    # Claude 3.5 Haiku pricing (as of current date)
    if "haiku" in model:
        input_cost_per_1k = 0.00025  # $0.25 per 1K input tokens
        output_cost_per_1k = 0.00125  # $1.25 per 1K output tokens
    elif "sonnet" in model:
        input_cost_per_1k = 0.003    # $3.00 per 1K input tokens  
        output_cost_per_1k = 0.015   # $15.00 per 1K output tokens
    else:
        # Default to Haiku pricing
        input_cost_per_1k = 0.00025
        output_cost_per_1k = 0.00125
    
    input_cost = (input_tokens / 1000) * input_cost_per_1k
    output_cost = (output_tokens / 1000) * output_cost_per_1k
    
    return input_cost + output_cost

def generate_research_with_claude(prompt: str, api_key: str) -> tuple[str, float]:
    """Generate biblical research using Claude API and return result with cost"""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
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

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0

def main():
    st.title("📖 Biblical Research Tool")
    st.markdown("*A resource for deeper theological understanding and personal study using theological frameworks built off of the Southern Baptist Faith and Message*")
    
    # Get API key from secrets
    try:
        claude_api_key = st.secrets["CLAUDE_API_KEY"]
    except KeyError:
        claude_api_key = None
        st.error("⚠️ API Key not found in secrets. Please add CLAUDE_API_KEY to your Streamlit app settings.")
        st.stop()
    
    # Main interface - single column layout with more space
    st.header("Research Options")
        
    # Create two columns for better layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Research type selection
        research_type = st.selectbox(
            "Select Research Type:",
            [
                "Topical Study",
                "Verse Analysis", 
                "Study Guide Builder",
                "Cross-Reference Explorer"
            ]
        )
        
        # Input based on research type
        if research_type == "Topical Study":
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
        
        # Generate button
        if st.button("🔍 Generate Research", type="primary"):
            if user_input:
                with st.spinner("Generating biblical research..."):
                    try:
                        # Get the appropriate prompt
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
        st.header("Research Results")
        
def parse_and_display_json_results(json_text: str):
    """Parse JSON results and display them in formatted containers"""
    try:
        import json
        
        # Clean the JSON text - remove any non-JSON content
        json_start = json_text.find('{')
        json_end = json_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            # Fallback to original display if no JSON found
            st.markdown(json_text)
            return
        
        clean_json = json_text[json_start:json_end]
        data = json.loads(clean_json)
        
        # Display title
        if 'title' in data:
            st.markdown(f"## {data['title']}")
        
        # Define section mappings
        section_configs = {
            'key_verses': {'icon': '📖', 'color': 'blue', 'title': 'Key Bible Verses'},
            'verse_context': {'icon': '📖', 'color': 'blue', 'title': 'Verse in Context'},
            'main_verse': {'icon': '📖', 'color': 'blue', 'title': 'Main Verse'},
            'connections': {'icon': '🔗', 'color': 'orange', 'title': 'Connections'},
            'historical_background': {'icon': '🏛️', 'color': 'green', 'title': 'Historical Background'},
            'theological_themes': {'icon': '⛪', 'color': 'indigo', 'title': 'Theological Themes'},
            'cross_references': {'icon': '🔗', 'color': 'orange', 'title': 'Cross References'},
            'key_cross_references': {'icon': '🔗', 'color': 'orange', 'title': 'Key Cross References'},
            'thematic_connections': {'icon': '🔗', 'color': 'orange', 'title': 'Thematic Connections'},
            'reflection_questions': {'icon': '💭', 'color': 'purple', 'title': 'Reflection Questions'},
            'practical_application': {'icon': '🎯', 'color': 'red', 'title': 'Practical Application'},
            'application_principles': {'icon': '🎯', 'color': 'red', 'title': 'Application Principles'},
            'greek_hebrew_insights': {'icon': '🔤', 'color': 'gold', 'title': 'Greek/Hebrew Insights'},
            'additional_study': {'icon': '📚', 'color': 'cyan', 'title': 'Additional Study'},
            'opening_questions': {'icon': '🚀', 'color': 'green', 'title': 'Opening Questions'},
            'observation_questions': {'icon': '👁️', 'color': 'blue', 'title': 'Observation Questions'},
            'interpretation_questions': {'icon': '🧠', 'color': 'purple', 'title': 'Interpretation Questions'},
            'application_questions': {'icon': '🎯', 'color': 'red', 'title': 'Application Questions'},
            'discussion_questions': {'icon': '👥', 'color': 'orange', 'title': 'Discussion Questions'},
            'prayer_points': {'icon': '🙏', 'color': 'violet', 'title': 'Prayer Points'},
            'suggested_study_path': {'icon': '🛤️', 'color': 'brown', 'title': 'Suggested Study Path'}
        }
        
        # Display each section
        for key, value in data.items():
            if key == 'title':
                continue
                
            config = section_configs.get(key, {'icon': '📝', 'color': 'gray', 'title': key.replace('_', ' ').title()})
            
            with st.container():
                st.markdown(f"""
                <div style="
                    border-left: 4px solid {config['color']};
                    padding: 15px;
                    margin: 10px 0;
                    background-color: rgba(128, 128, 128, 0.1);
                    border-radius: 5px;
                ">
                <h4 style="color: {config['color']}; margin-top: 0;">{config['icon']} {config['title']}</h4>
                <div style="margin-left: 10px;">
                """, unsafe_allow_html=True)
                
                # Format content based on type
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            format_dict_item(item)
                        else:
                            st.markdown(f"• {item}")
                elif isinstance(value, dict):
                    format_dict_item(value)
                else:
                    st.markdown(str(value))
                
                st.markdown("</div></div>", unsafe_allow_html=True)
                
    except json.JSONDecodeError as e:
        st.error("Error parsing research results. Displaying raw output:")
        st.markdown(json_text)
    except Exception as e:
        st.error(f"Error displaying results: {e}")
        st.markdown(json_text)

def format_dict_item(item):
    """Format a dictionary item for display"""
    if 'question' in item:
        # Format questions with verse references
        question = item['question']
        if 'verse_references' in item and item['verse_references']:
            refs = ', '.join(item['verse_references'])
            question += f" *(See {refs} for insights)*"
        st.markdown(f"**Q:** {question}")
        
        if 'study_note' in item:
            st.markdown(f"*{item['study_note']}*")
    
    elif 'reference' in item:
        # Format verse references
        st.markdown(f"**{item['reference']}**")
        if 'text' in item:
            st.markdown(f"*{item['text']}*")
        if 'context' in item:
            st.markdown(f"{item['context']}")
        if 'explanation' in item:
            st.markdown(f"{item['explanation']}")
    
    elif 'original' in item:
        # Format Greek/Hebrew words
        st.markdown(f"**{item['original']}** ({item.get('transliteration', 'N/A')})")
        if 'meaning' in item:
            st.markdown(f"Meaning: {item['meaning']}")
        if 'usage_examples' in item:
            examples = ', '.join(item['usage_examples'])
            st.markdown(f"Used in: {examples}")
    
    else:
        # Generic formatting for other dictionary items
        for key, value in item.items():
            if isinstance(value, list):
                value_str = ', '.join(map(str, value))
            else:
                value_str = str(value)
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value_str}")

        if st.session_state.results:
            # Parse and display JSON results
            parse_and_display_json_results(st.session_state.results)
            
            # Option to refine results
            st.subheader("Refine Results")
            refinement = st.text_area(
                "Add specific questions or areas to explore further:",
                placeholder="e.g., How does this connect to Old Testament prophecy?"
            )
            
            if st.button("🔄 Refine Research"):
                if refinement and claude_api_key:
                    with st.spinner("Refining research..."):
                        try:
                            refined_prompt = f"""
                            Based on the previous research, please expand on this specific aspect:
                            {refinement}
                            
                            Previous research context:
                            {st.session_state.results[:500]}...
                            """
                            
                            refined_result, refine_cost = generate_research_with_claude(refined_prompt, claude_api_key)
                            st.session_state.total_cost += refine_cost
                            st.session_state.request_count += 1
                            st.markdown("### Refined Analysis:")
                            st.markdown(refined_result)
                            
                        except Exception as e:
                            st.error(f"Error refining research: {str(e)}")
        else:
            st.info("👈 Select a research type and enter your topic or verse to begin.")
    
    # Cost tracker at bottom of page
    if st.session_state.request_count > 0:
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Research Requests", st.session_state.request_count)
        with col2:
            st.metric("Session Cost", f"${st.session_state.total_cost:.4f}")
        with col3:
            if st.button("🔄 Reset Cost Tracker", help="Reset cost tracking for this session"):
                st.session_state.total_cost = 0.0
                st.session_state.request_count = 0
                st.rerun()
        
        # Small disclaimer
        st.caption("💡 Cost tracking is approximate based on Claude 3.5 Haiku pricing. Actual costs may vary slightly.")

if __name__ == "__main__":
    main()
