from nieszkolni_folder.cleaner import Cleaner


class Wordcounter:
    def __init__(self, text):
        self.text = text
        self.text = Cleaner().clean_quotation_marks(self.text)

    def counter(self):
        list_of_words = self.text.split()
        word_count = len(list_of_words)
        return word_count

    def linecounter(self):
        list_of_lines = self.text.splitlines()
        line_count = len(list_of_lines)

        return line_count
