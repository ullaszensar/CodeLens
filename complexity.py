import radon.complexity as cc
import radon.metrics as rm
from radon.visitors import ComplexityVisitor
import plotly.graph_objects as go
import streamlit as st
import os
from typing import Dict, List, Tuple

def calculate_file_complexity(file_path: str) -> Dict:
    """Calculate complexity metrics for a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Calculate complexity metrics
        complexity_score = ComplexityVisitor.from_code(content)
        raw_metrics = rm.raw_metrics(content)
        
        return {
            'cyclomatic_complexity': sum(item.complexity for item in complexity_score.functions),
            'loc': raw_metrics.loc,
            'lloc': raw_metrics.lloc,
            'functions': len(complexity_score.functions),
            'complexity_rank': get_complexity_rank(sum(item.complexity for item in complexity_score.functions))
        }
    except Exception as e:
        st.error(f"Error analyzing {file_path}: {str(e)}")
        return None

def get_complexity_rank(complexity: int) -> str:
    """Convert complexity score to rank (A-F)"""
    if complexity <= 5:
        return 'A'
    elif complexity <= 10:
        return 'B'
    elif complexity <= 20:
        return 'C'
    elif complexity <= 30:
        return 'D'
    elif complexity <= 40:
        return 'E'
    else:
        return 'F'

def generate_complexity_heatmap(repo_path: str, file_extensions: List[str]) -> go.Figure:
    """Generate an interactive heat map visualization of code complexity"""
    complexity_data = []
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                metrics = calculate_file_complexity(file_path)
                if metrics:
                    complexity_data.append({
                        'file': relative_path,
                        'metrics': metrics
                    })
    
    if not complexity_data:
        return None
        
    # Prepare data for visualization
    files = [item['file'] for item in complexity_data]
    complexities = [item['metrics']['cyclomatic_complexity'] for item in complexity_data]
    
    # Create detailed hover text
    hover_text = []
    for item in complexity_data:
        metrics = item['metrics']
        hover_text.append(
            f"File: {item['file']}<br>" +
            f"Cyclomatic Complexity: {metrics['cyclomatic_complexity']}<br>" +
            f"Complexity Rank: {metrics['complexity_rank']}<br>" +
            f"Lines of Code: {metrics['loc']}<br>" +
            f"Logical Lines: {metrics['lloc']}<br>" +
            f"Functions: {metrics['functions']}"
        )
    
    # Create heat map with enhanced interactivity
    fig = go.Figure(data=go.Heatmap(
        z=[complexities],
        y=['Complexity'],
        x=files,
        colorscale=[
            [0, 'rgb(0, 255, 0)'],      # Green for low complexity
            [0.4, 'rgb(255, 255, 0)'],   # Yellow for medium complexity
            [0.7, 'rgb(255, 165, 0)'],   # Orange for high complexity
            [1, 'rgb(255, 0, 0)']        # Red for very high complexity
        ],
        showscale=True,
        text=[[hover_text[i] for i in range(len(complexities))]],
        hoverongaps=False,
        hoverinfo='text'
    ))
    
    # Enhanced layout with better interactivity
    fig.update_layout(
        title={
            'text': 'Interactive Code Complexity Heat Map',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title='Source Files',
        yaxis_title='Complexity Level',
        height=500,
        margin=dict(t=100, l=50, r=50, b=120),
        xaxis={
            'tickangle': 45,
            'tickfont': {'size': 10},
            'showgrid': False
        },
        yaxis={
            'showgrid': False
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def display_complexity_metrics(metrics: Dict):
    """Display complexity metrics in a formatted way"""
    st.write("### Complexity Metrics")
    
    cols = st.columns(4)
    cols[0].metric("Cyclomatic Complexity", metrics['cyclomatic_complexity'])
    cols[1].metric("Lines of Code", metrics['loc'])
    cols[2].metric("Logical Lines", metrics['lloc'])
    cols[3].metric("Functions", metrics['functions'])
    
    st.write(f"**Complexity Rank:** {metrics['complexity_rank']}")
