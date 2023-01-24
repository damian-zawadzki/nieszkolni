import os
import django

from django.db import connection

from django.conf import settings as django_settings

from nieszkolni_app.models import Binder

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from gtts import gTTS
from io import BytesIO
from pygame import mixer


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class SpeechManager:
    def __init__(self):
        pass

    def save(self, english):
        audio = gTTS(english)
        container = BytesIO()
        audio.write_to_fp(container)
        audio.save(f"{english}.mp3")

        mixer.init()
        sound = container
        sound.seek(0)
        mixer.music.load(sound, "mp3")
        mixer.music.play()

        return "Saved"