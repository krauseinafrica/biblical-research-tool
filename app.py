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


parse_and_display_json_results(json_text: str):
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
            if key == 'title' or key == 'cross_reference_keywords':
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
            create_word_study_interface()
        else:
            st.header("Research Results")
            
            if st.session_state.results:
                # Parse and display JSON results
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
                
                # Refinement section
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

