"""
YouTube Music Popularity Visualization

This script creates a dual-axis bar plot comparing daily views and total votes
for popular YouTube songs. It includes advanced visualization features and
data validation.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Visualization settings
COLORS = {
    'views': '#1f77b4',  # Muted blue
    'votes': '#d62728',  # Brick red
    'background': '#f7f7f7',
    'grid': '#dddddd'
}

# Set style and font for CJK characters with robust fallbacks
sns.set_theme(style="whitegrid", rc={
    'axes.facecolor': COLORS['background'],
    'grid.color': COLORS['grid']
})
plt.rcParams['font.family'] = ['Hiragino Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Arial Unicode MS', 'sans-serif']

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
    """Normalize the data to percentages relative to 'Hey Hey OK OK'."""
    # Get reference values from 'Hey Hey OK OK'
    reference_song = df[df['Title'] == '《Hey Hey OK!》'].iloc[0]
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

def create_dual_axis_plot(df: pd.DataFrame, output_path: Optional[str] = 'plot.png') -> None:
    """
    Create a plot comparing normalized views per day and total votes.
    
    Args:
        df: DataFrame containing song data
        output_path: Optional path to save the plot (default: 'plot.png')
    """
    try:
        # Validate and prepare data
        df = validate_data(df)
        df = normalize_data(df)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Set positions and width
        x = range(len(df))
        width = 0.35
        
        # Plot normalized views per day and total votes
        views_bars = ax.bar(
            [i - width/2 for i in x], df['normalized_views'],
            width, color=COLORS['views'], alpha=0.8, label='Views/Day (Normalized)'
        )
        
        votes_bars = ax.bar(
            [i + width/2 for i in x], df['normalized_votes'],
            width, color=COLORS['votes'], alpha=0.8, label='Total Votes (Normalized)'
        )
        
        # Configure axis
        ax.set_xlabel('Songs', fontsize=12, labelpad=15)
        ax.set_ylabel('Normalized Values', fontsize=12)
        
        # Format y-axis to show percentages (without multiplying by 100)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Add value labels
        for bar in views_bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}%', ha='center', va='bottom',
                   fontsize=8, color=COLORS['views'])
        
        for bar in votes_bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}%', ha='center', va='bottom',
                   fontsize=8, color=COLORS['votes'])
        
        # Configure x-axis
        plt.xticks(x, df['Title'], rotation=45, ha='right', fontsize=10)
        
        # Add legend
        ax.legend(loc='upper right', fontsize=11)
        
        # Add title and adjust layout
        plt.title('叱咤 903 我最喜愛歌曲票數比例 與 YouTube MV 觀看次數比例',
                 pad=25, fontsize=14)
        plt.tight_layout()
        
        # Add difference labels between the bars
        for i in range(len(df)):
            diff = df['proportion_difference'].iloc[i]
            x_pos = i
            y_pos = max(df['normalized_views'].iloc[i], df['normalized_votes'].iloc[i])
            color = 'green' if diff > 0 else 'red'
            if abs(diff) > 5:  # Only show differences greater than 5%
                ax.text(x_pos, y_pos + 2, 
                       f'Δ{diff:+.0f}%', 
                       ha='center', va='bottom',
                       color=color, fontsize=8, fontweight='bold')
        
        # Save and show plot
        if output_path:
            plt.savefig(output_path, bbox_inches='tight', dpi=300)
            logger.info(f"Plot saved to {output_path}")
        plt.show()
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Read and process data
        df = pd.read_csv('data.csv', skipinitialspace=True)
        
        df = df[df['Year'] == 2024]       
        
        # Create and save plot
        df = normalize_data(df)
        create_dual_axis_plot(df)
        
    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}")
        raise
