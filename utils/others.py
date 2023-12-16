def get_dict(data, description):
    title = [x[0] for x in description]
    return [dict(zip(title, x)) for x in data]
