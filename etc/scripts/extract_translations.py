"""
Script que se encarga de extraer las cadenas de traducción de los archivos CSV del proyecto y
generar un archivo YAML de traducción que pueda ser posteriormente incluido en el directorio
translations.

Parámetros pasados por consola:
CSV_PATH            -- Directorio que contiene los CSV del proyecto
TRANSLATION_FILE    -- Archivo YAML que se creará con las cadenas de traducción
"""

import os
import unidecode
import csv
import sys


def check_args():
    if len(sys.argv) < 3:
        print("El script esperaba al menos dos argumentos.")
        print("python3 extract_translations.py CSV_PATH TRANSLATION_FILE")
        print("     CSV_PATH: Ruta hasta el directorio que contiene los CSV del proyecto")
        print("     TRANSLATION_FILE: Nombre del archivo YAML que se generará")
        print("Ejemplo de llamada de este script:")
        print("python3 extract_translations.py ./data data.yml")
        sys.exit(1)


def clean_key(k):
    """ Función que limpia las claves para el archivo YAML y que no de error.
        Además se hace una limpieza de palabras de enlace para acortar las claves.

    Parámetros:
    k -- Cadena de texto con la clave
    """
    return  unidecode.unidecode(k.replace(' ', '_')
                                 .replace(':', '')
                                 .replace('.', '')
                                 .replace(',', '')
                                 .replace('(', '')
                                 .replace(')', '')
                                 .replace('%', '')
                                 .replace('_de_', '_')
                                 .replace('_los_', '_')
                                 .replace('_las_', '_')
                                 .replace('_el_', '_')
                                 .replace('_la_', '_')
                                 .replace('_por_', '_')
                                 .replace('_en_', '_')
                                 .replace('_con_', '_')
                                 .replace('_que_', '_')
                                 .replace('_del_', '_')
                                 .replace('_o_', '_')
                                 .replace('_a_', '_')
                                 .replace('_y_', '_')
                                 .lower())


def extract_translations(csv_path, translation_file):
    """ Función que extrae las cadena traducibles de los archivos CSV ubicados en la ruta
        pasada como parámetro en esta función y genera un archivo YAML con el nombre que se pasa
        también como parámetro que contiene dichas traducciones.

    Parámetros
    csv_path            -- Directorio que contiene los CSV a traducir
    translation_file    -- Archivo YAML que se va a crear con las traducciones
    """
    csv_files = [f for f in os.listdir(csv_path) if os.path.isfile(os.path.join(csv_path, f)) and f[-4:] == '.csv']
    csv_files = [f for f in csv_files if f not in ['demo_indicator.csv', 'indice.csv']]

    headers = []
    desagregaciones = []

    for csv_name in csv_files:
        with open(os.path.join(csv_path, csv_name), 'r', encoding='utf-8', newline='') as file:
            csv_reader = csv.reader(file)
            current_headers = csv_reader.__next__()
            headers.extend([i for i in current_headers if i not in ['Year', 'Units', 'Value']])
            for row in csv_reader:
                desagregaciones.extend([i for i in row if current_headers[row.index(i)] not in ['Year', 'Territorio', 'Value']])

    headers = [i for i in set(headers) if i != '']
    desagregaciones = [i for i in set(desagregaciones) if i != '']

    with open(translation_file, 'w', encoding='utf-8') as writer:
        for h in headers:
            writer.write('%s: "%s"\n' % (clean_key(h), h))

        for d in desagregaciones:
            writer.write('%s: "%s"\n' % (clean_key(d), d))


if __name__ == '__main__':
    check_args()
    CSV_PATH = sys.argv[1]
    TRANSLATION_FILE = sys.argv[2]
    extract_translations(CSV_PATH, TRANSLATION_FILE)