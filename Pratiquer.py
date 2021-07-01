import os
import boto3
import time
import random
import pandas as pd
import numpy as np
import json
from pathlib import Path
import vlc
import pyautogui
from mutagen.mp3 import MP3


# Setting volume (Windows) for automated Win task scheduling to ensure sound is always audible
for _ in range(50):
    pyautogui.press('volumedown')
    time.sleep(0.05)
for _ in range(10):
    pyautogui.press('volumeup')
    time.sleep(0.05)

# -------------------------------------------------------------------------------
# ---------------------------------- Globals ------------------------------------
# -------------------------------------------------------------------------------

DIRNAME = os.path.dirname(os.path.realpath(__file__))
AUDIO_DIRNAME = os.path.join(DIRNAME, 'audios')

# -------------------------------------------------------------------------------
# -------------------------- Setting Up Amazon Polly ----------------------------
# -------------------------------------------------------------------------------

# Get credentials data from separate file
creds = json.load(open('creds.json',))


# Amazon Polly client
polly = boto3.Session(
    aws_access_key_id=creds['amazon_polly']['aws_access_key_id'],
    aws_secret_access_key=creds['amazon_polly']['aws_secret_access_key'],
    region_name=creds['amazon_polly']['region_name']).client('polly')

# Amazon Polly Voice IDs
en_voice_ids = ['Salli','Kendra','Joey']
# de_voice_ids = ['Vicki']
fr_voice_ids = ['Lea', 'Celine', 'Mathieu']


def audio_file_duration(path):
    return MP3(path).info.length


# -------------------------------------------------------------------------------
# ------------------------- Get vocabulary list file ----------------------------
# -------------------------------------------------------------------------------

vocablist = pd.read_excel(os.path.join(DIRNAME,"Liste des mots.xlsx"))[['nr','word_fr','word_en','sent_fr','sent_en']]
vocablist = vocablist.dropna(thresh=5)
vocablist['nr'] = vocablist['nr'].astype(int)
vocablist = vocablist.set_index('nr')
vocab_idx_list = list(vocablist.index)


while True:

    vocab_idx_list = list(vocablist.index)

    if len(vocab_idx_list) == 0:
        break

    sample_idx = None
    while sample_idx not in vocab_idx_list:
        if vocab_idx_list[0] != vocab_idx_list[-1]:
            # Sample words using a triangular distribution: newer word entries to be more present during recall
            sample_idx = int(np.random.triangular(vocab_idx_list[0],vocab_idx_list[-1],vocab_idx_list[-1]))
        else:
            sample_idx = vocab_idx_list[0]

    row = vocablist.loc[sample_idx, :]
    print(row['word_fr'], "\t", row['word_en'])
    print(row['sent_fr'])
    print(row['sent_en'])

    # create row id by increasing df row id by one to avoid 00000 (for filenames)
    row_id = str(sample_idx).zfill(5)

    # flags to know if it is the first (fast) or second (slow) pronunciation
    first_fr = True

    for col in ['word_en','word_fr','sent_fr','sent_en','sent_fr']:

        if "fr" in col: voice_id_list = fr_voice_ids; lang_code = 'fr-FR'
        elif "en" in col: voice_id_list = en_voice_ids; lang_code = 'en-US'

        # sample a random speaker - we will check if, from this particular speaker, we already have a recording
        speaker = random.sample(voice_id_list,1)[0]

        # if entry is not empty
        if not pd.isnull(row[col]):

            if (not first_fr) and col == "sent_fr":
                # check if audio file already exists
                if os.path.isfile(os.path.join(AUDIO_DIRNAME, f"{row_id}_{col}_{speaker}_slow.mp3")):

                    # get duration of audio
                    try:
                        audio_duration = audio_file_duration(os.path.join(AUDIO_DIRNAME, row_id + f"_{col}_{speaker}_slow.mp3"))
                    except:
                        audio_duration = 1
                    # play sound
                    vlc.MediaPlayer(os.path.join(AUDIO_DIRNAME, f"{row_id}_{col}_{speaker}_slow.mp3")).play()
                    # wait for a duration equivalent to the duration of audio to ensure playsound doesn't cut end of sound
                    time.sleep(max(audio_duration,1))

                # if file doesn't yet exist, create it
                else:
                    response = polly.synthesize_speech(
                        VoiceId=speaker,
                        LanguageCode=lang_code,
                        OutputFormat='mp3',
                        TextType='ssml',
                        Text= "<speak><prosody rate='90%'><break time='0.3s'/>" + row[col] + "</prosody></speak>"
                    )

                    file = open(os.path.join(AUDIO_DIRNAME, f"{row_id}_{col}_{speaker}_slow.mp3"), 'wb')
                    file.write(response['AudioStream'].read())
                    file.close()

                    # get duration of audio
                    try:
                        audio_duration = audio_file_duration(os.path.join(AUDIO_DIRNAME, f"{row_id}_{col}_{speaker}_slow.mp3"))
                    except:
                        audio_duration = 1
                    # play sound
                    vlc.MediaPlayer(Path(AUDIO_DIRNAME) / f"{row_id}_{col}_{speaker}_slow.mp3").play()
                    # wait for a duration equivalent to the duration of audio to ensure playsound doesn't cut end of sound
                    time.sleep(max(audio_duration,1))

            else:
                # check if audio file already exists
                if os.path.isfile(os.path.join(AUDIO_DIRNAME, row_id + f"_{col}_{speaker}.mp3")):

                    # get duration of audio
                    try:
                        audio_duration = audio_file_duration(os.path.join(AUDIO_DIRNAME, row_id + f"_{col}_{speaker}.mp3"))
                    except:
                        audio_duration = 1
                    # play sound
                    vlc.MediaPlayer(Path(AUDIO_DIRNAME) / f"{row_id}_{col}_{speaker}.mp3").play()
                    # wait for a duration equivalent to the duration of audio to ensure playsound doesn't cut end of sound
                    time.sleep(max(audio_duration,1))

                # if file doesn't yet exist, create it
                else:
                    if lang_code == 'en-US':
                        response = polly.synthesize_speech(
                            Engine='neural',
                            VoiceId=speaker,
                            LanguageCode=lang_code,
                            OutputFormat='mp3',
                            TextType='ssml',
                            Text= "<speak><prosody rate='90%'><break time='0.3s'/>" + row[col] + "</prosody></speak>"
                        )
                    else:
                        response = polly.synthesize_speech(
                            VoiceId=speaker,
                            LanguageCode=lang_code,
                            OutputFormat='mp3',
                            TextType='ssml',
                            Text= "<speak><prosody rate='85%'><break time='0.1s'/>" + row[col] + "</prosody></speak>"
                        )

                    file = open(Path(AUDIO_DIRNAME) / f"{row_id}_{col}_{speaker}.mp3", 'wb')
                    file.write(response['AudioStream'].read())
                    file.close()

                    # get duration of audio
                    try:
                        audio_duration = audio_file_duration(Path(AUDIO_DIRNAME) / f"{row_id}_{col}_{speaker}.mp3")
                    except:
                        audio_duration = 1

                    # play sound
                    vlc.MediaPlayer(Path(AUDIO_DIRNAME) / f"{row_id}_{col}_{speaker}.mp3").play()

                    # wait for a duration equivalent to the duration of audio to ensure playsound doesn't cut end of sound
                    time.sleep(max(audio_duration,1))

        if col == "sent_fr": first_fr = False

    time.sleep(1.5)

    # remove randomly sampled row index
    vocablist = vocablist.drop(sample_idx,axis=0)
    print("="*100)