import xlrd
import re

book=xlrd.open_workbook('rechner.xlsx')
sheet=book.sheet_by_index(0)

num_rows = sheet.nrows
num_cols = sheet.ncols

def is_question_number(s):
    return re.match('^\d*\.\d$', s) is not None

def is_question_level(s, level=1):
    if level == 1:
        return s.count(".") == 0
    elif level == 2:
        return s.count(".") == 1
    raise ValueError(s)


questions = dict()
algorithm = {}

for row in range(1, num_rows):
    q_number = sheet.cell(row, 0).value
    q_text = sheet.cell(row, 1).value
    q_description= sheet.cell(row, 2).value
    q_label = sheet.cell(row, 3).value

    if not is_question_number(q_number):
        continue
    print(q_number, q_text, q_description)

    first_number = q_number.split(".")[0]
    if first_number not in questions:
        questions[first_number] = dict(
                question=q_text,
                desription=q_description, 
                labels=dict())
    questions[first_number]['labels'][q_number] = q_label

for col in range(4, num_cols):
    options = []
    for row in range(1, num_rows - 1): 
        value = sheet.cell(row, col).value
        if value.lower() != 'x':
            continue
        question_number = sheet.cell(row, 0). value
        options.append(question_number)
    result = sheet.cell(num_rows - 1, col).value
    options_key = '|'.join(options)
    algorithm[options_key] = dict(
            options=options,
            result=result)

# process RESULT row

import pprint
pprint.pprint(questions)
pprint.pprint(algorithm)
