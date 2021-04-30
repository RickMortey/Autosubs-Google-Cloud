import io
import srt
import time
from google.cloud import speech
from moviepy.editor import *


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/timur/study/MIPT/python_MIPT/autosubs_mipt_python_project/src/core/resources/ml-dev.json"

class googleAPI:
    audio = None
    subs = None

    def __init__(self, audio):
        """
        Gives value to the audio, subs
        """
        self.audio = audio
        self.subs = audio.replace(".wav", ".srt")

    def recognize(self, args):
        """
        Transcribe long audio file from Cloud Storage using asynchronous speech recognition

        Args:
            storage_uri - URI for audio file in GCS, e.g. gs://[BUCKET]/[FILE]
            language_code - language google should recognize, e.g. ru
            sample_rate_hertz - hertz rate of audio file, e.g. 16000
            out_file - name subtitles should be called, e.g. mySubs.srt
            max_chars - maximum amount of chars which should be displayed on a frame, doesn't break words into syllables, e. g. 10
        """

        print("Transcribing {} ...".format(self.audio))

        client = speech.SpeechClient()
        with io.open(self.audio, "rb") as audio_file:
            content = audio_file.read()
        """
         Note that transcription is limited to a 60 seconds audio file.
         Use a GCS file for audio longer than 1 minute.
        """
        audio = speech.RecognitionAudio(content=content)

        # Encoding of audio data sent.
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        config = {
            "enable_word_time_offsets": True,
            "enable_automatic_punctuation": True,
            "sample_rate_hertz": args['sample_rate_hertz'],
            "language_code": args['language_code'],
            "encoding": encoding,
        }

        response = client.recognize(config=config, audio=audio)
        subs = []

        for result in response.results:
            # First alternative is the most probable result
            subs = self.break_sentences(args, subs, result.alternatives[0])

        print("Transcribing finished")
        return subs

    def break_sentences(self, args, subs, alternative):
        """
        Transforms plain text into srt-readable text

        Args:
            args - arguments are the same which were passed into long_running_recognize function
            subs - srt-readable text (look at the examples)
            alternative - words that have been recognized, best ones
        """
        firstword = True
        charcount = 0
        idx = len(subs) + 1
        content = ""

        for w in alternative.words:
            if firstword:
                # first word in sentence, record start time
                start_hhmmss = time.strftime('%H:%M:%S', time.gmtime(
                    w.start_time.seconds))
                start_ms = int(w.start_time.microseconds / 1000)
                start = start_hhmmss + "," + str(start_ms)

            charcount += len(w.word)
            content += " " + w.word.strip()

            if ("." in w.word or "!" in w.word or "?" in w.word or
                    charcount > args['max_chars'] or
                    ("," in w.word and not firstword)):
                # break sentence at: . ! ? or line length exceeded
                # also break if , and not first word
                end_hhmmss = time.strftime('%H:%M:%S', time.gmtime(
                    w.end_time.seconds))
                end_ms = int(w.end_time.microseconds / 1000)
                end = end_hhmmss + "," + str(end_ms)
                subs.append(srt.Subtitle(index=idx,
                                         start=srt.srt_timestamp_to_timedelta(start),
                                         end=srt.srt_timestamp_to_timedelta(end),
                                         content=srt.make_legal_content(content)))
                firstword = True
                idx += 1
                content = ""
                charcount = 0
            else:
                firstword = False
        return subs

    def write_srt(self, args, subs):
        """
        Transforms srt-readable text (list of sentences with timestamps) into .srt file

        Args:
            args - arguments are the same which were passed into long_running_recognize function
            subs - srt-readable text
        """
        srt_file = args['out_file'] + ".srt"
        print("Writing {} subtitles to: {}".format(args['language_code'], srt_file))
        f = open(srt_file, 'w')
        f.writelines(srt.compose(subs))
        f.close()
        return

    def GetSubsName(self):
        return self.subs

    def speech2srt(self, language='ru', max_chars=8):
        """
        Function that creates file with subtitles in the same folder where video is

        Args:
            audio - audio file name
            language - subs will be on this language
            max_chars - maximum amount of chars on one frame
        """
        subs_name = self.subs.replace(".srt", "")
        args = {
            'language_code': language,
            'sample_rate_hertz': 16000,
            'out_file': subs_name,  # указывается без расширения
            'max_chars': max_chars
        }
        subs = self.recognize(args)
        self.write_srt(args, subs)
        return

    def transform(self, language='ru', max_chars=8):
        """
        Uploads audio file into Google Storage, processes it through Speech Recognition, downloads subtitles onto computer
        """
        if self.audio is None:
            print("Error: video is not initialized")
            raise SystemExit

        self.speech2srt(language, max_chars)
        return

    def __del__(self):
        '''
        Sets fields to None
        '''
        self.audio = None
        self.subs = None
