from Video2AudioConverter import *
from googleAPI import *
from Subs2VideoAppender import *


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video",
        type=str,
        default="/home/timur/study/MIPT/python_MIPT/autosubs_mipt_python_project/examples/test/timur.mp4",
    )
    parser.add_argument(
        "--language_code",
        type=str,
        default="ru",
    )
    parser.add_argument(
        "--max_chars",
        type=int,
        default=8,
    )
    args = parser.parse_args()
    video = args.video
    language = args.language_code
    max_chars = args.max_chars

    convert2audio = Video2AudioConverter(video)
    convert2audio.transform()
    audio = convert2audio.GetAudioPath()

    transcribeSubs = googleAPI(audio)
    transcribeSubs.transform(language, max_chars)
    subs = transcribeSubs.GetSubsName()

    subsAdding = Subs2VideoAppender(video, subs)
    subsAdding.transform()
    finalVideo = subsAdding.FinalVideo()

    print("Video {} with subs has been successfully created!".format(finalVideo))


if __name__ == "__main__":
    main()
