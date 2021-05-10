"""
Script que se encarga de sustituir las cadenas de traducción en los archivos CSV del proyecto
para poder utilizar las traducciones generadas con el script extract_translations.py

Parámetros pasados por consola:
CSV_PATH            -- Directorio que contiene los CSV del proyecto
TRANSLATION_FILE    -- Archivo YAML que se utilizará para sustitur las cadenas de traducción
"""

import sys
import os
import yaml
import csv


def check_args():
    if len(sys.argv) < 3:
        print("El script esperaba al menos dos argumentos.")
        print("python3 extract_translations.py CSV_PATH TRANSLATION_FILE")
        print("     CSV_PATH: Ruta hasta el directorio que contiene los CSV del proyecto")
        print("     TRANSLATION_FILE: Nombre del archivo YAML que se utilizará para traducir los datos")
        print("Ejemplo de llamada de este script:")
        print("python3 extract_translations.py ./data data.yml")
        sys.exit(1)


def translate_csv(csv_path, translation_path):
    """ Función que traduce los CSV del directorio pasado como parámetro con el archivo de traducción pasado.

    Parámetros
    csv_path            -- Directorio que contiene los CSV a traducir
    translation_path    -- Ruta hasta el archivo YAML con la traducción
    """

    translation_dict = {}
    with open(translation_path, 'r') as file:
        translation_dict = yaml.load(file, Loader=yaml.FullLoader)
        translation_dict = {v:k for k,v in translation_dict.items()}

    csv_files = [f for f in os.listdir(csv_path) if os.path.isfile(os.path.join(csv_path, f)) and f[-4:] == '.csv']
    csv_files = [f for f in csv_files if f not in ['demo_indicator.csv', 'indice.csv']]

    for file_name in csv_files:
        csv_file = open(os.path.join(csv_path, file_name), 'r', encoding='utf-8')
        new_csv_file = open(os.path.join(csv_path, 'new_%s' % file_name), 'w', encoding='utf-8')
        reader = csv.reader(csv_file)
        writer = csv.writer(new_csv_file)
        for line in reader:
            writer.writerow([i if i not in translation_dict else 'data.%s' % translation_dict[i] for i in line])

        csv_file.close()
        new_csv_file.close()

        os.remove(os.path.join(csv_path, file_name))
        os.rename(os.path.join(csv_path, 'new_%s' % file_name), os.path.join(csv_path, file_name))


if __name__ == '__main__':
    check_args()
    CSV_PATH = sys.argv[1]
    TRANSLATION_FILE = sys.argv[2]
    translate_csv(CSV_PATH, TRANSLATION_FILE)