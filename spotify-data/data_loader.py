import pandas as pd
import json
from datetime import datetime
import numpy as np

def load_spotify_data(json_file_path='combined_data.json'):
    """
    Load Spotify listening data from JSON file into a pandas DataFrame
    with proper data types and preprocessing.
    """
    print(f"Loading data from {json_file_path}...")
    
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    print(f"Loaded {len(df):,} listening records")
    
    df = preprocess_data(df)
    
    return df

def preprocess_data(df):
    """
    Clean and preprocess the Spotify data for analysis.
    """
    print("Preprocessing data...")
    
    df['ts'] = pd.to_datetime(df['ts'])
    
    df['date'] = df['ts'].dt.date
    df['hour'] = df['ts'].dt.hour
    df['day_of_week'] = df['ts'].dt.day_name()
    df['month'] = df['ts'].dt.month_name()
    df['year'] = df['ts'].dt.year
    
    df['minutes_played'] = df['ms_played'] / (1000 * 60)
    df['seconds_played'] = df['ms_played'] / 1000
    
    def get_media_info(row):
        if pd.notna(row['master_metadata_track_name']):
            return {
                'media_type': 'song',
                'title': row['master_metadata_track_name'],
                'artist': row['master_metadata_album_artist_name'] if pd.notna(row['master_metadata_album_artist_name']) else 'Unknown Artist',
                'album': row['master_metadata_album_album_name'] if pd.notna(row['master_metadata_album_album_name']) else 'Unknown Album'
            }
        elif pd.notna(row['episode_name']):
            return {
                'media_type': 'podcast',
                'title': row['episode_name'],
                'artist': row['episode_show_name'] if pd.notna(row['episode_show_name']) else 'Unknown Podcast',
                'album': 'Podcast Episode'
            }
        elif pd.notna(row['audiobook_title']):
            return {
                'media_type': 'audiobook',
                'title': row['audiobook_chapter_title'] if pd.notna(row['audiobook_chapter_title']) else row['audiobook_title'],
                'artist': row['audiobook_title'],
                'album': 'Audiobook'
            }
        else:
            return {
                'media_type': 'unknown',
                'title': 'Unknown Content',
                'artist': 'Unknown',
                'album': 'Unknown'
            }
    
    media_info = df.apply(get_media_info, axis=1, result_type='expand')
    df['media_type'] = media_info['media_type']
    df['track_name'] = media_info['title']
    df['track_artist'] = media_info['artist']
    df['album_name'] = media_info['album']
    
    df['is_skip'] = df['skipped'] == True
    df['is_complete_play'] = (df['reason_end'] == 'endplay') & (~df['is_skip'])
    
    df['listening_session'] = (df['ts'].diff() > pd.Timedelta(minutes=30)).cumsum()
    
    print("Preprocessing complete!")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total listening time: {df['minutes_played'].sum():.1f} minutes ({df['minutes_played'].sum()/60:.1f} hours)")
    
    return df

def get_data_summary(df):
    """
    Generate a summary of the dataset.
    """
    media_type_counts = df['media_type'].value_counts()
    media_type_percentages = (df['media_type'].value_counts(normalize=True) * 100).round(1)
    
    summary = {
        'total_tracks': len(df),
        'unique_tracks': df['spotify_track_uri'].nunique(),
        'unique_artists': df['track_artist'].nunique(),
        'unique_albums': df['album_name'].nunique(),
        'date_range': f"{df['date'].min()} to {df['date'].max()}",
        'total_listening_hours': round(df['minutes_played'].sum() / 60, 1),
        'avg_daily_hours': round(df[df['date'] >= pd.to_datetime('2023-12-18').date()].groupby('date')['minutes_played'].sum().mean() / 60, 2),
        'skip_rate': round(df['is_skip'].mean() * 100, 1),
        'media_breakdown': {media_type: f"{count} ({media_type_percentages[media_type]}%)" 
                          for media_type, count in media_type_counts.items()}
    }
    
    return summary

if __name__ == "__main__":
    df = load_spotify_data()
    summary = get_data_summary(df)
    
    print("\n" + "="*50)
    print("SPOTIFY DATA SUMMARY")
    print("="*50)
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
