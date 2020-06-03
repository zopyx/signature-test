import re
import pprint
import xlrd
from attrdict import AttrDict


def is_question_number(number):
    return re.match(r"^\d*\.\d$", number) is not None


class SheetParser:
    def __init__(self):
        self.questions = AttrDict()
        self.algorithm = AttrDict()
        self.num_rows = self.num_cols = 0
        self.sheet = None

    def open_sheet(self):
        book = xlrd.open_workbook("rechner.xlsx")
        self.sheet = book.sheet_by_index(0)
        self.num_rows = self.sheet.nrows
        self.num_cols = self.sheet.ncols

    def parse(self):
        self.open_sheet()
        self.parse_questions()
        self.parse_algorithm()

    def parse_questions(self):
        for row in range(1, self.num_rows):
            q_number = self.sheet.cell(row, 0).value
            q_text = self.sheet.cell(row, 1).value
            q_description = self.sheet.cell(row, 2).value
            q_label = self.sheet.cell(row, 3).value

            if not is_question_number(q_number):
                continue

            first_number = q_number.split(".")[0]
            if first_number not in self.questions:
                self.questions[first_number] = AttrDict(
                    question=q_text, description=q_description, labels=dict()
                )
            self.questions[first_number]["labels"][q_number] = q_label

    def parse_algorithm(self):
        for col in range(4, self.num_cols):
            options = []
            for row in range(1, self.num_rows - 1):
                value = self.sheet.cell(row, col).value
                if value.lower() != "x":
                    continue
                question_number = self.sheet.cell(row, 0).value
                options.append(question_number)
            result = self.sheet.cell(self.num_rows - 1, col).value
            options_key = "|".join(options)
            options_as_text = []
            for option in options:
                d = self.questions[option.split(".")[0]]
                options_as_text.append(f"{d.question}={d.labels[option]}")
            self.algorithm[options_key] = AttrDict(
                options=options, options_as_text=options_as_text, result=result
            )


def main():

    parser = SheetParser()
    parser.parse()

    pprint.pprint(parser.questions)
    pprint.pprint(parser.algorithm)


if __name__ == "__main__":
    main()
