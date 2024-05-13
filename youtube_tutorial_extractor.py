import re
import sys
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

def streamlit_interface():
    st.title('YouTube Tutorial Extractor')
    youtube_url = st.text_input('Enter the YouTube URL:', '')
    extract_button = st.button('Extract Tutorial Steps')

    if extract_button and youtube_url:
        with st.spinner('Extracting tutorial steps...'):
            main(youtube_url)

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

def summarize_transcript(transcript):
    """
    Summarizes the transcript by concatenating all text entries.
    """
    summary = ' '.join([entry['text'] for entry in transcript])
    return summary

def main(url):
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL.")
        return

    transcript = fetch_transcript(video_id)
    if not transcript:
        st.error("No transcript available for this video.")
        return

    summary = summarize_transcript(transcript)
    if summary:
        video_details = fetch_video_details(video_id)
        if video_details:
            title = video_details['title']
            sanitized_title = re.sub(r'[^\w\s-]', '', title).replace(' ', '_')
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f"{current_date}_{sanitized_title}_tutorial.md"
            export_dir = 'export'
            os.makedirs(export_dir, exist_ok=True)
            with open(os.path.join(export_dir, filename), 'w') as f:
                f.write(f"# {title} Tutorial\n\n")
                f.write("## Summary\n")
                f.write(summary)
            st.success(f"Tutorial steps have been saved to '{filename}'")
    else:
        st.warning("No steps could be extracted from the transcript.")

def fetch_video_details(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    video_details = video_response.get('items', [])[0]['snippet']
    return {
        'title': video_details['title']
    }

if __name__ == "__main__":
    st.set_page_config(page_title="YouTube Tutorial Extractor", page_icon=":clapper:", layout="wide")
    streamlit_interface()
