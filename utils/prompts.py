def get_research_prompt(research_type: str, user_input: str, depth_level: str, include_greek_hebrew: bool) -> str:
    """Generate appropriate prompt based on research type and parameters"""
    
    # Base prompt components
    depth_instruction = {
        "Basic": "Provide clear, accessible insights suitable for general Bible study.",
        "Intermediate": "Include moderate theological depth with some technical terms explained.",
        "Deep Theological": "Provide thorough theological analysis with detailed cross-references and doctrinal implications."
    }
    
    greek_hebrew_addon = """
    
    IMPORTANT: Include a dedicated "GREEK/HEBREW INSIGHTS" section with:
    - Key original language words with transliterations (e.g., Greek: agape, Hebrew: hesed)
    - Meaning and nuance of original words that may be lost in translation
    - How these words are used in other significant Bible passages
    - Theological significance of the original language choices
    - Practical implications for understanding and application
    - Suggestions for further word study using tools like Strong's Concordance or Blue Letter Bible
    
    Format this as a clear, separate section that helps users understand the richness of the original languages.
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
        {greek_hebrew_addon}
        
        {depth_instruction[depth_level]}
        
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
        1. MAIN VERSE: The verse in context (ESV)
        2. KEY CROSS-REFERENCES: 5-7 key cross-references with brief explanations
        3. THEMATIC CONNECTIONS: How these passages relate thematically
        4. REFLECTION QUESTIONS: Questions about connections with verse references for deeper study
        5. SUGGESTED STUDY PATH: Recommended order for studying the references
        6. THEOLOGICAL THEMES: Key themes that emerge across the passages
        
        {depth_instruction[depth_level]}
        {greek_hebrew_addon}
        
        Help the reader see the interconnected nature of Scripture. Include verse references with all reflection questions.
        """

def get_verse_enhancement_prompt(content: str, research_context: str) -> str:
    """Generate prompt for AI to enhance questions with relevant Bible verse references"""
    return f"""
    Please enhance the following biblical study content by adding specific, relevant Bible verse references to any questions that don't already have them.

    INSTRUCTIONS:
    - Look for questions in the content that would benefit from specific Bible verse references
    - Add verse references in this format: "Question? (See [specific verse references] for insights)"
    - Only suggest verses that are directly relevant and helpful for answering the specific question
    - Ensure all verse references are accurate and from a conservative theological perspective
    - Don't change questions that already have verse references
    - Focus on well-known, clear passages that address the question topic

    RESEARCH CONTEXT: {research_context}

    CONTENT TO ENHANCE:
    {content}

    Please return the enhanced content with appropriate verse references added to questions.
    """
