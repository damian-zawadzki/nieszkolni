class Cleaner:
    def __init__(self):
        pass

    def clean_quotation_marks(self, text):
        text = text.replace('"', "")
        text = text.replace("'", "’")

        return text