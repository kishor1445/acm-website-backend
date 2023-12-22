from typing import List


def get_dict(data, description) -> List[dict]:
    title = [x[0] for x in description]
    return [dict(zip(title, x)) for x in data]


def get_dict_one(data, description) -> dict:
    title = [x[0] for x in description]
    return dict(zip(title, data))


def check_not_none(data: dict, ignore: list) -> bool:
    for k, v in data.items():
        if k in ignore:
            continue
        if isinstance(v, str) and v.strip() == "":
            return False
    return True


def event_responses_200():
    return {
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "events": [
                            {
                                "id": "string",
                                "name": "string",
                                "description": "string",
                                "venue": "string",
                                "start": "datetime",
                                "end": "datetime",
                                "link": "string",
                            }
                        ]
                    }
                }
            },
        }
    }
