import os
import markdown
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'  # Replace with your YouTube Data API v3 key
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

def save_to_markdown(videos, filename='video_summaries.md'):
    with open(filename, 'w') as file:
        for video in videos:
            file.write(f"## {video['title']}\n\n")
            file.write(f"{video['overview']}\n\n")

def main():
    subject = input('Enter the subject to search on YouTube: ')
    top_videos = get_top_videos_by_views(subject)

    for video in top_videos:
        transcript = get_video_transcript(video['video_id'])
        if transcript:
            video['overview'] = transcript[:500] + '...'  # Taking the first 500 characters for a brief overview

    save_to_markdown(top_videos)
    print(f"Video summaries have been saved to 'video_summaries.md'")

if __name__ == '__main__':
    main()
