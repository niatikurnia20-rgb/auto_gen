import re
import time

import google.generativeai as genai
import requests
from google.generativeai.types import RequestOptions

from config import GEMINI_API_KEY

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)

# We prioritize the newest Flash models, then fall back to stable aliases.
MODEL_PRIORITY_LIST = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_REQUEST_TIMEOUT = 6
GEMINI_REQUEST_TIMEOUT = 20
SCRIPT_TOTAL_TIMEOUT = 45

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "fakta",
    "fact",
    "facts",
    "negeri",
    "negara",
    "tentang",
    "about",
}

META_MARKERS = (
    "here is your voiceover script",
    "note:",
    "please clarify",
    "the prompt asked",
    "provided facts",
    "would be incorrect",
    "i have written the script based on",
    "to ensure accuracy",
    "instead, here is",
)


def _report(progress_callback, message):
    print(message)
    if progress_callback:
        try:
            progress_callback(message)
        except Exception:
            pass


def _normalize_tokens(text):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def _pick_best_search_result(topic, search_results):
    topic_tokens = _normalize_tokens(topic)
    best_title = None
    best_score = 0

    for title in search_results:
        title_tokens = _normalize_tokens(title)
        if not title_tokens:
            continue

        overlap = len(topic_tokens & title_tokens)
        score = overlap * 3
        title_lower = title.lower()
        topic_lower = topic.lower()

        if title_lower in topic_lower or topic_lower in title_lower:
            score += 4

        for token in topic_tokens:
            if token in title_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_title = title

    if best_score <= 0:
        return None
    return best_title


def _wiki_request(params):
    headers = {"User-Agent": "ClipCoreAI/1.0 (script generation)"}
    response = requests.get(
        WIKIPEDIA_API_URL,
        params=params,
        headers=headers,
        timeout=WIKIPEDIA_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _trim_summary(text, max_sentences=4):
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return ""

    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return " ".join(parts[:max_sentences]).strip()


def _fetch_summary(page_title):
    data = _wiki_request(
        {
            "action": "query",
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "redirects": 1,
            "titles": page_title,
            "format": "json",
        }
    )

    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    extract = _trim_summary(page.get("extract", ""))

    if not extract:
        return None

    lower_extract = extract.lower()
    if "may refer to:" in lower_extract or "may also refer to:" in lower_extract:
        return None

    return {"title": page.get("title", page_title), "summary": extract}


def get_wiki_summary(topic):
    """Fetch a relevant Wikipedia summary with explicit network timeouts."""
    cleaned_topic = topic.strip()
    candidates = [cleaned_topic]

    if "," in cleaned_topic:
        candidates.extend(part.strip() for part in cleaned_topic.split(",") if part.strip())

    seen = set()
    for candidate in candidates:
        key = candidate.lower()
        if not candidate or key in seen:
            continue
        seen.add(key)

        try:
            summary = _fetch_summary(candidate)
            if summary:
                return summary
        except Exception:
            pass

    try:
        search_data = _wiki_request(
            {
                "action": "query",
                "list": "search",
                "srprop": "",
                "srlimit": 5,
                "srsearch": cleaned_topic,
                "format": "json",
            }
        )
        search_results = [
            item.get("title", "")
            for item in search_data.get("query", {}).get("search", [])
            if item.get("title")
        ]
    except Exception:
        return None

    best_title = _pick_best_search_result(cleaned_topic, search_results)
    if not best_title:
        return None

    try:
        return _fetch_summary(best_title)
    except Exception:
        return None


def _build_prompt(topic, context):
    context_block = ""
    if context:
        context_block = (
            f"Reference facts from Wikipedia about {context['title']}:\n"
            f"{context['summary']}\n\n"
        )

    return (
        "You are a professional YouTube Shorts scriptwriter.\n"
        f"Topic: {topic}\n\n"
        f"{context_block}"
        "Write the final narration in Bahasa Indonesia.\n"
        "Return ONLY the narration script.\n"
        "Do not add notes, disclaimers, explanations, titles, headings, labels, or quotation marks.\n"
        "Do not mention the prompt, the reference facts, or any mismatch.\n"
        "If the reference facts seem unrelated to the topic, ignore them and keep writing about the topic.\n\n"
        "Requirements:\n"
        "1. Approx 100 words for a 40-second video.\n"
        "2. Structure: hook -> 3 fakta menarik -> penutup singkat.\n"
        "3. No scene directions. Only write what the narrator says.\n"
        "4. Tone: energik, jelas, dan edukatif."
    )


def _clean_generated_script(raw_text):
    cleaned = raw_text.replace("**", "").replace("##", "").replace("*", "").strip()
    lines = []

    for line in cleaned.splitlines():
        stripped = line.strip(" \t:-")
        if not stripped:
            continue

        lower = stripped.lower()
        if any(marker in lower for marker in META_MARKERS):
            continue
        if lower.startswith("catatan"):
            continue

        lines.append(stripped)

    cleaned = "\n".join(lines).strip()
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned


def _looks_like_meta_response(text):
    lower = text.lower()
    return any(marker in lower for marker in META_MARKERS)


def _build_fallback_script(topic):
    return (
        f"Hari ini kita akan membahas fakta menarik tentang {topic}. "
        "Topik ini punya latar belakang yang unik, sejarah yang kaya, dan hal-hal yang sering tidak diketahui banyak orang. "
        "Semoga video singkat ini menambah wawasan kamu."
    )


def generate_script(topic, progress_callback=None):
    started_at = time.monotonic()
    _report(progress_callback, f"Generating script for '{topic}'...")

    _report(progress_callback, "Fetching reference facts...")
    context = get_wiki_summary(topic)
    if context:
        _report(progress_callback, f"Reference found: {context['title']}.")
    else:
        _report(progress_callback, "Reference lookup skipped. Continuing with topic only.")

    for model_name in MODEL_PRIORITY_LIST:
        elapsed = time.monotonic() - started_at
        if elapsed >= SCRIPT_TOTAL_TIMEOUT:
            _report(progress_callback, "Script generation timeout reached. Using fallback script.")
            return _build_fallback_script(topic)

        _report(progress_callback, f"Trying model: {model_name}...")
        model = genai.GenerativeModel(model_name)

        prompt_contexts = [context] if context else []
        prompt_contexts.append(None)

        for current_context in prompt_contexts:
            try:
                prompt = _build_prompt(topic, current_context)
                response = model.generate_content(
                    prompt,
                    request_options=RequestOptions(timeout=GEMINI_REQUEST_TIMEOUT),
                )
                raw_script = response.text.strip()

                if _looks_like_meta_response(raw_script):
                    raise ValueError("Model returned meta commentary instead of a script.")

                script = _clean_generated_script(raw_script)
                if not script:
                    raise ValueError("Model returned an empty script.")

                _report(progress_callback, f"Script ready with {model_name}.")
                return script

            except ValueError as e:
                _report(progress_callback, f"Retrying script generation: {e}")
                continue
            except Exception as e:
                if "429" in str(e) or "Quota" in str(e):
                    _report(progress_callback, f"Quota hit on {model_name}. Switching...")
                elif "Deadline" in str(e) or "timed out" in str(e).lower():
                    _report(progress_callback, f"{model_name} timed out. Switching...")
                else:
                    _report(progress_callback, f"Error on {model_name}: {e}")
                break

        time.sleep(1)

    _report(progress_callback, "All AI models failed. Using simple fallback script.")
    return _build_fallback_script(topic)
