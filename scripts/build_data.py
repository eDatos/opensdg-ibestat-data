#!/usr/bin/python
# -*- coding: utf-8 -*-

# import shutil
import csv
import re
import sys
from overrides import *
from sdg import open_sdg
import yaml

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
        print("Lenguajes detectados: ", languages, file=sys.stderr)

    for language in languages:
        with open(INDEX_FILEPATH.format(language), 'w', newline='', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            if language in HEADER_TRANSLATIONS:
                header_i18n = HEADER_TRANSLATIONS[language]
            else:
                print(f"Advertencia: no se ha encontrado el header traducido al idioma {language}, por lo que se "
                      f"usará por defecto el español", file=sys.stderr)
                header_i18n = HEADER_TRANSLATIONS['es']
            csv_writer.writerow(header_i18n)
            with open(f'translations/{language}/subindicator.yml', 'r', encoding="utf-8") as translations_file:
                for line in translations_file.readlines():
                    match = re.search(r'(.*)-nombre:\s?"(.*)"', line)
                    if match:
                        csv_writer.writerow([str(match.groups()[0]), str(match.groups()[1])])

if __name__ == "__main__":

    # Validate the indicators.
    print("Validando datos...", file=sys.stderr)
    validation_successful = open_sdg.open_sdg_check(config='config_data.yml')
    # If everything was valid, perform the build.
    if not validation_successful:
        print("Se han producido errores de validación. Consulte la salida del proceso para más detalles.")
    else:
        print("Creando índice...", file=sys.stderr)
        create_index_csv()
        print("Construyendo datos...", file=sys.stderr)
        try:
            success = open_sdg.open_sdg_build(config='config_data.yml')
            if not success:
                print("Error en open_sdg_build: algún output no se generó correctamente.")
        except Exception as e:
            print(f"Error en open_sdg_build: {str(e)}")
