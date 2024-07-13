import glob
import json
import os.path

from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
import ffmpeg
from sys import argv
from moviepy.editor import VideoFileClip, concatenate_videoclips


API_KEY = 'AIzaSyCeTZtv9BC4FLVrmiJjd8L_GfuYM3V2UuQ'
video_output = "temp"

youtube = build(
    serviceName='youtube',
    version='v3',
    developerKey=API_KEY
)



# Functions
def get_video_files_from_folder(folder_path):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in video_extensions]

def concatenate_videos(video_files, output_path):
    clips = [VideoFileClip(video) for video in video_files]
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_path, codec="libx264")

def download(video_id: str, folder_path: str = None):
    if folder_path is None:
        output_directory = '{}/%(title)s.%(ext)s'.format(video_output)
    else:
        output_directory = '{}/%(title)s.%(ext)s'.format(folder_path)
    video_option = {
        "format": "best",
        'outtmpl': output_directory,
    }

    with YoutubeDL(video_option) as ydl:
        ydl.download([video_id])

def get_videos(playlist_id: str):
    global youtube

    video_ids = []
    next_page_token = None
    print("[INFO] get videos. playlist_id : {}".format(playlist_id))
    while True:
        # YouTube Data APIを使用して再生リストのアイテムを取得します
        try:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,  # 1回のリクエストで取得する最大件数
                pageToken=next_page_token
            )
            response = request.execute()

            # 動画IDを抽出します
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                if video_id in video_ids:
                    return video_ids
                print("[INFO] Add video_id : {}".format(video_id))
                video_ids.append(video_id)

            # 次のページのトークンを取得します
            next_page_token = response.get('nextPageToken')


            # 次のページが存在しない場合、ループを終了します
            if next_page_token is None:
                break
            print("[LOG] go to next page. nextPageToken : {}".format(next_page_token))
        except:
            print("Playlist is not found.")
            return

    return video_ids

def main():

    if argv[1] == "-help":
        help_text = "If you want to download a single video\nCommand : ydl video VIDEO_ID\nIf you want to download all the videos in a playlist\nCommad : ydl list short PLAYLIST_ID\nIf you want to download and merge all the videos in a playlist\nCommand : ydl list long PLAYLIST_ID"
        print(help_text)
        return



    if os.path.isdir(video_output):
        files = glob.glob("./{}/*".format(video_output))
        for video in files:
            print("[LOG] Remove video. title : {}".format(video))
            os.remove(video)
        pass
    else:
        os.mkdir(video_output)
        pass


    if len(argv) == 1:
        while True:
            command = input("Command or video_id $ ")
            if command == "exit":
                return
            else:
                download(command, "OutPut")
            pass

    elif len(argv) == 3:
        download_type = argv[1]
        if download_type == 'video':
            download(argv[2], "OutPut")
            print("[info] video installed.\nexit")

    elif len(argv) ==4:
        download_type = argv[1]
        if download_type == 'list':
            video_type = argv[2]
            playlist_id = argv[3]

            videos = get_videos(playlist_id=playlist_id)

            if video_type == "short":
                for video_id in videos:
                    print("[info] Begin download video_id : " + video_id)
                    download(video_id=video_id, folder_path="OutPut")
                return

            elif video_type == "long":
                for video_id in videos:
                    print("[info] Begin download video_id : " + video_id)
                    download(video_id=video_id)

                OutPut = input("OutPut Video Name $ ")
                OutPut_Path = "./OutPut/{}.mp4".format(OutPut)
                if not os.path.exists("OutPut"):
                    os.mkdir("OutPut")
                videos = get_video_files_from_folder("./{}".format(video_output))
                concatenate_videos(videos, OutPut_Path)
                doYouPlay = input('Do you play this movie background ( y / n ) ? ').lower()
                if doYouPlay == 'y' or doYouPlay == "yes":
                    os.system("start {}".format(OutPut_Path))
                    return
                elif doYouPlay == 'n' or doYouPlay == "no":
                    return





    else:
        print("Command is 'ydl [video / list] [video_id / list_id]'")


    return

if __name__ == '__main__':
    main()