import requests
from config import PEXELS_API_KEY

def fetch_stock_media(query, count=5):
    headers = {"Authorization": PEXELS_API_KEY}
    # Changed 'search' to 'videos/search'
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={count}&min_width=1280"
    
    media_urls = []
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        
        for video in data.get('videos', []):
            # Get the best quality video file (usually HD)
            video_files = video.get('video_files', [])
            # Sort by width to get high quality (descending)
            video_files.sort(key=lambda x: x['width'], reverse=True)
            
            if video_files:
                media_urls.append(video_files[0]['link'])
                
    except Exception as e:
        print(f"Pexels Error: {e}")
    
    return media_urls