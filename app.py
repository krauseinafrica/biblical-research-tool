import streamlit as st

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
        
        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = calculate_cost(input_tokens, output_tokens)
        
        return response.content[0].text, cost
        
    except Exception as e:
        return f"Error generating research: {str(e)}", 0.0

def get_research_prompt(research_type: str, user_input: str, depth_level: str, include_greek_hebrew: bool) -> str:
    """Generate appropriate prompt based on research type and parameters"""
    
    # Base prompt components
    depth_instruction = {
        "Basic": "Provide clear, accessible insights suitable for general Bible study.",
        "Intermediate": "Include moderate theological depth with some technical terms explained.",
        "Deep Theological": "Provide thorough theological analysis with detailed cross-references and doctrinal implications."
    }
    
    greek_hebrew_addon = """
    
    Include a dedicated "GREEK/HEBREW INSIGHTS" section with:
    - Key original language words with transliterations (e.g., Greek: agape, Hebrew: hesed)
    - Meaning and nuance of original words that may be lost in translation
    - How these words are used in other significant Bible passages
    - Theological significance of the original language choices
    - Practical implications for understanding and application
    - Suggestions for further word study using tools like Strong's Concordance or Blue Letter Bible
    """ if include_greek_hebrew else ""
    
    # Research type specific prompts
    if research_type == "Topical Study":
        return f"""
        Conduct a topical Bible study on: {user_input}
        
        Please provide clearly formatted sections:
        
        1. KEY BIBLE VERSES: List relevant verses with full text (ESV)
        2. CONTEXT: Brief context for each key verse
        3. CONNECTIONS: How these verses connect to each other thematically
        4. REFLECTION QUESTIONS: Thoughtful questions with specific Bible verse references for further study (format: "Question? (See [verse reference] for insights)")
        5. PRACTICAL APPLICATION: Concrete application points with supporting verses
        6. ADDITIONAL VERSES FOR STUDY: Suggested verses for deeper exploration
        {greek_hebrew_addon}
        
        {depth_instruction[depth_level]}
        
        Format your response with clear section headers using ALL CAPS for section names.
        """
    
    elif research_type == "Verse Analysis":
        return f"""
        Provide a detailed analysis of: {user_input}
        
        Please include clearly formatted sections:
        
        1. VERSE IN CONTEXT: The verse(s) with surrounding context (ESV)
        2. HISTORICAL BACKGROUND: Historical and cultural background
        3. THEOLOGICAL THEMES: Key theological themes and doctrines
        4. CROSS-REFERENCES: Related passages with explanations
        5. REFLECTION QUESTIONS: Personal study questions with specific verse references for answers (format: "Question? (See [verse reference] for insights)")
        6. APPLICATION PRINCIPLES: How to apply this passage today
        {greek_hebrew_addon}
        
        {depth_instruction[depth_level]}
        
        Format your response with clear section headers using ALL CAPS for section names.
        """
    
    elif research_type == "Study Guide Builder":
        return f"""
        Create a study guide for: {user_input}
        
        Structure the guide with clearly formatted sections:
        
        1. OPENING QUESTIONS: Questions to engage with the text initially
        2. OBSERVATION QUESTIONS: What does the text say? (Include verse references for answers)
        3. INTERPRETATION QUESTIONS: What does it mean? (Include verse references for insights)
        4. APPLICATION QUESTIONS: How should I respond? (Include verse references for guidance)
        5. CROSS-REFERENCE PASSAGES: Related passages to explore with explanations
        6. DISCUSSION QUESTIONS: Questions for group study with supporting verses
        7. PRAYER POINTS: Prayer topics based on the passage
        {greek_hebrew_addon}
        
        {depth_instruction[depth_level]}
        
        Format your response with clear section headers using ALL CAPS for section names.
        """
    
    else:  # Cross-Reference Explorer
        return f"""
        Explore cross-references for: {user_input}
        
        Please provide clearly formatted sections:
        
        1. MAIN VERSE: The verse in context (ESV)
        2. KEY CROSS-REFERENCES: 5-7 key cross-references with brief explanations
        3. THEMATIC CONNECTIONS: How these passages relate thematically
        4. REFLECTION QUESTIONS: Questions about connections with verse references for deeper study
        5. SUGGESTED STUDY PATH: Recommended order for studying the references
        6. THEOLOGICAL THEMES: Key themes that emerge across the passages
        {greek_hebrew_addon}
        
        {depth_instruction[depth_level]}
        
        Format your response with clear section headers using ALL CAPS for section names.
        """

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
        
        if st.session_state.results:
            # Simple formatted display
            result_text = st.session_state.results
            
            # Split into sections based on ALL CAPS headers
            lines = result_text.split('\n')
            current_section = ""
            sections = []
            
            for line in lines:
                if line.strip() and line.strip().isupper() and ':' in line:
                    if current_section:
                        sections.append(current_section)
                    current_section = line + '\n'
                else:
                    current_section += line + '\n'
            
            if current_section:
                sections.append(current_section)
            
            # Display sections with formatting
            for section in sections:
                if section.strip():
                    lines = section.split('\n')
                    header = lines[0] if lines else "Section"
                    content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                    
                    # Determine icon and color based on header
                    header_lower = header.lower()
                    if 'key bible verses' in header_lower or 'verse in context' in header_lower or 'main verse' in header_lower:
                        icon = "📖"
                        color = "blue"
                    elif 'context' in header_lower or 'historical' in header_lower:
                        icon = "🏛️"
                        color = "green"
                    elif 'connections' in header_lower or 'cross-references' in header_lower:
                        icon = "🔗"
                        color = "orange"
                    elif 'reflection' in header_lower or 'questions' in header_lower:
                        icon = "💭"
                        color = "purple"
                    elif 'application' in header_lower:
                        icon = "🎯"
                        color = "red"
                    elif 'additional' in header_lower:
                        icon = "📚"
                        color = "cyan"
                    elif 'greek' in header_lower or 'hebrew' in header_lower:
                        icon = "🔤"
                        color = "gold"
                    elif 'theological' in header_lower:
                        icon = "⛪"
                        color = "indigo"
                    elif 'prayer' in header_lower:
                        icon = "🙏"
                        color = "violet"
                    else:
                        icon = "📝"
                        color = "gray"
                    
                    # Display with container
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border-left: 4px solid {color};
                            padding: 15px;
                            margin: 10px 0;
                            background-color: rgba(128, 128, 128, 0.1);
                            border-radius: 5px;
                        ">
                        <h4 style="color: {color}; margin-top: 0;">{icon} {header.replace(':', '')}</h4>
                        <div style="margin-left: 10px;">
                        """, unsafe_allow_html=True)
                        
                        st.markdown(content)
                        st.markdown("</div></div>", unsafe_allow_html=True)
            
            # If no sections found, display as-is
            if not sections:
                st.markdown(result_text)
            
            # Option to refine results
            st.subheader("Refine Results")
            refinement = st.text_area(
                "Add specific questions or areas to explore further:",
                placeholder="e.g., How does this connect to Old Testament prophecy?"
            )
            
            if st.button("🔄 Refine Research"):
                if refinement:
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
