#!/usr/bin/python
# -*- coding: utf-8 -*-

# import shutil
import csv
import re
from overrides import *
from sdg import open_sdg
import yaml
from edatos.services import common_metadata, statistical_resources, structural_resources
from edatos.utils import json, i18n, csv as csv_utils, opensdg

INDEX_FILEPATH = "data/indice_{}.csv"
CONFIG_FILE = "config_data.yml"
HEADER_TRANSLATIONS = {
    "es": ["Indicador", "Nombre"],
    "en": ["Indicator", "Name"],
    "ca": ["Indicador", "Nom"],
}


def create_index_csv():
    """
    Método que generará el índice para la correlación de cada serie con su nombre.
    """
    with open(CONFIG_FILE, 'r') as stream:
        languages = yaml.safe_load(stream)['languages']
        print("Lenguajes detectados: ", languages)

    for language in languages:
        with open(INDEX_FILEPATH.format(language), 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            if language in HEADER_TRANSLATIONS:
                header_i18n = HEADER_TRANSLATIONS[language]
            else:
                print(f"Advertencia: no se ha encontrado el header traducido al idioma {language}, por lo que se "
                      f"usará por defecto el español")
                header_i18n = HEADER_TRANSLATIONS['es']
            csv_writer.writerow(header_i18n)
            with open(f'translations/{language}/subindicator.yml', 'r', encoding="utf-8") as translations_file:
                for line in translations_file.readlines():
                    match = re.search(r'(.*)-nombre:\s?"(.*)"', line)
                    if match:
                        csv_writer.writerow([str(match.groups()[0]), str(match.groups()[1])])

def build_sources():

    config = common_metadata.initialize_properties(config='config_data.yml')

    collection_url = statistical_resources.urn_to_url(config['statistical_resources_rest'], config['root_collection'])
    collection = json.download(collection_url) 
    
    organisation_url = structural_resources.urn_to_url(config['structural_resources_rest'], config['organisation'])
    organisation = json.download(organisation_url)
    
    meta_from_csv = csv_utils.load_indexed_csv('indicator_key', 'meta/meta.csv')
    meta_from_csv = opensdg.setup_indicators_navigation(meta_from_csv)
    
    statistical_resources.process_nodes(collection, config, meta_from_csv, organisation)

if __name__ == "__main__":

    # TODO modificar el pipeline para que esto se ejecute durante el proceso de build
    # build_sources()
                
    # Validate the indicators.
    print("Validando datos...")
    validation_successful = open_sdg.open_sdg_check(config='config_data.yml')

    # If everything was valid, perform the build.
    if not validation_successful:
        raise Exception('There were validation errors. See output above.')
    else:
        print("Creando índice...")
        create_index_csv()
        print("Construyendo datos...")
        open_sdg.open_sdg_build(config='config_data.yml')
