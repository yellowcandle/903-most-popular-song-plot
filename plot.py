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
    df = df.dropna(subset=['view per day', 'Total'])
    df = df.sort_values('view per day', ascending=False)
    
    return df

def create_dual_axis_plot(df: pd.DataFrame, output_path: Optional[str] = 'plot.png') -> None:
    """
    Create an enhanced dual-axis plot comparing views per day and total votes.
    
    Args:
        df: DataFrame containing song data
        output_path: Optional path to save the plot (default: 'plot.png')
    """
    try:
        # Validate and prepare data
        df = validate_data(df)
        
        # Create figure and axes
        fig, ax1 = plt.subplots(figsize=(16, 8))
        ax2 = ax1.twinx()
        
        # Set positions and width
        x = range(len(df))
        width = 0.4
        
        # Plot views per day
        views_bars = ax1.bar(
            [i - width/2 for i in x], df['view per day'],
            width, color=COLORS['views'], alpha=0.8, label='Views/Day'
        )
        
        # Plot total votes
        votes_bars = ax2.bar(
            [i + width/2 for i in x], df['Total'],
            width, color=COLORS['votes'], alpha=0.8, label='Total Votes'
        )
        
        # Configure axes
        ax1.set_xlabel('Songs', fontsize=12, labelpad=15)
        ax1.set_ylabel('Views per Day', color=COLORS['views'], fontsize=12)
        ax2.set_ylabel('Total Votes', color=COLORS['votes'], fontsize=12)
        
        # Format y-axes
        for ax in [ax1, ax2]:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
            ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Add value labels
        for bar in views_bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}', ha='center', va='bottom',
                    fontsize=8, color=COLORS['views'])
        
        for bar in votes_bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}', ha='center', va='bottom',
                    fontsize=8, color=COLORS['votes'])
        
        # Configure x-axis
        plt.xticks(x, df['Title'], rotation=45, ha='right', fontsize=10)
        
        # Add combined legend
        lines = [views_bars, votes_bars]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right', 
                  bbox_to_anchor=(1, 1.15), fontsize=11)
        
        # Add title and adjust layout
        plt.title('YouTube Music Popularity: Daily Views vs Total Votes (2024)',
                 pad=25, fontsize=14)
        plt.tight_layout()
        
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
        
        # Create and save plot
        create_dual_axis_plot(df)
        
    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}")
        raise
