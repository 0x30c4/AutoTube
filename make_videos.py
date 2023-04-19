#!/usr/bin/python3
import os
import time
import tqdm
from moviepy.video.io.VideoFileClip import VideoFileClip

change_aspect_ratio_cmd = 'ffmpeg -i {} -vf "scale=w=720:h=1280\
        :force_original_aspect_ratio=decrease,pad=720:1280:(ow-\
        iw)/2:(oh-ih)/2" -c:a copy {}'
concat_command = "ffmpeg -f concat -safe 0 -i {} -c copy {}"


def make_video(
        video_clips_dir, concat_files_dir,
        final_output, video_len=540
        ):

    videos = [file for file in os.listdir(video_clips_dir) if "720x1280.output.mp4" in file]
    total = 0
    full_total = 0
    videos_clips = []
    full_videos = []

    for n, file in tqdm.tqdm(enumerate(videos)):
        file = os.path.join(video_clips_dir, file)
        video = VideoFileClip(file)
        length = video.duration
        videos_clips.append(file)
        total += length
        full_total += length
        if total >= video_len:
            full_videos.append([videos_clips, total])
            videos_clips = []
            total = 0
        elif n == videos.__len__() - 1:
            full_videos.append([videos_clips, total])
            videos_clips = []

    concat_files = []
    for n, data in enumerate(full_videos):
        clips, total_length = data
        base_name = list(map(str, [time.time(), n, clips.__len__(), total_length]))
        base_name = "ts:{}_c:{}_clips:{}_length:{}".format(*base_name)
        concat_file_name = "{}.concatfile.txt".format(base_name)
        video_file_name = "{}.mp4".format(base_name)

        concat_path = os.path.join(concat_files_dir, concat_file_name)
        outfile_path = os.path.join(final_output, video_file_name)

        with open(concat_path, "w") as concat:
            for clip in clips:
                print(f"file '../{clip}'", file=concat)
        concat_files.append([concat_path, outfile_path])

    for concat_file, output_file in concat_files:
        cmd = concat_command.format(concat_file, output_file)
        print(cmd)
        os.system(cmd)


if __name__ == "__main__":
    make_video("./19-04-2023-Wed-videos/", "./concat_files", "./final_output")
