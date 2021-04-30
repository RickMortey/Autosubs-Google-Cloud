import moviepy.editor as mp
import sox
import os

class Video2AudioConverter:
    video = None
    audio = None

    def __init__(self, video):
        '''
        Fits video into class, also gives name to the future .wav file
        '''
        self.video = video
        self.audio = video.replace(".mp4", ".wav")

    def transform(self):
        '''
        Creates audiotrack of the video with given parameters
        '''
        if self.video is None:
            print("Error! Video is not initialized")
            raise SystemExit
        audioFileName = self.video.replace(".mp4", '_audio.wav')
        clip = mp.VideoFileClip(self.video)
        clip.audio.write_audiofile(audioFileName)
        sox.Transformer().convert(16000, 1, 16).build(audioFileName, audioFileName.replace("_audio.wav", ".wav"))
        os.remove(audioFileName) # removes extra file which was required for correct work of FFMPEG
        print('Created audiofile {} with proper settings'.format(audioFileName.replace("_audio.wav", ".wav")))
        return

    def GetAudioPath(self):
        '''
        Returns a path to audio file
        '''
        return self.audio

    def __del__(self):
        '''
        Sets fields to None
        '''
        self.video = None
        self.audio = None
