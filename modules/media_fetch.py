import requests
from config import PEXELS_API_KEY
from modules.video_format import get_target_size, matches_orientation, normalize_aspect_ratio


def _pick_best_video_file(video_files, aspect_ratio):
    target_width, target_height = get_target_size(aspect_ratio)
    target_ratio = target_width / target_height
    target_area = target_width * target_height

    candidates = []
    for video_file in video_files:
        width = int(video_file.get('width') or 0)
        height = int(video_file.get('height') or 0)
        link = video_file.get('link')

        if not link or not matches_orientation(width, height, aspect_ratio):
            continue

        file_ratio = width / height if height else 0
        ratio_gap = abs(file_ratio - target_ratio)
        area = width * height
        meets_target = width >= target_width and height >= target_height
        size_score = abs(area - target_area) if meets_target else -area

        candidates.append(((0 if meets_target else 1, ratio_gap, size_score), video_file))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def fetch_stock_media(query, count=5, aspect_ratio='landscape'):
    aspect_ratio = normalize_aspect_ratio(aspect_ratio)
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/videos/search"
    per_page = min(max(count * 3, 15), 80)
    
    media_urls = []
    seen_links = set()
    try:
        for page in range(1, 4):
            params = {
                "query": query,
                "per_page": per_page,
                "page": page,
                "orientation": aspect_ratio,
            }

            r = requests.get(url, headers=headers, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            videos = data.get('videos', [])

            if not videos:
                break

            for video in videos:
                best_file = _pick_best_video_file(video.get('video_files', []), aspect_ratio)

                if not best_file:
                    continue

                link = best_file.get('link')
                if not link or link in seen_links:
                    continue

                media_urls.append(link)
                seen_links.add(link)

                if len(media_urls) >= count:
                    return media_urls

            if len(videos) < per_page:
                break

    except requests.RequestException as e:
        print(f"Pexels Error: {e}")
    
    return media_urls
