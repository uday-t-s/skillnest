from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """Extract YouTube video ID from URL."""
    if 'youtube.com/watch?v=' in url:
        match = re.search(r'v=([^&]+)', url)
        return match.group(1) if match else ''
    elif 'youtu.be/' in url:
        match = re.search(r'youtu\.be/([^?]+)', url)
        return match.group(1) if match else ''
    return ''

@register.filter
def extract_embed_url(value):
    """Extract embed URL from full iframe embed code or return URL as-is."""
    if not value:
        return ''

    # First, check if it's a full iframe embed code and extract the src
    iframe_match = re.search(r'<iframe[^>]*src=["\']([^"\']*)["\'][^>]*>', value, re.IGNORECASE)
    if iframe_match:
        return iframe_match.group(1)

    # Check if it's already an embed URL
    if '/embed/' in value or '/video/' in value:
        return value

    # Check if it's a regular YouTube URL that needs conversion
    if 'youtube.com/watch?v=' in value or 'youtu.be/' in value:
        video_id = youtube_id(value)
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'

    # Return as-is for other URLs
    return value