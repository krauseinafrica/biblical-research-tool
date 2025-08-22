def get_research_prompt(research_type: str, user_input: str, depth_level: str, include_greek_hebrew: bool) -> str:
    """Generate appropriate prompt based on research type and parameters"""
    
    # Base prompt components
    depth_instruction = {
        "Basic": "Provide clear, accessible insights suitable for general Bible study.",
        "Intermediate": "Include moderate theological depth with some technical terms explained.",
        "Deep Theological": "Provide thorough theological analysis with detailed cross-references and doctrinal implications."
    }
    
    greek_hebrew_section = """
        "greek_hebrew_insights": {
            "key_words": [
                {
                    "original": "original word",
                    "transliteration": "pronunciation",
                    "meaning": "detailed meaning",
                    "usage_examples": ["verse reference 1", "verse reference 2"],
                    "theological_significance": "why this matters"
                }
            ],
            "study_resources": ["Strong's Concordance", "Blue Letter Bible", "specific recommendations"]
        },""" if include_greek_hebrew else ""
    
    # Research type specific prompts
    if research_type == "Topical Study":
        return f"""
        Conduct a topical Bible study on: {user_input}
        
        {depth_instruction[depth_level]}
        
        Please respond with ONLY valid JSON in this exact format:
        
        {{
            "title": "TOPICAL BIBLE STUDY: {user_input.upper()}",
            "key_verses": [
                {{
                    "reference": "Book Chapter:Verse",
                    "text": "Full verse text (ESV)",
                    "context": "Brief context explanation"
                }}
            ],
            "connections": [
                "Connection point 1 between verses",
                "Connection point 2 between themes"
            ],
            "reflection_questions": [
                {{
                    "question": "Thoughtful question text?",
                    "verse_references": ["Reference 1", "Reference 2"],
                    "study_note": "See [references] for insights"
                }}
            ],
            "practical_application": [
                {{
                    "principle": "Application principle",
                    "supporting_verses": ["Reference 1", "Reference 2"],
                    "action_step": "Specific action to take"
                }}
            ],{greek_hebrew_section}
            "additional_study": [
                {{
                    "reference": "Verse reference",
                    "reason": "Why this verse is relevant for further study"
                }}
            ],
            "cross_reference_keywords": [
                "keyword1",
                "keyword2", 
                "keyword3",
                "keyword4"
            ]
        }}
        
        IMPORTANT: 
        - Return ONLY the JSON, no other text
        - Ensure all JSON is valid and properly formatted
        - Include all required sections
        - Each reflection question must include specific verse references
        - cross_reference_keywords should be 3-5 key theological words for Scripture lookup
        """
    
    elif research_type == "Verse Analysis":
        return f"""
        Provide a detailed analysis of: {user_input}
        
        {depth_instruction[depth_level]}
        
        Please respond with ONLY valid JSON in this exact format:
        
        {{
            "title": "VERSE ANALYSIS: {user_input}",
            "verse_context": {{
                "main_verse": "Full verse text (ESV)",
                "surrounding_context": "Context explanation",
                "book_chapter_context": "Broader context within the book"
            }},
            "historical_background": {{
                "time_period": "When this was written",
                "cultural_context": "Cultural background",
                "audience": "Original audience"
            }},
            "theological_themes": [
                {{
                    "theme": "Major theological theme",
                    "explanation": "How this verse relates to the theme",
                    "related_verses": ["Reference 1", "Reference 2"]
                }}
            ],
            "cross_references": [
                {{
                    "reference": "Related verse reference",
                    "connection": "How it connects to the main verse",
                    "explanation": "Why this connection matters"
                }}
            ],
            "reflection_questions": [
                {{
                    "question": "Personal study question?",
                    "verse_references": ["Reference 1", "Reference 2"],
                    "study_note": "See [references] for insights"
                }}
            ],{greek_hebrew_section}
            "application_principles": [
                {{
                    "principle": "How to apply this today",
                    "supporting_verses": ["Reference 1"],
                    "practical_steps": ["Specific action 1", "Specific action 2"]
                }}
            ],
            "cross_reference_keywords": [
                "keyword1",
                "keyword2", 
                "keyword3",
                "keyword4"
            ]
        }}
        
        IMPORTANT: 
        - Return ONLY the JSON, no other text
        - cross_reference_keywords should be 3-5 key words from this verse for Scripture-wide lookup
        """
    
    elif research_type == "Study Guide Builder":
        return f"""
        Create a study guide for: {user_input}
        
        {depth_instruction[depth_level]}
        
        Please respond with ONLY valid JSON in this exact format:
        
        {{
            "title": "STUDY GUIDE: {user_input}",
            "opening_questions": [
                {{
                    "question": "Engaging opening question?",
                    "purpose": "Why this question matters"
                }}
            ],
            "observation_questions": [
                {{
                    "question": "What does the text say?",
                    "verse_references": ["Reference 1"],
                    "focus": "What to look for"
                }}
            ],
            "interpretation_questions": [
                {{
                    "question": "What does it mean?",
                    "verse_references": ["Reference 1", "Reference 2"],
                    "study_note": "See [references] for insights"
                }}
            ],
            "application_questions": [
                {{
                    "question": "How should I respond?",
                    "verse_references": ["Reference 1"],
                    "guidance": "Practical guidance"
                }}
            ],
            "cross_references": [
                {{
                    "reference": "Related passage",
                    "explanation": "How it connects"
                }}
            ],{greek_hebrew_section}
            "discussion_questions": [
                {{
                    "question": "Group discussion question?",
                    "verse_references": ["Reference 1"],
                    "discussion_points": ["Point 1", "Point 2"]
                }}
            ],
            "prayer_points": [
                "Prayer topic based on the passage",
                "Another prayer focus"
            ],
            "cross_reference_keywords": [
                "keyword1",
                "keyword2", 
                "keyword3"
            ]
        }}
        
        IMPORTANT: 
        - Return ONLY the JSON, no other text
        - cross_reference_keywords should be 3-5 key words for broader Scripture study
        """
    
    else:  # Cross-Reference Explorer
        return f"""
        Explore cross-references for: {user_input}
        
        {depth_instruction[depth_level]}
        
        Please respond with ONLY valid JSON in this exact format:
        
        {{
            "title": "CROSS-REFERENCE STUDY: {user_input}",
            "main_verse": {{
                "reference": "{user_input}",
                "text": "Full verse text (ESV)",
                "context": "Brief context"
            }},
            "key_cross_references": [
                {{
                    "reference": "Related verse reference",
                    "text": "Verse text (ESV)",
                    "connection_type": "thematic/verbal/conceptual",
                    "explanation": "How it connects to main verse"
                }}
            ],
            "thematic_connections": [
                {{
                    "theme": "Connecting theme",
                    "verses": ["Reference 1", "Reference 2"],
                    "explanation": "How these verses develop the theme"
                }}
            ],
            "reflection_questions": [
                {{
                    "question": "How do these passages relate?",
                    "verse_references": ["Reference 1", "Reference 2"],
                    "study_note": "See [references] for insights"
                }}
            ],{greek_hebrew_section}
            "suggested_study_path": [
                {{
                    "step": 1,
                    "reference": "First verse to study",
                    "focus": "What to focus on"
                }}
            ],
            "theological_themes": [
                {{
                    "theme": "Major theme",
                    "verses": ["Reference 1", "Reference 2"],
                    "significance": "Why this theme matters"
                }}
            ],
            "cross_reference_keywords": [
                "keyword1",
                "keyword2", 
                "keyword3"
            ]
        }}
        
        IMPORTANT: 
        - Return ONLY the JSON, no other text
        - cross_reference_keywords should be 3-5 key words for expanded cross-reference lookup
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
def get_system_message() -> str:
    """Get the consistent system message for all biblical research"""
    return """
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
    
def get_enhanced_research_prompt(research_type: str, user_input: str, depth_level: str, include_greek_hebrew: bool) -> str:
    """Enhanced research prompt that identifies key words for API lookup"""
    
    # Your existing prompt logic, but add this instruction to ALL prompts:
    api_instruction = """
    
    IMPORTANT: At the end of your response, include a section called "KEY WORDS FOR CROSS-REFERENCE" 
    that lists 3-5 key theological or thematic words from this study that would be valuable 
    to search for throughout Scripture. Format as: KEY WORDS: word1, word2, word3, word4
    """
    
    # Add api_instruction to all your existing prompts
    if research_type == "Topical Study":
        return f"""
        Conduct a topical Bible study on: {user_input}
        
        Please provide clearly formatted sections:
        1. KEY BIBLE VERSES: List relevant verses with full text (ESV)
        2. CONTEXT: Brief context for each key verse
        3. CONNECTIONS: How these verses connect to each other thematically
        4. REFLECTION QUESTIONS: Thoughtful questions with specific Bible verse references
        5. PRACTICAL APPLICATION: Concrete application points with supporting verses
        6. ADDITIONAL VERSES FOR STUDY: Suggested verses for deeper exploration
        
        {depth_level} - Provide clear, accessible insights suitable for general Bible study.
        {api_instruction}
        """
    
    elif research_type == "Verse Analysis":
        return f"""
        Provide a detailed analysis of: {user_input}
        
        Please include clearly formatted sections:
        1. VERSE IN CONTEXT: The verse(s) with surrounding context (ESV)
        2. HISTORICAL BACKGROUND: Historical and cultural background
        3. THEOLOGICAL THEMES: Key theological themes and doctrines
        4. CROSS-REFERENCES: Related passages with explanations
        5. REFLECTION QUESTIONS: Personal study questions with verse references
        6. APPLICATION PRINCIPLES: How to apply this passage today
        
        {depth_level} - Provide clear, accessible insights suitable for general Bible study.
        {api_instruction}
        """
    
    # Continue with other research types...
    return "Enhanced prompt with API integration"


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
