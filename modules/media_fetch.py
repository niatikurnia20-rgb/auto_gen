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
            # Ambil semua daftar file video dari Pexels
            video_files = video.get('video_files', [])
            
            # FILTER 1080p: Singkirkan video 4K, ambil yang lebarnya (width) maksimal 1920 pixel
            target_files = [f for f in video_files if f.get('width', 0) <= 1920]
            
            # Jaga-jaga: Jika pembuat video Pexels hanya mengunggah resolusi 4K (sangat jarang),
            # kita tetap ambil file aslinya agar tidak error
            if not target_files:
                target_files = video_files
                
            # Urutkan dari yang terbesar (tapi karena sudah difilter, yang terbesar pasti 1080p)
            target_files.sort(key=lambda x: x.get('width', 0), reverse=True)
            
            if target_files:
                media_urls.append(target_files[0]['link'])
                
    except Exception as e:
        print(f"Pexels Error: {e}")
    
    return media_urls