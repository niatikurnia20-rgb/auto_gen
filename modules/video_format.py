DEFAULT_ASPECT_RATIO = "portrait"

ASPECT_RATIO_CONFIG = {
    "landscape": {
        "label": "Landscape",
        "orientation": "landscape",
        "target_size": (1280, 720),
    },
    "portrait": {
        "label": "Portrait",
        "orientation": "portrait",
        "target_size": (720, 1280),
    },
}


def normalize_aspect_ratio(value):
    normalized = (value or "").strip().lower()
    if normalized in ASPECT_RATIO_CONFIG:
        return normalized
    return DEFAULT_ASPECT_RATIO


def get_target_size(aspect_ratio):
    normalized = normalize_aspect_ratio(aspect_ratio)
    return ASPECT_RATIO_CONFIG[normalized]["target_size"]


def matches_orientation(width, height, aspect_ratio):
    normalized = normalize_aspect_ratio(aspect_ratio)

    if not width or not height:
        return False

    if normalized == "portrait":
        return height > width

    return width > height
