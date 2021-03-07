#  speech2srt libs
import srt
import time
from google.cloud import speech
#  video2wav libs
from google.cloud import storage
import moviepy.editor as mp
import sox
import os
#  srt2video libs
import subprocess
import ffmpeg


def long_running_recognize(args):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition

    Args:
      storage_uri URI for audio file in GCS, e.g. gs://[BUCKET]/[FILE]
    """

    print("Transcribing {} ...".format(args['storage_uri']))
    client = speech.SpeechClient()

    # Encoding of audio data sent.
    encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "enable_word_time_offsets": True,
        "enable_automatic_punctuation": True,
        "sample_rate_hertz": args['sample_rate_hertz'],
        "language_code": args['language_code'],
        "encoding": encoding,
    }
    audio = {"uri": args['storage_uri']}

    operation = client.long_running_recognize(
        request={
            "config": config,
            "audio": audio,
        }
    )
    response = operation.result()

    subs = []

    for result in response.results:
        # First alternative is the most probable result
        subs = break_sentences(args, subs, result.alternatives[0])

    print("Transcribing finished")
    return subs


def break_sentences(args, subs, alternative):
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


def write_srt(args, subs):
    srt_file = args['out_file'] + ".srt"
    print("Writing {} subtitles to: {}".format(args['language_code'], srt_file))
    f = open(srt_file, 'w')
    f.writelines(srt.compose(subs))
    f.close()
    return


def write_txt(args, subs):
    txt_file = args['out_file'] + ".txt"
    print("Writing text to: {}".format(txt_file))
    f = open(txt_file, 'w')
    for s in subs:
        f.write(s.content.strip() + "\n")
    f.close()
    return


def speech2srt(video, language='ru', max_chars=10):  #
    audio = audiofile_name_in_Google_Storage(video)
    subs_name = video.replace('.mp4', '')
    args = {
        'storage_uri': audio,  # audiofile
        'language_code': language,
        'sample_rate_hertz': 16000,
        'out_file': subs_name,  # указывается без расширения
        'max_chars': max_chars
    }
    subs = long_running_recognize(args)
    write_srt(args, subs)
    #  write_txt(args, subs)
    return

#  _________________________
#  Speech recognition functions end here


def video2wav(video): #  video - название файла для обработки
    audiofile = video.replace(".mp4", '_audio.wav')  # делаем строковое название для аудиофайла, который будем сохранять
    # в ту же папку, где лежит видос
    clip = mp.VideoFileClip(video)
    clip.audio.write_audiofile(audiofile)
    # we've got an audiofile. Now we need to set proper settings: bitrate 16 bits, sample_rate = 16000, channels = 1
    trans_audio = audiofile.replace('_audio.wav', '.wav')
    tfm = sox.Transformer().convert(16000, 1, 16).build(audiofile, trans_audio)
    print('Created audiofile {} with proper settings'.format(trans_audio))
    # creates wav file in the same directory
    return


def upload_audiofile_in_Google_Storage(video):
    trans_audio = video.replace('.mp4', '.wav')
    #  let's upload audio file to google cloud
    print('Starting to upload {} to google storage in audiotrack-in bucket'.format(trans_audio))
    client = storage.Client()
    bucket = client.get_bucket('audiotrack-in')
    #  audiotrack-in - name of bucket(folder) in Google Cloud
    blob = bucket.blob(trans_audio)
    blob.upload_from_filename(trans_audio)
    print('Uploaded {} successfully!'.format(trans_audio))
    return


def audiofile_name_in_Google_Storage(video):
    audio = video.replace('.mp4', '.wav')
    path_to_audio = 'gs://audiotrack-in/' + audio
    return path_to_audio  # возвращает путь к аудиофайлу на Google Storage, а не сам аудиофайл


#  _________________________
#  video converting to audio and uploading it to google storage functions end here


def srt2video(input_video, input_subs):
    output_video = input_video.replace('.mp4', '_output') + '.mp4'
    #  конечное название файла: навзание видео + output.mp4
    args = ['ffmpeg', '-i', input_video, '-vf', 'subtitles={}'.format(input_subs), output_video]
    subprocess.call(args)
    print('Merged subs and video successfully!')
    return output_video  # возвращает название конечного видео


# реализовать функцию, удаляющую мусор: изначальное видео, аудио.wav, субтитры, текст (не буду его создавать)
def delete_junk(input_video):
    oldaudio = input_video.replace('.mp4', '_audio.wav')
    os.remove(oldaudio)
    print('Deleted old audio file successfully, cannot be restored')
    audio = input_video.replace('.mp4', '.wav')
    os.remove(audio)
    print('Deleted audio file from computer, copy available on Google storage')
    subs = input_video.replace('.mp4', '.srt')
    os.remove(subs)
    print('Deleted subs successfully, cannot be restored')
    #os.remove(input_video)
    #print('Deleted original video successfully, cannot be restored')
    return


def final(video):
    video2wav(video)
    upload_audiofile_in_Google_Storage(video)
    speech2srt(video, 'ru', 10)
    srt2video(video, video.replace('.mp4', '.srt'))
    delete_junk(video)


video = 'timur.mp4'
final(video)
