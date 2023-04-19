#!/usr/bin/python3

import os
import sys
import json
import argparse
import concurrent.futures
from datetime import date
from uuid import uuid4
from redditparser import data_parser, download_reddit_video

from make_videos import make_video

description = """
AutoTube is a Reddit video compiler that automates the process of downloading,
compiling, and uploading Reddit videos to YouTube in one simple program.
"""

parser = argparse.ArgumentParser(description=description)
# parser.add_argument('output-dir', help='The output directory')

parser.add_argument("-d", action='store_true',
                    help='Download parsed videos.')

parser.add_argument("-j", action='store_true',
                    help='Just download the parsed videos.\
                            Use it with --parsed-dir')

parser.add_argument("-p", "--parsed-dir", type=str,
                    help='Parse and save parsed data into \
                            PARSED_DIR. Default: video_data')

parser.add_argument("-l", "--parse-limit", type=int, default=5,
                    help='Set the limit of videos to be \
                            parsed from a subreddit. Default: 5')

parser.add_argument("-t", "--timeframe", type=str, default='day',
                    help='Time frame of video parsing \
                            (day, week, month, year). Default: day')

parser.add_argument("-s", "--download-with-date",
                    help='Download videos of date. Example: -s 2023-03-30')

parser.add_argument("-f", "--subreddit-list",
                    help='Subreddit list file. \
                            One line should contain just one subreddit.')

parser.add_argument("-o", "--output-dir", default="./videos",
                    help='Video download directory. Default: ./videos')

parser.add_argument("-g", "--final-out-dir", default="./final_output/",
                    help='Finale output directory. Default: ./final_output')

parser.add_argument("-w", "--threads", type=int, default=1,
                    help='Threads to use for downloading. Default: 1')

parser.add_argument("-a", action='store_true',
                    help='Automatically creates \
                        videos and data output directorys with uuid')

parser.add_argument("-c", action='store_true',
                    help='Automatically concatinates all the \
                        clips into specific duration length video')

parser.add_argument("-k", "--video-length", type=int, default=540,
                    help='Threads to use for downloading. \
                        Default: 540 seconds or 9 minutes')

parser.add_argument("-z", "--concat-clips-dir", type=str,
                    default="./concat_files/",
                    help='FFMPEG concat files dir. Default: ./concat_files')


args = parser.parse_args()

parsed_dir = args.parsed_dir
timeframe = args.timeframe
parse_limit = args.parse_limit
subreddit = args.subreddit_list
download_date = args.download_with_date
videos = args.output_dir
final_output = args.final_out_dir
threads = args.threads
video_length = args.video_length

concat_files_dir = args.concat_clips_dir

if not subreddit and args.j:
    print("Please Provide a subreddit list with -f <filename> option.\
            \nUse --help for help.",
          file=sys.stderr)
    exit(-1)

if args.a:
    uid = uuid4().hex
    today = date.today().__str__()
    uid = uid[:4] + "_" + today
    videos = uid + "_videos"
    parsed_dir = uid + "_data"

if not os.path.exists(parsed_dir):
    os.makedirs(parsed_dir)

if not os.path.exists(videos):
    os.makedirs(videos)

if not os.path.exists(concat_files_dir):
    os.makedirs(concat_files_dir)

# parse video data
if subreddit:
    with open(subreddit) as sb:
        sb = [i.strip() for i in sb.readlines() if i.strip()]

    if not threads:
        data_parser(sb, timeframe, parse_limit, parsed_dir)
    else:
        with concurrent.futures.ThreadPoolExecutor(
                        max_workers=threads) as executor:

            futures = [executor.submit(data_parser, [sr], timeframe, parse_limit, parsed_dir) for sr in sb]

            # Wait for all downloads to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                except Exception as exc:
                    print(f'Download failed: {exc}')

if args.j:
    exit(0)

if args.d or download_date:

    all_videos = []
    if not download_date:
        download_date = date.today().__str__()

    for file in os.listdir(parsed_dir):
        if download_date.strip() in file:
            file_path = os.path.join(parsed_dir, file)
            with open(file_path) as f:
                all_videos += [i["url"] for i in json.load(f)]

    if not threads:
        for video in all_videos:
            download_reddit_video(video, videos)
    else:
        with concurrent.futures.ThreadPoolExecutor(
                        max_workers=threads) as executor:

            futures = [executor.submit(download_reddit_video, video, videos) for video in all_videos]

            # Wait for all downloads to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                except Exception as exc:
                    print(f'Download failed: {exc}')

if args.c:
    make_video(videos, concat_files_dir, final_output)
