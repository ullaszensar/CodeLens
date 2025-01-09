import streamlit as st
import plotly.graph_objects as go
from complexity import generate_complexity_heatmap, calculate_file_complexity, display_complexity_metrics
from utils import create_file_tree, display_code_with_highlights
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
                hovertemplate=(
                    "<b>File:</b> %{x}<br>" +
                    "<b>Complexity Score:</b> %{z}<br>" +
                    "<b>Grade:</b> %{customdata[0]}<br>" +
                    "<b>Functions:</b> %{customdata[1]}<br>" +
                    "<b>Lines of Code:</b> %{customdata[2]}<br>" +
                    "<b>Click for details</b><extra></extra>"
                )
            )

            # Enhanced layout with better interactivity
            heatmap.update_layout(
                title={
                    'text': 'Interactive Code Complexity Heat Map',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 24}
                },
                margin=dict(t=100, l=50, r=50, b=120),
                xaxis={
                    'tickangle': 45,
                    'tickfont': {'size': 10},
                    'title': 'Source Files',
                    'showgrid': False
                },
                yaxis={
                    'title': 'Complexity Level',
                    'showgrid': False
                }
            )

            # Add legend for complexity grades
            legend_html = """
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <h4>Complexity Grade Legend</h4>
                <p>🟢 Grade A (1-5): Simple, well-structured code</p>
                <p>🟡 Grade B (6-10): Moderately complex code</p>
                <p>🟠 Grade C (11-20): Complex code that needs attention</p>
                <p>🔴 Grade D (21-30): Very complex code that needs refactoring</p>
                <p>⚫ Grade F (>30): Critical complexity, immediate attention required</p>
            </div>
            """
            st.markdown(legend_html, unsafe_allow_html=True)

            # Display the interactive heatmap
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
                        # File content preview
                        with st.expander("View File Content", expanded=False):
                            try:
                                with open(selected_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    display_code_with_highlights(content, 1)
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")

                        st.markdown("### Detailed Metrics")

                        # Enhanced metrics display with descriptions
                        cols = st.columns(5)
                        cols[0].metric("Cyclomatic Complexity", metrics['cyclomatic_complexity'])
                        cols[1].metric("Lines of Code", metrics['loc'])
                        cols[2].metric("Logical Lines", metrics['lloc'])
                        cols[3].metric("Functions", metrics['functions'])
                        cols[4].metric("Complexity Grade", metrics['complexity_rank'])

                        # Interactive complexity visualization
                        st.markdown("### Complexity Distribution")
                        fig = go.Figure()

                        # Enhanced bar chart
                        fig.add_trace(go.Bar(
                            name='Cyclomatic Complexity',
                            x=['Complexity Score'],
                            y=[metrics['cyclomatic_complexity']],
                            marker_color='#FF4B4B',
                            hovertemplate="Complexity Score: %{y}<extra></extra>"
                        ))

                        # Add reference lines with enhanced styling
                        for threshold, grade, color in [
                            (5, 'A', 'green'),
                            (10, 'B', 'yellow'),
                            (20, 'C', 'orange'),
                            (30, 'D', 'red'),
                            (40, 'E', 'darkred')
                        ]:
                            fig.add_hline(
                                y=threshold,
                                line_dash="dash",
                                annotation_text=f"Grade {grade} Threshold",
                                line_color=color,
                                opacity=0.5
                            )

                        fig.update_layout(
                            title={
                                'text': "Cyclomatic Complexity Score",
                                'y': 0.95,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top'
                            },
                            showlegend=False,
                            height=400,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(t=50, l=50, r=50, b=50)
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Expanded metrics explanation
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
                              - Includes comments and blank lines
                              - High LOC might indicate need for file splitting

                            - **Logical Lines (LLOC)**: Number of executable statements
                              - More accurate measure of code size
                              - Excludes comments and blank lines

                            - **Functions**: Total number of functions/methods
                              - High number might indicate need for better organization
                              - Consider splitting into multiple files if too high
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