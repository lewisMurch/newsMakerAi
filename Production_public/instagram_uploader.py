import requests
import time
import json

#https://developers.facebook.com/tools/explorer - here you can get the access_tokens that last an hour

credentials = {
    'ASMR': {
        'access_token': 'your-apikeyhere',
        'business_account': "account_id"
    },
    'left': {
        'access_token': "your-apikeyhere",
        'business_account': "account_id"
    },
    'right': {
        'access_token': 'your-apikeyhere',
        'business_account': 'account_id'
    },
    'centre': {
        'access_token': 'your-apikeyhere',
        'business_account': 'account_id'
    }
}

def upload_to_file_service(filepath):
    """
    Uploads the video to a free file hosting service to obtain a public URL.

    Parameters:
    - filepath: str, The path to the video file on your computer.

    Returns:
    - str, The URL of the uploaded video.
    """
    # Using File.io for demonstration
    upload_url = "https://file.io"
    
    with open(filepath, 'rb') as video_file:
        files = {'file': video_file}
        response = requests.post(upload_url, files=files)
    
    if response.status_code == 200:
        upload_result = response.json()
        video_url = upload_result.get("link")
        print(f"Video uploaded successfully: {video_url}")
        return video_url
    else:
        print("Failed to upload video.")
        return None

graph_url = 'https://graph.facebook.com/v20.0/'
def post_reel(caption='', media_type ='',share_to_feed='',thumb_offset='0',video_url='',access_token = '',instagram_account_id =''):
    url = graph_url + instagram_account_id + '/media'
    param = dict()
    param['access_token'] = access_token
    param['caption'] = caption
    param['media_type'] = media_type
    param['share_to_feed'] = share_to_feed
    param['thumb_offset'] = thumb_offset
    param['video_url'] = video_url
    response =  requests.post(url,params = param)
    response =response.json()
    return response

def status_of_upload(ig_container_id = '',access_token=''):
    url = graph_url + ig_container_id
    param = {}
    param['access_token'] = access_token
    param['fields'] = 'status_code'
    response = requests.get(url,params=param)
    response = response.json()
    return response

def publish_container(creation_id = '',access_token = '',instagram_account_id=''):
    url = graph_url + instagram_account_id + '/media_publish'
    param = dict()
    param['access_token'] = access_token
    param['creation_id'] = creation_id
    response = requests.post(url,params=param)
    response = response.json()
    return response

def run(filepath, caption, politic):
    access_token = credentials[politic]['access_token']
    account_id = credentials[politic]['business_account']
    video_url = upload_to_file_service(filepath)

    #Step 1
    post_info = post_reel(caption, 'REELS', 'true', '0', video_url, access_token, account_id)
    post_ID = post_info.get("id")

    #Step 2
    upload_info = status_of_upload(post_ID, access_token)
    upload_status = upload_info.get("status_code")
    while upload_status != 'FINISHED':
        time.sleep(5)
        upload_info = status_of_upload(post_ID, access_token)
        upload_status = upload_info.get("status_code")

    upload_id = upload_info.get("id")
    print(upload_info)
    print(upload_id)

    #Step 3
    x = publish_container(upload_id, access_token, account_id)
    print('Published Instagram content! - ' + json.dumps(x, indent=2))
