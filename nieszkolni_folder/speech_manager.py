import os
import django

from django.db import connection

from nieszkolni_app.models import Binder

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from gtts import gTTS
from io import BytesIO


os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class SpeechManager:
    def __init__(self):
        pass

    def save(self, english):
        audio = gTTS(english)
        audio.save(f"{english}.mp3")
        os.system(f"{english}.mp3")
        # container = BytesIO()



            # super(Binder).save(*args, **kwargs)

        # binder = Binder(binder=audio, title=english)
        # binder.save()

        return "Saved"

    def play(self, english):
        files = Binder.objects.filter(title=english)
        print(files[0].binder.path)

        # if file.exists():
        #     os.system(file[0].binder.path)

