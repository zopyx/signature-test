import os
import re
import pprint
import xlrd
from typeguard import typechecked

from attrdict import AttrDict

@typechecked
def is_question_number(number: str):
    """ Check if the given `number` is in the format 
        <number.<number>
    """
    return re.match(r"^\d*\.\d$", number) is not None


@typechecked
def normalized(s: str):
    """ create a lowercase normalized representation of `s`"""
    return s.strip().lower().replace(" ", "_")


class MissingHeader(Exception):
    """ Exception for a missing header line in Excel sheet """

    def __init__(self, header_name: str):
        self.header_name = header_name

    def __str__(self):
        return f"{self.__class__.__name__}: {self.header_name}"

    __repr__ = __str__


class UnknownHeader(MissingHeader):
    """ Exception for unknown header line in Excel sheet"""


class NoAlgorithmResult(Exception):
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __str__(self):
        return f"{self.__class__.__name__}: Result reference missing in row {self.row}, column {self.col}"

    __repr__ = __str__


class NoValidOption(Exception):
    def __init__(self, value: str, row: int, col: int):
        self.value = value
        self.row = row
        self.col = col

    def __str__(self):
        return f"{self.__class__.__name__}: Invalid option '{self.value}' in  row {self.row}, column {self.col}"

    __repr__ = __str__


class ParserError(Exception):
    """ Parser error """

    def __init__(self, message, exception=None, errors=[]):
        self.message = message
        self.exception = exception
        self.errors = errors

    def __str__(self):
        return f"{self.__class__.__name__}\nexception: {self.exception}\nerrors: {self.errors}"

    __repr__ = __str__



expected_headers = ["Question", "Number", "Description", "Result", "Answer label"]
valid_options = ['x', 'yes', 'no']

class SheetParser:
    """ Excelsheet parser """
    
    def __init__(self):
        self.questions = AttrDict()
        self.algorithm = AttrDict()
        self.headers = AttrDict()
        self.num_rows = self.num_cols = 0
        self.sheet = None
        self.errors = []

    @typechecked
    def open_sheet(self, excel_filename: str):
        book = xlrd.open_workbook(excel_filename)
        self.sheet = book.sheet_by_index(0)
        self.num_rows = self.sheet.nrows
        self.num_cols = self.sheet.ncols

    @typechecked
    def parse(self, excel_filename: str):

        if not os.path.exists(excel_filename):
            raise IOError(f"Excel file '{excel_filename}' does not exist")

        try:
            self._parse(excel_filename)
        except Exception as e:
            raise ParserError(f"Unable to parse Excel file '{excel_filename}': {e}", exception=e, errors=self.errors)

        if self.errors:
            raise ParserError(f"Parsed Excel file '{excel_filename}' contains errors: {self.errors}", errors=self.errors)


    @typechecked
    def _parse(self, excel_filename: str):
        self.open_sheet(excel_filename)
        self.parse_headers()
        self.parse_questions()
        self.parse_algorithm()

    def parse_headers(self):
        for col in range(0, self.num_cols):
            value = self.sheet.cell(0, col).value
            value = normalized(value)
            if value not in self.headers:
                self.headers[value] = col

        for name in expected_headers:
            if normalized(name) not in self.headers:
                self.errors.append(MissingHeader(name))

        expected_headers_normalized = [normalized(name) for name in expected_headers]
        for name in self.headers:
            if name not in expected_headers_normalized:
                self.errors.append(UnknownHeader(name))

    def parse_questions(self):

        cell = self.sheet.cell
        for row in range(1, self.num_rows):
            q_number = cell(row, self.headers.number).value
            q_text = cell(row, self.headers.question).value
            q_description = cell(row, self.headers.description).value
            q_label = cell(row, self.headers.answer_label).value

            if not is_question_number(q_number):
                continue

            first_number = q_number.split(".")[0]
            if first_number not in self.questions:
                self.questions[first_number] = AttrDict(
                    question=q_text, description=q_description, labels=dict()
                )
            self.questions[first_number]["labels"][q_number] = q_label

    def parse_algorithm(self):
        for col in range(self.headers.result, self.num_cols):
            options = []
            for row in range(1, self.num_rows - 1):
                value = self.sheet.cell(row, col).value
                value = value.lower()
                if not value:
                    continue
                if value not in valid_options:
                    self.errors.append(NoValidOption(value, row+1, col+1))
                question_number = self.sheet.cell(row, 0).value
                options.append(question_number)

            # the last row contains the result (references)
            result = self.sheet.cell(self.num_rows - 1, col).value
            if not result:
                self.errors.append(NoAlgorithmResult(self.num_rows, col + 1))

            options_key = "|".join(options)
            options_as_text = []
            for option in options:
                d = self.questions[option.split(".")[0]]
                options_as_text.append(f"{d.question}={d.labels[option]}")
            self.algorithm[options_key] = AttrDict(
                options=options, options_as_text=options_as_text, result=result
            )


def main():

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default="rechner.xlsx")
    options = parser.parse_args()

    s_parser = SheetParser()
    s_parser.parse(options.filename)

    pprint.pprint(s_parser.headers)
    pprint.pprint(s_parser.questions)
    pprint.pprint(s_parser.algorithm)
    pprint.pprint(s_parser.errors)


if __name__ == "__main__":
    main()
