import os
import shutil

base_dir = 'generated/translations'

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

def clean_translation_files():
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
        os.makedirs(base_dir)
