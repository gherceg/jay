import json


def parse(data):
    if isinstance(data, str):
        return json.loads(data)
    elif isinstance(data, dict):
        return json.dumps(data)

    return None
