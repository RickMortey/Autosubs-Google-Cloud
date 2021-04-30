import unittest

from src.core.resources.Video2AudioConverter import *
from src.core.resources.googleAPI import *
from src.core.resources.Subs2VideoAppender import *


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.googleAPI = googleAPI(None)
        self.vid2audio = Video2AudioConverter(None)
        self.subs2video = Subs2VideoAppender(None)

    def test_breakSentences(self):

        video = "standart-captions-example.mp4"
        self.vid2audio = Video2AudioConverter(video)
        self.vid2audio.transform()
        audio = self.vid2audio.GetAudioPath()
        self.googleAPI = googleAPI(audio)
        self.googleAPI.transform()
        subs = self.googleAPI.GetSubsName()
        with open("true-standard-captions-example.srt", 'r') as source:
            with open(subs, 'r') as instance:
                self.assertEqual(instance.readlines(), source.readlines())


if __name__ == '__main__':
    unittest.main()
