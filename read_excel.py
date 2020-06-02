import xlrd
import re

book=xlrd.open_workbook('rechner.xlsx')
sheet=book.sheet_by_index(0)

num_rows = sheet.nrows

def is_question_level(s, level=1):
    if level == 1:
        return s.count(".") == 0
    elif level == 2:
        return s.count(".") == 1
    raise ValueError(s)


questions = dict()

for row in range(1, num_rows):
    q_number = sheet.cell(row, 0).value
    q_text = sheet.cell(row, 1).value
    q_description= sheet.cell(row, 2).value
    print(q_number, q_text, q_description)
    if is_question_level(q_number, 1):
        questions[q_number] = dict(
                question=q_text,
                desription=q_description, 
                labels=dict())
        questions[q_number]['labels'][q_number] = 'xx'
    elif is_question_level(q_number, 2):
        q_number2 = q_number.split('.', 1)[0]
        questions[q_number2]['labels'][q_number] = 'xx'

import pprint
pprint.pprint(questions)
