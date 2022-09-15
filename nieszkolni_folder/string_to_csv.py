import re


class StringToCsv:
    def __init__(self):
        pass

    def convert(self, text):
        lines = text.splitlines()
        pieces = [line.split(",") for line in lines]

        entries = []
        for piece in pieces:
            item = []
            entry = []
            for chunk in piece:
                if re.search(r'"', chunk) is None:
                    if len(entry) == 0:
                        item.append(chunk)
                    else:
                        entry.append(chunk)
                else:
                    if re.search(r'"$', chunk) is not None:
                        entry.append(chunk)
                        add_entry = ",".join(entry)
                        item.append(add_entry)
                        entry.clear()
                    else:
                        entry.append(chunk)

            entries.append(item)

        return entries[1:]
