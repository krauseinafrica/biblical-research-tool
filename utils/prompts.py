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
