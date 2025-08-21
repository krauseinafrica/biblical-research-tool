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

def enhance_questions_with_verses_ai(content: str, research_context: str, claude_api_key: str) -> str:
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
        
        return response.content[0].text
        
    except Exception as e:
        # If AI enhancement fails, return original content
        return content

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
                        result = generate_research_with_claude(prompt, claude_api_key)
                        st.session_state.results = result
                        
                    except Exception as e:
                        st.error(f"Error generating research: {str(e)}")
            else:
                st.warning("Please enter your research topic or verse.")
    
    with col2:
        st.header("Research Results")
        
        if st.session_state.results:
            # Display results with enhanced formatting
            st.header("Research Results")
            
            # Parse and format the results
            result_text = st.session_state.results
            
            # Split the content into sections based on numbered lists or headers
            sections = []
            current_section = ""
            lines = result_text.split('\n')
            
            for line in lines:
                if line.strip():
                    # Check if this is a main section header
                    if (line.strip().endswith(':') and 
                        any(keyword in line.upper() for keyword in 
                            ['KEY BIBLE VERSES', 'CONTEXT', 'CONNECTIONS', 'REFLECTION QUESTIONS', 
                             'PRACTICAL APPLICATION', 'ADDITIONAL VERSES', 'CROSS-REFERENCES',
                             'HISTORICAL BACKGROUND', 'THEOLOGICAL THEMES', 'APPLICATION PRINCIPLES'])):
                        if current_section:
                            sections.append(current_section)
                        current_section = line + '\n'
                    else:
                        current_section += line + '\n'
                else:
                    current_section += '\n'
            
            if current_section:
                sections.append(current_section)
            
            # Display each section in a container
            for i, section in enumerate(sections):
                if section.strip():
                    # Determine section type and icon
                    section_lower = section.lower()
                    if 'key bible verses' in section_lower:
                        icon = "📖"
                        color = "blue"
                    elif 'context' in section_lower:
                        icon = "🏛️"
                        color = "green"
                    elif 'connections' in section_lower or 'cross-references' in section_lower:
                        icon = "🔗"
                        color = "orange"
                    elif 'reflection' in section_lower or 'questions' in section_lower:
                        icon = "💭"
                        color = "purple"
                    elif 'practical application' in section_lower or 'application' in section_lower:
                        icon = "🎯"
                        color = "red"
                    elif 'additional verses' in section_lower:
                        icon = "📚"
                        color = "cyan"
                    elif 'theological themes' in section_lower:
                        icon = "⛪"
                        color = "indigo"
                    elif 'historical background' in section_lower:
                        icon = "🏺"
                        color = "brown"
                    else:
                        icon = "📝"
                        color = "gray"
                    
                    # Create container with colored border
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border-left: 4px solid #{color};
                            padding: 15px;
                            margin: 10px 0;
                            background-color: rgba(128, 128, 128, 0.1);
                            border-radius: 5px;
                        ">
                        <h4 style="color: #{color}; margin-top: 0;">{icon} {section.split(':')[0] if ':' in section else 'Content'}</h4>
                        <div style="margin-left: 10px;">
                        """, unsafe_allow_html=True)
                        
                        # Process the content to add verse references to questions
                        content = ':'.join(section.split(':')[1:]).strip() if ':' in section else section
                        
                        # If this is a reflection/questions section, enhance with AI-generated verse references
                        if 'reflection' in section_lower or 'questions' in section_lower:
                            content = enhance_questions_with_verses_ai(
                                content, 
                                f"{research_type}: {user_input}", 
                                claude_api_key
                            )
                        
                        st.markdown(content)
                        st.markdown("</div></div>", unsafe_allow_html=True)
            
            # If no clear sections were found, display as-is but in a container
            if not sections:
                with st.container():
                    st.markdown(f"""
                    <div style="
                        border-left: 4px solid #1f77b4;
                        padding: 15px;
                        margin: 10px 0;
                        background-color: rgba(31, 119, 180, 0.1);
                        border-radius: 5px;
                    ">
                    """, unsafe_allow_html=True)
                    st.markdown(result_text)
                    st.markdown("</div>", unsafe_allow_html=True)
            
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
