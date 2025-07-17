import os
import shutil
from edatos.utils import html
from edatos.utils.yaml import yaml

base_dir = 'translations'

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

def update_translation_files(translations):    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    for lang, translation_by_lang in translations.items():
        lang_dir = os.path.join(base_dir, lang)
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        # Group translations by the first part of the key
        grouped_translations = {}
        for key, value in translation_by_lang.items():
            group, rest = key.split('.', 1)  # Divide by first point
            if group not in grouped_translations:
                grouped_translations[group] = {}
            grouped_translations[group][rest] = value
        
        for group, group_translations in grouped_translations.items():
            file_path = os.path.join(lang_dir, f'{group}.yml')
            
            # Read existing translations
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    existing_translations = yaml.load(file) or {}
            else:
                existing_translations = {}
            
            # Ignore existing translation keys
            for key, value in group_translations.items():
                if key in existing_translations and existing_translations[key] != value:
                    print(f"WARNING: Key '{key}' already exists in {file_path} with different value: \n PREVIOUS: >{existing_translations[key]}< \n      NEW: >{value}<")
            
            # Add new keys that do not exist in the file
            new_translations = {key: value for key, value in group_translations.items()}
            existing_translations.update(new_translations)
            
            # Write updated translations to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.width = 4000  # Ensure long lines are not wrapped
                yaml.dump(existing_translations, file)

def update_translations(translations, key, international_string):
    if not international_string or 'text' not in international_string:
        print(f"WARNING: international_string is empty for key '{key}'")
    else:
        for localized_string in international_string['text']:
            if localized_string['lang'] not in translations:
                translations[localized_string['lang']] = {}
        
            translations[localized_string['lang']][key] = html.remove_tags(localized_string['value'])
    return key
