#!/usr/bin/python
# -*- coding: utf-8 -*-

# import shutil
import csv
import re
from overrides import *
from sdg import open_sdg
import yaml

INDEX_NAME = "indice.csv"
CONFIG_FILE = "config_data.yml"


def create_index_csv():
    """
    Método que generará el índice para la correlación de cada serie con su nombre.
    """
    with open(CONFIG_FILE, 'r') as stream:
        languages = yaml.safe_load(stream)['languages']

    with open('data/%s' % INDEX_NAME, 'w', newline='', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Indicador', 'Nombre castellano', 'Nombre catalán'])
        names = {}
        print("Lenguajes detectados: ", languages)
        for language in languages:
            with open(f'translations/{language}/subindicator.yml', 'r', encoding="utf-8") as translations_file:
                for line in translations_file.readlines():
                    match = re.search(r'(.*)-nombre:\s?"(.*)"', line)
                    if match:
                        indicator = str(match.groups()[0])
                        name = str(match.groups()[1])
                        if indicator in names:
                            names[indicator].append(name)
                        else:
                            names[indicator] = [name]
        for indicator, name in names.items():
            csv_writer.writerow([indicator, name[0], name[1]])


if __name__ == "__main__":
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
