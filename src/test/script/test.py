import unittest

from src.core.python.Video2AudioConverter import *
from src.core.python.googleAPI import *


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.googleAPI = googleAPI("None")
        self.vid2audio = Video2AudioConverter("None")

    def test_breakSentences(self):

        video = "src/test/resources/standard-captions-example.mp4"
        self.vid2audio = Video2AudioConverter(video)
        self.vid2audio.transform()
        audio = self.vid2audio.GetAudioPath()
        self.googleAPI = googleAPI(audio)
        self.googleAPI.transform()
        subs = self.googleAPI.GetSubsName()
        with open("../resources/true-standard-captions-example.srt", 'r') as source:
            with open(subs, 'r') as instance:
                self.assertEqual(instance.readlines(), source.readlines())


if __name__ == '__main__':
    unittest.main()
