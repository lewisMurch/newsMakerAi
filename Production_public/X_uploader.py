import os
from requests_oauthlib import OAuth1
import tweepy

# Define your keys and tokens
CONSUMER_KEY  = 'consumerkey_example'
CONSUMER_SECRET  = 'consumersecret__example'
ACCESS_TOKEN  = 'access-tokenexample'
ACCESS_TOKEN_SECRET  = 'access_token_secret'

# Authenticate to Twitter using v2 for creating tweets
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Authenticate to Twitter using v1.1 for media uploads
auth = tweepy.OAuth1UserHandler(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Function to upload media using v1.1
def upload_media_v1(filepath):
    media = api.media_upload(filepath)
    return media.media_id

# Function to post a tweet with media using v2
def post_tweet_v2(text, media_id, filename):
    response = client.create_tweet(text=text, media_ids=[media_id])
    if response.errors:
        raise Exception(f"Tweet failed: {response.errors}")
    print(f"Tweet ({filename}) posted successfully!")

def upload_video_to_X(video_filepath, tweet_text, filename):
    try:
        # Upload video and get media ID
        media_id = upload_media_v1(video_filepath)
        # Post tweet with the uploaded video
        post_tweet_v2(tweet_text, media_id, filename)
    except Exception as e:
        print(f"Error: {e}")