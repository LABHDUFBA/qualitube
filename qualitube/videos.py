from channel import API_KEY
import requests
import json
import pandas as pd
from configparser import ConfigParser
import sys

config = ConfigParser()
config.read("config.ini")
API_KEY = config['credentials']['api_key']

class Videos:
    def __init__(self, videos_ids, api_key=API_KEY):
        self.videos_ids = videos_ids
        self.api_key = api_key
    
    def _try_parse(self, item, key):
        try:
            parsed = item[key]
        except KeyError:
            parsed = None
        return parsed

    def _parse_response(self, data):
        raw = json.loads(data)
        try:
            items = raw['items']
        except KeyError as e:
            print(raw)
            sys.exit(e)

        parsed = []
        for item in items:
            parsed.append({
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'video_id': item['id'],
                'video_title': item['snippet']['title'],
                'video_description': item['snippet']['description'],
                'video_tags': self._try_parse(item['snippet'], 'tags'),
                'video_published_at': item['snippet']['publishedAt'],
                'video_view_count': item['statistics']['viewCount'],
                'video_like_count': item['statistics']['likeCount'],
                'video_dislike_count': item['statistics']['dislikeCount'],
                'video_favorite_count': item['statistics']['favoriteCount'],
                'video_comment_count': self._try_parse(item['statistics'], 'commentCount')
            })

        try:
            next_page_token = raw["nextPageToken"]
        except KeyError:
            next_page_token = False
        
        return parsed, next_page_token

    def _get_ids_parameter(self):
        ids = ','.join(self.videos_ids)
        return ids

    def get_data(self, page_token=None):
        headers = {
            'Accept': 'application/json',
        }

        params = [
            ('part', 'snippet,statistics'),
            ('id', self._get_ids_parameter()),
            ('key', self.api_key)
        ]

        if page_token:
            params.append(
                ('pageToken', page_token)
            )

        r = requests.get('https://youtube.googleapis.com/youtube/v3/videos', headers=headers, params=params)
        
        videos_data, next_page_token = self._parse_response(r.text)

        if next_page_token:
            return videos_data + self.get_data(next_page_token)

        return videos_data
    
    def to_df(self):
        df = pd.DataFrame(self.get_data())
        return df
