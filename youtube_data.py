from googleapiclient.discovery import build
from datetime import datetime

def get_video_stats(video_id):
    """
    Fetch video statistics from YouTube Data API v3.
    
    Args:
        video_id (str): YouTube video ID (e.g., 'dQw4w9WgXcQ' from https://www.youtube.com/watch?v=dQw4w9WgXcQ)
    
    Returns:
        tuple: (view_count, upload_date) where:
            - view_count (int): Number of views
            - upload_date (str): Video upload date in YYYY-MM-DD format
    """
    # API credentials
    API_KEY = 'AIzaSyAQUs8WjOoaFcJTwYjHuGsdZflwMDxF7NE'
    
    try:
        # Create YouTube API client
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        # Request video details
        request = youtube.videos().list(
            part='statistics,snippet',
            id=video_id
        )
        response = request.execute()
        
        # Check if video exists
        if not response['items']:
            raise ValueError(f"No video found with ID: {video_id}")
        
        # Extract data
        video_data = response['items'][0]
        view_count = int(video_data['statistics']['viewCount'])
        upload_date = video_data['snippet']['publishedAt'][:10]  # Get YYYY-MM-DD format
        
        return view_count, upload_date
        
    except Exception as e:
        print(f"Error fetching video data: {str(e)}")
        return None, None

# Example usage
if __name__ == "__main__":
    video_id = "DaQNnnU1DA4"
    views, date = get_video_stats(video_id)
    
    if views and date:
        print(f"Views as of {datetime.now().strftime('%Y-%m-%d')}: {views}")
        print(f"Upload Date: {date}")
        print(f"Views per day as of {datetime.now().strftime('%Y-%m-%d')}: {round(views / (datetime.now() - datetime.strptime(date, '%Y-%m-%d')).days)}")
