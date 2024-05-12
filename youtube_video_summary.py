import streamlit as st
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()  # Load environment variables from a .env file
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def get_top_videos_by_views(subject, max_results=5):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    search_response = youtube.search().list(
        q=subject,
        part='snippet',
        order='viewCount',
        maxResults=max_results,
        type='video'
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        videos.append({
            'title': search_result['snippet']['title'],
            'video_id': search_result['id']['videoId']
        })
    return videos

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f'An error occurred while fetching transcript: {e}')
        return None

def display_video_summaries(videos):
    for video in videos:
        st.subheader(video['title'])
        st.write(video['overview'])

def save_to_markdown(videos):
    export_dir = 'export'
    os.makedirs(export_dir, exist_ok=True)
    with open(f'{export_dir}/video_summaries.md', 'w') as f:
        for video in videos:
            f.write(f"## {video['title']}\n\n")
            f.write(f"{video['overview']}\n\n")

def main():
    st.title('YouTube Video Summary')
    subject = st.text_input('Enter the subject to search on YouTube:', '')
    if subject:
        with st.spinner('Fetching top videos...'):
            top_videos = get_top_videos_by_views(subject)
            for video in top_videos:
                transcript = get_video_transcript(video['video_id'])
                if transcript:
                    video['overview'] = transcript[:500] + '...'  # Taking the first 500 characters for a brief overview
                else:
                    video['overview'] = 'No transcript available...'
        display_video_summaries(top_videos)
        save_to_markdown(top_videos)
        st.success("Video summaries have been saved to 'video_summaries.md'")

if __name__ == '__main__':
    st.set_page_config(page_title="YouTube Video Summary", page_icon=":clapper:", layout="wide")
    main()
