"""
YouTube Music Popularity Visualization

This script creates a dual-axis bar plot comparing daily views and total votes
for popular YouTube songs using Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the input data."""
    required_columns = {'Title', 'view per day', 'Total', 'Year'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Data must contain these columns: {required_columns}")
    
    # Filter and clean data
    df = df[df['Year'] == 2024].copy()
    
    # Only keep rows where both 'view per day' and 'Total' are non-null and greater than 0
    df = df[
        df['view per day'].notna() & 
        df['Total'].notna() & 
        (df['view per day'] > 0) & 
        (df['Total'] > 0)
    ]
    
    df = df.sort_values('view per day', ascending=False)
    
    logger.info(f"Number of songs with complete data: {len(df)}")
    logger.info("Songs included in analysis:")
    logger.info(df['Title'].tolist())
    
    return df

def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the data to percentages relative to the song with highest views per day."""
    # Get reference values from song with highest views per day
    reference_song = df.loc[df['view per day'].idxmax()]
    reference_views = reference_song['view per day']
    reference_votes = reference_song['Total']
    
    logger.info(f"Reference views per day: {reference_views:,.0f}")
    logger.info(f"Reference total votes: {reference_votes:,.0f}")
    
    # Normalize to percentages relative to the reference song
    df['normalized_views'] = (df['view per day'] / reference_views) * 100
    df['normalized_votes'] = (df['Total'] / reference_votes) * 100
    
    # Calculate difference between proportions
    df['proportion_difference'] = df['normalized_views'] - df['normalized_votes']
    
    return df

def create_dual_axis_plot(df: pd.DataFrame, output_path: Optional[str] = None) -> go.Figure:
    """
    Create a plot comparing normalized views per day and total votes using Plotly.
    
    Args:
        df: DataFrame containing song data
        output_path: Optional path to save the plot
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        # Validate and prepare data
        df = validate_data(df)
        df = normalize_data(df)
        
        # Create figure
        fig = go.Figure()
        
        # Add views bars
        fig.add_trace(go.Bar(
            name='MV 每日觀看次數',
            x=df['Title'],
            y=df['normalized_views'],
            text=df['normalized_views'].round(0).astype(str) + '%',
            textposition='outside',
            marker_color='#1f77b4',
            opacity=0.8,
            offsetgroup=0,
            hovertemplate='Views per day: %{customdata:,.0f}<extra></extra>',
            customdata=df['view per day']
        ))
        
        # Add votes bars
        fig.add_trace(go.Bar(
            name='Total Votes (Normalized)',
            x=df['Title'],
            y=df['normalized_votes'],
            text=df['normalized_votes'].round(0).astype(str) + '%',
            textposition='outside',
            marker_color='#d62728',
            opacity=0.8,
            offsetgroup=1,
            hovertemplate='叱吒場內總票數: %{customdata:,.0f}<extra></extra>',
            customdata=df['Total']
        ))
        
        # Add difference annotations for all songs
        for i, row in df.iterrows():
            # Determine colors based on difference magnitude
            if row['proportion_difference'] > 0:
                color = '#2ecc71' if abs(row['proportion_difference']) > 10 else '#27ae60'  # Bright/dark green
            else:
                color = '#e74c3c' if abs(row['proportion_difference']) > 10 else '#c0392b'  # Bright/dark red
                
            fig.add_annotation(
                x=row['Title'],
                y=max(row['normalized_views'], row['normalized_votes']) + 2,
                text=f"Δ{row['proportion_difference']:+.0f}%",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color,
                font=dict(
                    color=color,
                    size=12,
                    weight='bold'
                ),
                bordercolor=color,
                borderwidth=2,
                borderpad=4,
                bgcolor='white',
                opacity=0.9
            )
        
        # Update layout
        fig.update_layout(
            title='叱咤 903 我最喜愛歌曲票數比例 與 YouTube MV 觀看次數比例',
            xaxis_title='歌曲',
            yaxis_title='標準化值',
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            xaxis=dict(
                tickangle=45
            ),
            yaxis=dict(
                ticksuffix='%'
            ),
            plot_bgcolor='#f7f7f7',
            width=1000,
            height=600
        )
        
        # Save if path provided
        if output_path:
            fig.write_image(output_path)
            logger.info(f"Plot saved to {output_path}")
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}")
        raise
