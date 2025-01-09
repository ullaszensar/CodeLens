import streamlit as st
import plotly.graph_objects as go
from complexity import generate_complexity_heatmap, calculate_file_complexity, display_complexity_metrics
from utils import create_file_tree
from ai_suggestions import get_ai_suggestions
import os

def show_complexity_analysis(repo_path: str):
    """Display the code complexity analysis tab content"""
    st.header("Code Complexity Analysis")

    # Create sub-tabs for different analysis views
    complexity_tab, suggestions_tab = st.tabs(["Complexity Metrics", "AI Suggestions"])

    with complexity_tab:
        # Generate and display enhanced complexity heat map
        heatmap = generate_complexity_heatmap(
            repo_path,
            ['.py', '.java', '.js', '.ts', '.cs', '.php', '.rb', '.xsd']
        )

        if heatmap:
            # Add interactive features to heatmap
            heatmap.update_traces(
                hoverongaps=False,
                hovertemplate="<b>File:</b> %{x}<br>" +
                             "<b>Complexity Score:</b> %{z}<br>" +
                             "<b>Click for details</b><extra></extra>"
            )

            # Display the heatmap
            st.plotly_chart(heatmap, use_container_width=True)

            # Add interactive file analysis
            st.subheader("File-specific Analysis")

            # Get all analyzable files
            files = []
            for root, _, filenames in os.walk(repo_path):
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in ['.py', '.java', '.js', '.ts', '.cs', '.php', '.rb']):
                        files.append(os.path.join(root, filename))

            if files:
                selected_file = st.selectbox(
                    "Select a file to analyze",
                    files,
                    format_func=lambda x: os.path.relpath(x, repo_path)
                )

                if selected_file:
                    metrics = calculate_file_complexity(selected_file)
                    if metrics:
                        st.markdown("### Detailed Metrics")

                        # Create metrics display
                        cols = st.columns(5)
                        cols[0].metric("Cyclomatic Complexity", metrics['cyclomatic_complexity'])
                        cols[1].metric("Lines of Code", metrics['loc'])
                        cols[2].metric("Logical Lines", metrics['lloc'])
                        cols[3].metric("Functions", metrics['functions'])
                        cols[4].metric("Complexity Grade", metrics['complexity_rank'])

                        # Add complexity trend visualization
                        st.markdown("### Complexity Distribution")
                        fig = go.Figure()

                        # Add cyclomatic complexity bar
                        fig.add_trace(go.Bar(
                            name='Cyclomatic Complexity',
                            x=['Complexity Score'],
                            y=[metrics['cyclomatic_complexity']],
                            marker_color='#FF4B4B'
                        ))

                        # Add reference lines for complexity thresholds
                        for threshold, grade in [(5, 'A'), (10, 'B'), (20, 'C'), (30, 'D'), (40, 'E')]:
                            fig.add_hline(
                                y=threshold,
                                line_dash="dash",
                                annotation_text=f"Grade {grade} Threshold",
                                line_color="gray"
                            )

                        fig.update_layout(
                            title="Cyclomatic Complexity Score",
                            showlegend=False,
                            height=400
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Add explanation
                        with st.expander("Understanding Complexity Metrics"):
                            st.markdown("""
                            ### Complexity Metrics Explained

                            - **Cyclomatic Complexity**: Measures the number of linearly independent paths through the code. Lower is better.
                              - Grade A (1-5): Simple, well-structured code
                              - Grade B (6-10): Moderately complex code
                              - Grade C (11-20): Complex code that may need attention
                              - Grade D (21-30): Very complex code that needs refactoring
                              - Grade E (31-40): Extremely complex code
                              - Grade F (>40): Code that requires immediate attention

                            - **Lines of Code (LOC)**: Total number of lines in the file
                            - **Logical Lines (LLOC)**: Number of executable statements
                            - **Functions**: Total number of functions/methods
                            """)

    with suggestions_tab:
        st.header("AI-Powered Code Suggestions")

        if files:
            selected_file = st.selectbox(
                "Select a file for AI analysis",
                files,
                format_func=lambda x: os.path.relpath(x, repo_path),
                key="ai_analysis_file"
            )

            if selected_file:
                get_ai_suggestions(selected_file)

        # File structure view
        st.subheader("Repository Structure")
        create_file_tree(repo_path)