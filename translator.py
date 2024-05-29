import re
from openai import OpenAI
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pydub import AudioSegment
from pydub.playback import play
import io
import threading
import queue
import time

client = OpenAI()

device_index = 2
sample_rate = 44100

audio_queue = queue.Queue()

english_transcriptions = []
spanish_translations = []

def record_audio():
    while True:
        print("Recording...")
        audio_data = sd.rec(int(5 * sample_rate), samplerate=sample_rate, channels=1, dtype='int16', device=device_index)
        sd.wait()
        print("Recording complete")

        wav_file = io.BytesIO()
        wav.write(wav_file, sample_rate, audio_data)
        wav_file.seek(0)

        audio_segment = AudioSegment.from_wav(wav_file)

        if np.mean(np.abs(audio_data)) > 15:
            audio_queue.put(audio_segment)
        else:
            print("No significant audio detected. Skipping this segment.")

def process_audio():
    while True:
        if not audio_queue.empty():
            audio_segment = audio_queue.get()
            mp3_file_path = "output.mp3"
            audio_segment.export(mp3_file_path, format="mp3")

            with open(mp3_file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt="."
                )

            transcription_text = transcription.text.strip()

            if not transcription_text or re.match(r'^\s*\.?\s*(\.\s*|\s*\.)*\s*$', transcription_text):
                print("No valid transcription available. Waiting for the next audio segment.")
                continue

            print(f"Transcription: {transcription_text}")
            english_transcriptions.append(transcription_text)

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0,
                messages=[
                    {"role": "system", "content": "You are a translator which translates English to Spanish. Every piece of text you receive after this you need to translate into Spanish. Only respond with the translated sentence:"},
                    {"role": "user", "content": transcription_text}
                ]
            )

            translation = completion.choices[0].message.content
            print(f"Translation: {translation}")
            spanish_translations.append(translation)

            speech_file_path = "./speech.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=translation
            )

            response.stream_to_file(speech_file_path)

            audio = AudioSegment.from_mp3(speech_file_path)
            play(audio)

            with open("english_transcriptions.txt", "w") as eng_file:
                eng_file.write("\n".join(english_transcriptions))

            with open("spanish_translations.txt", "w") as span_file:
                span_file.write("\n".join(spanish_translations))

recording_thread = threading.Thread(target=record_audio)
processing_thread = threading.Thread(target=process_audio)

recording_thread.start()
processing_thread.start()

recording_thread.join()
processing_thread.join()
