# Sample international string
# 'text': [
#     {'value': '8.9.1', 'lang': 'es'},
#     {'value': '8.9.1', 'lang': 'ca'}
# ]
def international_string_to_string(international_string, language):
    for item in international_string['text']:
        if item['lang'] == language:
            return item['value']
    return None