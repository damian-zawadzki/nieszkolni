from nieszkolni_folder.wordcounter import Wordcounter
from nieszkolni_folder.cleaner import Cleaner
import re


class TextAnalysis:
    def __init__(self, text):
        self.text = text
        self.text = Cleaner().clean_quotation_marks(self.text)

    def find_marks(self):
        wordcount = Wordcounter(self.text).counter()
        analysis = []

        for index in range(0, 10):
            mark = r"\\" + str(index)
            matches = re.findall(mark, self.text)
            if len(matches) == 0:
                count = 0
                description = re.search(mark, mark).group().replace("\\", "mark ")
                analysis.append((description, count, 0))
            else:
                match = matches[0]
                count = matches.count(match)
                description = match.replace("\\", "mark ")
                promile = round(count/wordcount*1000)
                analysis.append((description, count, promile))

        return analysis

    def calculate_percentage(self):
        analysis = self.find_marks()
        total_errors = sum([index[2] for index in analysis])
        analysis_with_percentage = [(index[0], index[1], str(round(index[2]/total_errors*100)) + "%") for index in analysis]

        return analysis_with_percentage

    def calculate_errors(self, error_type):
        error_types = {
            "mark 1": "major",
            "mark 2": "major",
            "mark 3": "major",
            "mark 4": "major",
            "mark 5": "major",
            "mark 6": "major",
            "mark 7": "major",
            "mark 8": "minor",
            "mark 9": "minor",
            "mark 0": "minor"
            }

        rows = self.find_marks()
        wordcount = Wordcounter(self.text).counter()

        errors = []
        for row in rows:
            if error_types.get(row[0]) == error_type:
                errors.append(row[2])

        result = round(sum(errors)/wordcount*1000)

        return result

    def convert_to_flagged_text(self):
        flagged_content = re.sub(r"\\\d", "🏁", self.text)

        return flagged_content

# descriptions = {
#     "mark 1": "articles",
#     "mark 2": "other determiners",
#     "mark 3": "prepositions",
#     "mark 4": "vocabulary and phrases",
#     "mark 5": "tenses and conjugation",
#     "mark 6": "word order",
#     "mark 7": "other issues",
#     "mark 8": "style",
#     "mark 9": "spelling",
#     "mark 0": "punctuation"
#     }