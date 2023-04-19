# AutoTube - Reddit Video Compiler

AutoTube is a Python program that automates the process of downloading, compiling, and uploading Reddit videos to YouTube. 

## Installation

Clone the repository from Github:
```shell
$ git clone https://github.com/0x30c4/repo.git
```
Install the required dependencies:
```shell
$ pip3 install -r requirements.txt
```

### This script requires [ffmpeg](https://ffmpeg.org)

## Setup.
First run:
```shell
$ cp creds.example.json creds.json
```

Put your reddit api key in the ```creds.json``` file
```
{
	"client_secret": "CLIENT_SECRET",
	"client_id": "CLIENT_ID",
	"username": "USERNAME",
	"password": "PASSWORD"
}
```

Run the program:
```
$ python3 main.py --help
usage: main.py [-h] [-d] [-j] [-p PARSED_DIR] [-l PARSE_LIMIT] [-t TIMEFRAME]
               [-s DOWNLOAD_WITH_DATE] [-f SUBREDDIT_LIST] [-o OUTPUT_DIR]
               [-g FINAL_OUT_DIR] [-w THREADS] [-a] [-c] [-k VIDEO_LENGTH]
               [-z CONCAT_CLIPS_DIR]

AutoTube is a Reddit video compiler that automates the process of downloading,
compiling, and uploading Reddit videos to YouTube in one simple program.

optional arguments:
  -h, --help            show this help message and exit
  -d                    Download parsed videos.
  -j                    Just download the parsed videos. Use it with --parsed-
                        dir
  -p PARSED_DIR, --parsed-dir PARSED_DIR
                        Parse and save parsed data into PARSED_DIR. Default:
                        video_data
  -l PARSE_LIMIT, --parse-limit PARSE_LIMIT
                        Set the limit of videos to be parsed from a subreddit.
                        Default: 5
  -t TIMEFRAME, --timeframe TIMEFRAME
                        Time frame of video parsing (day, week, month, year).
                        Default: day
  -s DOWNLOAD_WITH_DATE, --download-with-date DOWNLOAD_WITH_DATE
                        Download videos of date. Example: -s 2023-03-30
  -f SUBREDDIT_LIST, --subreddit-list SUBREDDIT_LIST
                        Subreddit list file. One line should contain just one
                        subreddit.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Video download directory. Default: ./videos
  -g FINAL_OUT_DIR, --final-out-dir FINAL_OUT_DIR
                        Finale output directory. Default: ./final_output
  -w THREADS, --threads THREADS
                        Threads to use for downloading. Default: 1
  -a                    Automatically creates videos and data output
                        directorys with uuid
  -c                    Automatically concatinates all the clips into specific
                        duration length video
  -k VIDEO_LENGTH, --video-length VIDEO_LENGTH
                        Threads to use for downloading. Default: 540 seconds
                        or 9 minutes
  -z CONCAT_CLIPS_DIR, --concat-clips-dir CONCAT_CLIPS_DIR
                        FFMPEG concat files dir. Default: ./concat_files
```

# Example Usage

To parse the video URLs from a subreddit:
```
$ python3 main.py -f subreddits.txt -p video_data
```
To download the parsed videos:
```
$ python3 main.py -d -p video_data -o videos
```
To concatenate all the downloaded videos into a single video:
```
$ python3 main.py -c -o videos -g final_output
```

To parse, download and create a single video:
```
$ .python3 main.py -d -w 40 -a -f sublist -l 1 -s 2023-04-19 -k 60 -c
```
