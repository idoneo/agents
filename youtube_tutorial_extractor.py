import re
import sys
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """
    Fetches the transcript for a given YouTube video ID.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f'An error occurred while fetching transcript: {e}')
        return None

def process_transcript(transcript):
    """
    Processes the transcript to extract step-by-step instructions or bullet points.
    """
    steps = []
    for entry in transcript:
        text = entry['text']
        # Simple heuristic: if a line starts with a number or a bullet point, consider it a step
        if re.match(r"^\d+\.|\*", text):
            steps.append(text)
    return steps

def main(url):
    video_id = extract_video_id(url)
    if not video_id:
        print("Invalid YouTube URL.")
        return

    transcript = fetch_transcript(video_id)
    if not transcript:
        print("No transcript available for this video.")
        return

    steps = process_transcript(transcript)
    if steps:
        print("Extracted Steps:")
        for step in steps:
            print(f"- {step}")
    else:
        print("No steps could be extracted from the transcript.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_tutorial_extractor.py <YouTube URL>")
        sys.exit(1)
    youtube_url = sys.argv[1]
    main(youtube_url)
