import radon.complexity as cc
import radon.metrics as rm
from radon.visitors import ComplexityVisitor
import plotly.graph_objects as go
import streamlit as st
import os
from typing import Dict, List, Tuple, Optional

def calculate_file_complexity(file_path: str) -> Optional[Dict]:
    """Calculate complexity metrics for a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Calculate complexity metrics
        complexity_score = ComplexityVisitor.from_code(content)
        raw_metrics = rm.raw_metrics(content)

        cyclomatic_complexity = sum(item.complexity for item in complexity_score.functions)

        return {
            'cyclomatic_complexity': cyclomatic_complexity,
            'loc': raw_metrics.loc,
            'lloc': raw_metrics.lloc,
            'functions': len(complexity_score.functions),
            'complexity_rank': get_complexity_rank(cyclomatic_complexity)
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

def get_complexity_color(rank: str) -> str:
    """Get color for complexity rank"""
    colors = {
        'A': '#00FF00',  # Bright Green
        'B': '#FFFF00',  # Yellow
        'C': '#FFA500',  # Orange
        'D': '#FF4444',  # Light Red
        'E': '#FF0000',  # Red
        'F': '#8B0000'   # Dark Red
    }
    return colors.get(rank, '#FF0000')

def generate_complexity_heatmap(repo_path: str, file_extensions: List[str]) -> Optional[go.Figure]:
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

    # Prepare custom data for hover information
    customdata = [
        [
            item['metrics']['complexity_rank'],
            item['metrics']['functions'],
            item['metrics']['loc']
        ]
        for item in complexity_data
    ]

    # Create enhanced heat map with better interactivity
    fig = go.Figure(data=go.Heatmap(
        z=[complexities],
        y=['Complexity'],
        x=files,
        colorscale=[
            [0, '#00FF00'],      # Green for low complexity
            [0.2, '#90EE90'],    # Light green
            [0.4, '#FFFF00'],    # Yellow
            [0.6, '#FFA500'],    # Orange
            [0.8, '#FF0000'],    # Red
            [1, '#8B0000']       # Dark red
        ],
        showscale=True,
        customdata=[customdata],
        hoverongaps=False
    ))

    # Enhanced layout with better interactivity
    fig.update_layout(
        title={
            'text': 'Code Complexity Heat Map',
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
    cols[0].metric(
        "Cyclomatic Complexity",
        metrics['cyclomatic_complexity'],
        help="Measures the number of linearly independent paths through the code"
    )
    cols[1].metric(
        "Lines of Code",
        metrics['loc'],
        help="Total number of lines including comments and blank lines"
    )
    cols[2].metric(
        "Logical Lines",
        metrics['lloc'],
        help="Number of executable statements"
    )
    cols[3].metric(
        "Functions",
        metrics['functions'],
        help="Total number of functions/methods in the file"
    )

    # Display complexity rank with color coding
    rank_color = get_complexity_color(metrics['complexity_rank'])
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 5px; margin: 10px 0;">
            <h3 style="color: {rank_color};">Complexity Rank: {metrics['complexity_rank']}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )