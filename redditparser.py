import os
# import uuid
import json
import requests
import praw
import datetime
from subprocess import check_output
from clint.textui import progress
from config import *
# from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='AutoTube/0.69.beta')

video_output = "./videos"
video_url = "./video_data"

change_aspect_ratio_cmd = 'ffmpeg -i {} -vf "scale=w=720:h=1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2" -c:a copy {}'

def download_progress(url, path):
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(
                r.iter_content(chunk_size=1024),
                expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()


def get_video_id(url):
    if "v.redd" in url:
        url = "https://www.reddit.com/video/" + url.split("v.redd.it/")[1]

    if not url.endswith(".json"):
        url += ".json"

    # Fetch the JSON data for the post
    response = requests.get(url, headers={"User-agent": "video_downloader"})

    data = json.loads(response.text)

    return data[0]['data']['children'][0]['data']['id']


def download_reddit_video(url, output_dir=video_output):
    # Check if output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if "v.redd" in url:
        url = "https://www.reddit.com/video/" + url.split("v.redd.it/")[1]

    # Add .json to the end of the URL
    if not url.endswith(".json"):
        url += ".json"

    # Fetch the JSON data for the post
    response = requests.get(url, headers={"User-agent": "video_downloader"})
    data = json.loads(response.text)

    # Extract video URL
    video_url = data[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    audio_url = video_url.split("DASH_")[0] + "DASH_audio.mp4"

    # Download video
    # video_response = requests.get(video_url)
    video_filename = os.path.join(output_dir,
                                  f"video_{data[0]['data']['children'][0]['data']['id']}.mp4")
    audio_filename = os.path.join(output_dir,
                                  f"video_{data[0]['data']['children'][0]['data']['id']}_audio.mp4")

    output_filename = os.path.join(output_dir,
                                   f"video_{data[0]['data']['children'][0]['data']['id']}_output.mp4")

    tmp_audio = os.path.join(output_dir, data[0]['data']['children'][0]['data']['id'] + ".mp3")

#     print(video_url, video_filename)
#     print(audio_url, audio_filename)
#     print(tmp_audio)

    if os.path.exists(output_filename):
        print("Video Already Exists")
        return

    download_progress(video_url, video_filename)
    download_progress(audio_url, audio_filename)
    # Use FFmpeg to extract the audio from file2.mp4
    audio_command = f"ffmpeg -i {audio_filename} {tmp_audio}"

    try:
        check_output(audio_command, shell=True)

        # Use FFmpeg to merge the audio and video from the two files
        merge_command = f"ffmpeg -i \
                            {video_filename} -i \
                            {tmp_audio} -c:v copy -map 0:v:0 \
                            -map 1:a:0 {output_filename}"

        check_output(merge_command, shell=True)

        # Remove the temporary audio file
        changed_ratio_file = output_filename.replace("output.mp4", ".720x1280.output.mp4")
        cmd = change_aspect_ratio_cmd.format(output_filename, changed_ratio_file)

        check_output(cmd, shell=True)

        check_output(f"rm {tmp_audio} {video_filename} \
                     {audio_filename} {output_filename}", shell=True)

        print(f"Video saved as {changed_ratio_file}")
    except Exception as e:
        print(e)


def get_videos(subreddit, file=None, timeframe="day", limit=2):
    subreddit = reddit.subreddit(subreddit)

    top_videos = subreddit.top(timeframe, limit=limit)

    top_posts = []

    for video in top_videos:
        if 'v.redd.it' in video.url:
            data = {
                "title": video.title,
                "url": video.url,
                "video_id": get_video_id(video.url)
            }
            top_posts.append(data)

    return top_posts


def data_parser(subreddit, timeframe, limit, video_url):
    today = datetime.date.today().__str__()
    # subreddit = ["videomemes"]

    for sr in subreddit:
        print(f"Scraping {sr}", end=" | ")
        _data = get_videos(sr, video_url, timeframe=timeframe, limit=limit)
        print(f"Found {_data.__len__()} videos", end=" | ")

        if _data == []:
            continue

        filename = os.path.join(video_url, f"{sr}_{today}.json")

        print(f"Writing to {filename}", end=" | ")

        try:
            with open(filename, "w+") as file_data:
                str_data = file_data.read()
                json_data = None
                try:
                    if str_data.__len__() != 0:
                        json_data = json.loads(str_data)
                except Exception as e:
                    print(e)

                file_data.seek(0)
                if json_data is not None:
                    update = _data + json_data
                    json.dump(update, file_data)
                    file_data.truncate()
                else:
                    json.dump(_data, file_data)

            print("Done!")

        except Exception as e:
            print(e, filename)
