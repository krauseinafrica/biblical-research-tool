import streamlit as st
import os
try:
    from utils.claude_client import ClaudeClient
    from utils.prompts import get_research_prompt
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Biblical Research Tool",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'claude_client' not in st.session_state:
    # Initialize Claude client (will handle API key setup)
    st.session_state.claude_client = ClaudeClient()

def main():
    st.title("📖 Biblical Research Tool")
    st.markdown("*A resource for deeper theological understanding and personal study*")
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input (for initial setup)
        claude_api_key = st.text_input(
            "Claude API Key", 
            type="password",
            help="Enter your Anthropic Claude API key"
        )
        
        if claude_api_key:
            st.session_state.claude_client.set_api_key(claude_api_key)
            st.success("✅ Claude API key configured")
        
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
                        result = st.session_state.claude_client.generate_research(prompt)
                        st.session_state.results = result
                        
                    except Exception as e:
                        st.error(f"Error generating research: {str(e)}")
            else:
                if not user_input:
                    st.warning("Please enter your research topic or verse.")
                if not claude_api_key:
                    st.warning("Please enter your Claude API key in the sidebar.")
    
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
                if refinement:
                    with st.spinner("Refining research..."):
                        try:
                            refined_prompt = f"""
                            Based on the previous research, please expand on this specific aspect:
                            {refinement}
                            
                            Previous research context:
                            {st.session_state.results[:500]}...
                            """
                            
                            refined_result = st.session_state.claude_client.generate_research(refined_prompt)
                            st.markdown("### Refined Analysis:")
                            st.markdown(refined_result)
                            
                        except Exception as e:
                            st.error(f"Error refining research: {str(e)}")
        else:
            st.info("👈 Select a research type and enter your topic or verse to begin.")

if __name__ == "__main__":
    main()
