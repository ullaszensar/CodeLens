import os
from openai import OpenAI
import streamlit as st

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

client = OpenAI()

def analyze_code_quality(code: str, file_path: str) -> dict:
    """
    Analyze code quality and provide improvement suggestions using OpenAI
    """
    try:
        # Prepare the prompt for code analysis
        prompt = f"""Analyze the following code and provide specific improvement suggestions.
        Focus on:
        1. Code complexity and readability
        2. Best practices and design patterns
        3. Performance optimizations
        4. Security considerations
        5. Error handling
        
        Provide the response in JSON format with the following structure:
        {{
            "suggestions": [
                {{
                    "category": "category_name",
                    "issue": "description of the issue",
                    "suggestion": "specific improvement suggestion",
                    "priority": "high|medium|low"
                }}
            ]
        }}

        Code to analyze ({file_path}):
        {code}
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer focusing on code quality, security, and best practices."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Error analyzing code: {str(e)}")
        return {
            "suggestions": [
                {
                    "category": "error",
                    "issue": "Failed to analyze code",
                    "suggestion": str(e),
                    "priority": "high"
                }
            ]
        }

def display_suggestions(suggestions: list, file_path: str):
    """
    Display code improvement suggestions in a structured format
    """
    st.subheader(f"Code Analysis Results for {os.path.basename(file_path)}")
    
    # Group suggestions by priority
    priority_groups = {
        "high": [],
        "medium": [],
        "low": []
    }
    
    for suggestion in suggestions:
        priority_groups[suggestion["priority"]].append(suggestion)
    
    # Display suggestions by priority
    priority_colors = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }
    
    for priority in ["high", "medium", "low"]:
        if priority_groups[priority]:
            with st.expander(f"{priority_colors[priority]} {priority.title()} Priority Suggestions"):
                for suggestion in priority_groups[priority]:
                    st.markdown(f"""
                    **Category:** {suggestion['category']}
                    
                    **Issue:** {suggestion['issue']}
                    
                    **Suggestion:** {suggestion['suggestion']}
                    """)
                    st.divider()

def get_ai_suggestions(file_path: str) -> None:
    """
    Get AI-powered suggestions for code improvements
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        with st.spinner("Analyzing code with AI..."):
            analysis_result = analyze_code_quality(code, file_path)
            display_suggestions(analysis_result["suggestions"], file_path)
            
    except Exception as e:
        st.error(f"Error processing file {file_path}: {str(e)}")
