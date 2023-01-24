import os
import django
from django.db import connection

import nltk

from nltk.corpus import words, wordnet, stopwords

from nieszkolni_app.models import SentenceStock
from nieszkolni_app.models import Submission
from nieszkolni_app.models import Composer

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neural_network import MLPRegressor

nltk.download('stopwords')

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class TranslationManager:
    def __init__(self):
        pass

    def run(self, english, sentence_id):
        conversion = self.convert(english, sentence_id)
        data = conversion["data"]
        sample = conversion["sample"]
        count = conversion["count"]

        alternation = self.alter(data, sample)
        lexicon = alternation["lexicon"]
        glossary = alternation["glossary"]

        check = self.spellcheck(glossary)

        dictionary = self.step_3(lexicon)
        data_matrix = self.process_data(data, dictionary)
        sample_matrix = self.process_sample(sample, dictionary)
        prediction = self.predict(data_matrix, sample_matrix)
        score = prediction["score"]
        label = prediction["label"]
        shape = prediction["shape"]

        analysis = self.analyze(check, count, score, label, shape)

        return analysis

    def convert(self, english, sentence_id):
        sample = pd.DataFrame(
            data=[(english, -1)],
            columns=["translation", "label"]
            )

        rows = SentenceStock.objects.filter(sentence_id=sentence_id)
        rows_raw = [{
            "sentence_id": row.sentence_id,
            "english": row.english,
            "label": 1}
            for row in rows
            ]

        things = Composer.objects.filter(
                sentence_id=sentence_id,
                status="graded"
                )

        things_raw_0 = [{
            "sentence_id": thing.sentence_id,
            "english": thing.translation,
            "label": 0}
            for thing in things
            if thing.result == "incorrect"
            ]

        things_raw_1 = [{
            "sentence_id": thing.sentence_id,
            "english": thing.translation,
            "label": 1}
            for thing in things
            if thing.result == "correct"
            ]

        count = len(rows) + len(things)

        data_raw = rows_raw + things_raw_0 + things_raw_1

        data = pd.DataFrame(
            data=data_raw,
            columns=["sentence_id", "english", "label"]
            )

        return {"data": data, "sample": sample, "count": count}

    def alter(self, data, sample):
        lexicon = []
        dictionary = data["english"].to_list()
        glossary = sample["translation"].to_list()
        lexicon.extend(dictionary)
        lexicon.extend(glossary)

        return {"lexicon": lexicon, "glossary": glossary}

    def spellcheck(self, glossary):
        model = CountVectorizer(
                analyzer="word",
                binary=True,
                ngram_range=(1, 1),
                min_df=0
                )

        model_data = model.fit(glossary)
        phrases = model_data.vocabulary_
        stop_words = set(stopwords.words("english"))

        check = [
            phrase in words.words()
            or phrase in wordnet.words()
            or phrase in stop_words
            for phrase in phrases
            ]

        remarks = "/".join([
            phrase for phrase in phrases
            if phrase not in words.words()
            and phrase not in wordnet.words()
            and phrase not in stop_words
            ])

        check = all(check)

        return {"check": check, "remarks": remarks}

    def step_3(self, lexicon):
        model = CountVectorizer(
                analyzer="word",
                binary=True,
                ngram_range=(1, 2),
                min_df=0
                )
        model_data = model.fit(lexicon)
        dictionary = model_data.vocabulary_

        return dictionary

    def process_data(self, data, dictionary):
        model = CountVectorizer(
                analyzer="word",
                binary=True,
                lowercase=False,
                stop_words=None,
                ngram_range=(1, 3),
                vocabulary=dictionary
                )

        model_data = model.transform(data["english"]).toarray()
        matrix = pd.DataFrame(
                data=model_data,
                columns=model.get_feature_names_out()
                )
        matrix["label"] = data["label"]
        data_matrix = matrix.to_numpy(na_value=-1)

        return data_matrix

    def process_sample(self, sample, dictionary):
        model = CountVectorizer(
                analyzer="word",
                binary=True,
                lowercase=False,
                stop_words=None,
                ngram_range=(1, 3),
                vocabulary=dictionary
                )

        model_data = model.transform(sample["translation"]).toarray()
        matrix = pd.DataFrame(
                data=model_data,
                columns=model.get_feature_names_out()
                )
        matrix["label"] = sample["label"]
        sample_matrix = matrix.to_numpy(na_value=-1)

        return sample_matrix

    def predict(self, data_matrix, sample_matrix):
        shape = f"{data_matrix.shape}/{sample_matrix.shape}"

        analysis = MLPRegressor(
                max_iter=10000,
                activation="identity",
                solver="lbfgs",
                warm_start=True
                ).fit(data_matrix[:, :-1], data_matrix[:, -1])

        calculations = analysis.predict(sample_matrix[:, :-1])

        if calculations[0] > 0.95 and calculations[0] < 1.05:
            label = 1
        else:
            label = 0

        return {"shape": shape, "label": label, "score": calculations[0]}

    def analyze(self, check, count, score, label, shape):
        if not check:
            label = 0
            method = "automatic_typo"

        elif count > 20 and (0.999 < score < 1.001 or -0.005 < score < 0.005):
            method = "automatic_confidence"

        else:
            method = "manual"

        score = round(score, 3)
        label = "correct" if label == 1 else "incorrect"
        analysis = {
            "score": score,
            "label": label,
            "method": method,
            "shape": shape
            }

        return analysis