class Cleaner:
    def __init__(self):
        pass

    def clean_quotation_marks(self, text):
        text = text.replace('"', "")
        text = text.replace("'", "’")

        return text

    def convert_acitivty_points_entry(self, entry):
        try:
            point_raw = re.search(r";\d+$|;-\d+$", entry).group()
            point = re.sub(";", "", point_raw)
            point = int(point)

            description_raw = re.search(r"\w.+;", entry).group()
            description = re.sub(";", "", description_raw)

            history = (description, point)

        except Exception as e:
            pass

        return history
