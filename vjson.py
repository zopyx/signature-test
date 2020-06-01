from jsonschema import validate
import json

with open('schema.json') as fp:
    schema = json.load(fp)

with open('catalog.json') as fp:
    data = json.load(fp)

validate(instance=data, schema=schema)
