def get_dict(data, description):
    title = [x[0] for x in description]
    return [dict(zip(title, x)) for x in data]


def get_dict_one(data, description):
    title = [x[0] for x in description]
    return dict(zip(title, data))


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
