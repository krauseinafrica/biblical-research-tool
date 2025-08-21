import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Biblical Research Tool",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        1. Key Bible verses related to this topic (ESV)
        2. Brief context for each verse
        3. How these verses connect to each other
        4. Questions for further reflection
        5. Practical application points
        6. Suggested additional verses to study
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Format your response with clear sections and include verse references.
        """
    
    elif research_type == "Verse Analysis":
        return f"""
        Provide a detailed analysis of: {user_input}
        
        Please include:
        1. The verse(s) in context (ESV)
        2. Historical and cultural background
        3. Key theological themes
        4. Cross-references to related passages
        5. Questions for personal study
        6. Application principles
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Help the reader understand both the immediate context and broader biblical connections.
        """
    
    elif research_type == "Study Guide Builder":
        return f"""
        Create a study guide for: {user_input}
        
        Structure the guide with:
        1. Opening questions to engage with the text
        2. Observation questions (What does it say?)
        3. Interpretation questions (What does it mean?)
        4. Application questions (How should I respond?)
        5. Cross-reference passages to explore
        6. Discussion questions for group study
        7. Prayer points based on the passage
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Make it suitable for both individual and group Bible study.
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

def generate_research_with_claude(prompt: str, api_key: str) -> str:
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
            model="claude-3-5-sonnet-20241022",
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

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

def main():
    st.title("📖 Biblical Research Tool")
    st.markdown("*A resource for deeper theological understanding and personal study using theological frameworks built off of the Southern Baptist Faith and Message*")
    
    # Get API key from secrets
    try:
        claude_api_key = st.secrets["CLAUDE_API_KEY"]
        api_key_status = "✅ Connected"
    except KeyError:
        claude_api_key = None
        api_key_status = "❌ API Key not found in secrets"
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key status
        st.write("**Claude API Status:**")
        st.write(api_key_status)
        
        if not claude_api_key:
            st.error("Please add CLAUDE_API_KEY to your Streamlit secrets.")
        
        st.divider()
        
        # Theological framework info
        st.info("""
        **Theological Framework:**
        - Southern Baptist Faith and Message
        - Conservative, scripturally sound
        - Vetted theological resources
        """)
    
    # Main interface
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
            if user_input and claude_api_key:
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
                        result = generate_research_with_claude(prompt, claude_api_key)
                        st.session_state.results = result
                        
                    except Exception as e:
                        st.error(f"Error generating research: {str(e)}")
            else:
                if not user_input:
                    st.warning("Please enter your research topic or verse.")
                if not claude_api_key:
                    st.warning("API key not found in secrets. Please configure CLAUDE_API_KEY in your Streamlit app settings.")
    
    with col2:
        st.header("Research Results")
        
        if st.session_state.results:
            # Display results
            st.markdown(st.session_state.results)
            
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
                            
                            refined_result = generate_research_with_claude(refined_prompt, claude_api_key)
                            st.markdown("### Refined Analysis:")
                            st.markdown(refined_result)
                            
                        except Exception as e:
                            st.error(f"Error refining research: {str(e)}")
        else:
            st.info("👈 Select a research type and enter your topic or verse to begin.")

if __name__ == "__main__":
    main()
