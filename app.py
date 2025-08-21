# Add these imports to your existing app.py
import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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

def load_bible_word_data():
    """Load Bible word data from local JSON files"""
    try:
        # Load from data/ folder in your repo
        with open('data/greek_words.json', 'r') as f:
            greek_words = json.load(f)
        with open('data/hebrew_words.json', 'r') as f:
            hebrew_words = json.load(f)
        with open('data/word_occurrences.json', 'r') as f:
            word_occurrences = json.load(f)
        
        return greek_words, hebrew_words, word_occurrences
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.error("Please ensure the data/ folder contains: greek_words.json, hebrew_words.json, word_occurrences.json")
        return {}, {}, {}

def create_word_study_interface():
    """Create the word study interface"""
    
    st.subheader("📈 Biblical Word Study")
    st.markdown("*Explore how key biblical words appear throughout Scripture*")
    
    # Load data
    greek_words, hebrew_words, word_occurrences = load_bible_word_data()
    
    if not word_occurrences:
        st.error("Word study data not available. Please check your data files.")
        return
    
    # Word selection dropdown
    available_words = list(word_occurrences.keys())
    
    selected_word = st.selectbox(
        "Select word to study:",
        options=available_words,
        help="Choose a word to see its distribution across Scripture",
        index=0
    )
    
    if selected_word and selected_word in word_occurrences:
        # Get related Greek/Hebrew words for this English word
        word_data = word_occurrences[selected_word]
        
        related_greek = {word: info for word, info in greek_words.items() 
                        if selected_word in info.get('english_words', [])}
        related_hebrew = {word: info for word, info in hebrew_words.items() 
                         if selected_word in info.get('english_words', [])}
        
        # Word selection interface
        st.subheader("🔤 Select Original Language Words")
        
        col1, col2 = st.columns(2)
        
        hebrew_selection = {}
        greek_selection = {}
        
        with col1:
            st.markdown("#### Hebrew Words")
            if related_hebrew:
                for word, info in related_hebrew.items():
                    if word in word_data:  # Only show words that have occurrence data
                        selected = st.checkbox(
                            f"**{word}** ({info['strong']}) - {info['meaning']}", 
                            value=True,
                            key=f"heb_{word}"
                        )
                        hebrew_selection[word] = selected
                if not any(word in word_data for word in related_hebrew.keys()):
                    st.info("No Hebrew occurrence data available for this word")
            else:
                st.info("No Hebrew words found for this term")
        
        with col2:
            st.markdown("#### Greek Words")
            if related_greek:
                for word, info in related_greek.items():
                    if word in word_data:  # Only show words that have occurrence data
                        selected = st.checkbox(
                            f"**{word}** ({info['strong']}) - {info['meaning']}", 
                            value=True,
                            key=f"grk_{word}"
                        )
                        greek_selection[word] = selected
                if not any(word in word_data for word in related_greek.keys()):
                    st.info("No Greek occurrence data available for this word")
            else:
                st.info("No Greek words found for this term")
        
        # Generate visualization
        if st.button("📊 Generate Word Distribution Chart", type="primary"):
            create_word_distribution_visualization(
                selected_word, 
                word_data, 
                hebrew_selection, 
                greek_selection
            )

def create_word_distribution_visualization(word, word_data, hebrew_selection, greek_selection):
    """Create the word distribution visualization"""
    
    # Bible books in order
    bible_books = [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
        "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther",
        "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Songs",
        "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
        "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
        "Matthew", "Mark", "Luke", "John", "Acts",
        "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
        "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon",
        "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
        "Jude", "Revelation"
    ]
    
    # Prepare chart data
    chart_data = []
    total_count = 0
    selected_words = []
    
    # Collect selected words and their data
    for original_word, selected in hebrew_selection.items():
        if selected and original_word in word_data:
            selected_words.append(f"{original_word} (Hebrew)")
            
    for original_word, selected in greek_selection.items():
        if selected and original_word in word_data:
            selected_words.append(f"{original_word} (Greek)")
    
    # Build chart data
    for book in bible_books:
        book_total = 0
        
        # Add selected Hebrew words
        for original_word, selected in hebrew_selection.items():
            if selected and original_word in word_data:
                count = word_data[original_word].get(book, 0)
                book_total += count
        
        # Add selected Greek words
        for original_word, selected in greek_selection.items():
            if selected and original_word in word_data:
                count = word_data[original_word].get(book, 0)
                book_total += count
        
        chart_data.append({
            "book": book,
            "book_index": bible_books.index(book) + 1,
            "total_occurrences": book_total
        })
        total_count += book_total
    
    if total_count > 0:
        st.subheader(f"📊 Distribution of '{word.title()}' Across Scripture")
        
        df = pd.DataFrame(chart_data)
        
        # Create bar chart visualization
        books_with_data = df[df['total_occurrences'] > 0]
        if not books_with_data.empty:
            fig_bar = px.bar(
                books_with_data, 
                x="book", 
                y="total_occurrences",
                title=f"'{word.title()}' Distribution Across Bible Books (Total: {total_count} occurrences)",
                labels={"book": "Bible Books", "total_occurrences": "Occurrences"},
                color="total_occurrences",
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Summary statistics
        create_word_study_summary(chart_data, total_count, selected_words)
        
        # Testament comparison
        create_testament_comparison_chart(chart_data)
        
    else:
        st.warning("No occurrences found for the selected word combinations. Try selecting different Hebrew/Greek words.")

def create_word_study_summary(chart_data, total_count, selected_words):
    """Create summary statistics for word study"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Occurrences", total_count)
    
    with col2:
        books_with_word = len([x for x in chart_data if x["total_occurrences"] > 0])
        st.metric("Books with Word", f"{books_with_word}/66")
    
    with col3:
        if books_with_word > 0:
            avg_per_book = total_count / books_with_word
            st.metric("Avg per Book", f"{avg_per_book:.1f}")
        else:
            st.metric("Avg per Book", "0")
    
    with col4:
        st.metric("Words Analyzed", len(selected_words))
    
    # Detailed breakdown
    if total_count > 0:
        st.subheader("📋 Detailed Book Breakdown")
        detailed_data = [
            {"Book": item["book"], "Occurrences": item["total_occurrences"]}
            for item in chart_data if item["total_occurrences"] > 0
        ]
        
        if detailed_data:
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df = detailed_df.sort_values("Occurrences", ascending=False)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.dataframe(detailed_df, use_container_width=True, hide_index=True)
            with col2:
                # Top 5 books
                top_5 = detailed_df.head(5)
                st.markdown("**Top 5 Books:**")
                for _, row in top_5.iterrows():
                    st.markdown(f"• {row['Book']}: {row['Occurrences']}")

def create_testament_comparison_chart(chart_data):
    """Create Old vs New Testament comparison"""
    
    old_testament_books = set([
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
        "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther",
        "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Songs",
        "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
        "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
        "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"
    ])
    
    ot_total = sum(item["total_occurrences"] for item in chart_data if item["book"] in old_testament_books)
    nt_total = sum(item["total_occurrences"] for item in chart_data if item["book"] not in old_testament_books)
    
    if ot_total > 0 or nt_total > 0:
        st.subheader("📊 Testament Distribution")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart
            testament_df = pd.DataFrame({
                "Testament": ["Old Testament", "New Testament"],
                "Occurrences": [ot_total, nt_total]
            })
            
            fig = px.pie(
                testament_df, 
                values="Occurrences", 
                names="Testament",
                title="OT vs NT Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Metrics
            total = ot_total + nt_total
            if total > 0:
                st.metric("Old Testament", f"{ot_total} ({ot_total/total*100:.1f}%)")
                st.metric("New Testament", f"{nt_total} ({nt_total/total*100:.1f}%)")
                
                if ot_total > 0 and nt_total > 0:
                    ratio = ot_total / nt_total
                    st.metric("OT:NT Ratio", f"{ratio:.1f}:1")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0

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
            # No user input needed for Word Study - it has its own interface
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
        # Handle Word Study differently
        if research_type == "Word Study":
            create_word_study_interface()
        else:
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
            
            # Only show this message if no results for non-Word Study types
            if not st.session_state.results:
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
