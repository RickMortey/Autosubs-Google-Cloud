from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip


class Subs2VideoAppender:
    video = None
    subs = None

    def __init__(self, video, subs):
        '''
        Fits video and subs name into class
        '''
        self.video = video
        self.subs = subs

    def transform(self, font='Arial', fontsize=100, color='white'):
        '''
        Creates video with subtitles
        '''
        generator = lambda filename: TextClip(filename, font=font, fontsize=fontsize, color=color)
        subtitles = SubtitlesClip(self.subs, generator)
        video = VideoFileClip(self.video)
        result = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))]).resize(newsize=(1080, 1920))
        result.write_videofile(self.video.replace(".mp4", "_with_subs.mp4"),
                               fps=video.fps, preset='ultrafast')
        result.close()
        video.close()

    def FinalVideo(self):
        '''
        Returns name of video with subs
        '''
        return self.video.replace(".mp4", "_with_subs.mp4")

    def __del__(self):
        '''
        Sets fields to None
        '''
        self.video = None
        self.subs = None
