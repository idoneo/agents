import streamlit as st
import os
import humanize
import isodate
from datetime import datetime, timezone
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
        video_id = search_result['id']['videoId']
        video_details = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute().get('items', [])[0]

        published_at = video_details['snippet']['publishedAt']
        channel_title = video_details['snippet']['channelTitle']
        duration = video_details['contentDetails']['duration']
        view_count = video_details['statistics']['viewCount']

        videos.append({
            'title': search_result['snippet']['title'],
            'video_id': video_id,
            'published_at': published_at,
            'channel_title': channel_title,
            'duration': duration,
            'view_count': view_count,
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
        video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
        published_time = humanize.naturaltime(datetime.now(timezone.utc) - isodate.parse_datetime(video['published_at']))
        duration = isodate.parse_duration(video['duration'])
        human_readable_duration = str(duration).split('.')[0]  # Remove microseconds
        views = humanize.intcomma(int(video['view_count']))
        st.markdown(f"Published by **{video['channel_title']}** {published_time}")
        st.markdown(f"Duration: **{human_readable_duration}**")
        st.markdown(f"Views: **{views}**")
        st.markdown(f'<h3><a href="{video_url}" target="_blank">{video["title"]}</a></h3>', unsafe_allow_html=True)
        st.markdown(video['overview'])

def save_to_markdown(videos, subject):
    export_dir = 'export'
    os.makedirs(export_dir, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{subject}_{current_date}_video_summaries.md".replace(" ", "_")
    with open(f'{export_dir}/{filename}', 'w') as f:
        for video in videos:
            video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
            published_time = humanize.naturaltime(datetime.now(timezone.utc) - isodate.parse_datetime(video['published_at']))
            duration = isodate.parse_duration(video['duration'])
            human_readable_duration = str(duration).split('.')[0]  # Remove microseconds
            views = humanize.intcomma(int(video['view_count']))
            f.write(f"Published by **{video['channel_title']}** {published_time}\n")
            f.write(f"Duration: **{human_readable_duration}**\n")
            f.write(f"Views: **{views}**\n")
            f.write(f"## [{video['title']}]({video_url})\n\n")
            f.write(f"{video['overview']}\n\n")

def main():
    st.title('YouTube Video Summary')
    subject = st.text_input('Enter the subject to search on YouTube:', '')
    submit_button = st.button('Search')
    if submit_button and subject:
        with st.spinner('Fetching top videos...'):
            top_videos = get_top_videos_by_views(subject)
            for video in top_videos:
                transcript = get_video_transcript(video['video_id'])
                if transcript:
                    video['overview'] = transcript[:500] + '...'  # Taking the first 500 characters for a brief overview
                else:
                    video['overview'] = 'No transcript available...'
        display_video_summaries(top_videos)
        filename = save_to_markdown(top_videos, subject)
        st.success(f"Video summaries have been saved to '{filename}'")
        filename = save_to_markdown(top_videos, subject)
        st.success(f"Video summaries have been saved to '{filename}'")

if __name__ == '__main__':
    st.set_page_config(page_title="YouTube Video Summary", page_icon=":clapper:", layout="wide")
    main()
