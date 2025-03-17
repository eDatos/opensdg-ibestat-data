import itertools

import pandas
import yaml
from edatos.utils import i18n, json

series_orden_attribute_id = 'SERIES_ORDEN'

def process_nodes(collection, config):
    if 'data' in collection and 'nodes' in collection['data'] and 'node' in collection['data']['nodes']:
        for node in collection['data']['nodes']['node']:
            process_node(node, config)

def process_node(node, config, parent_node = None, level=1):    
    if level == 1:
        node_type = 'objective'
    elif level == 2:
        node_type = 'meta'
    elif level == 3:
        node_type = 'indicator'
    else:
        print(f"Unsupported level {level}")
        return

    default_language = config['languages'][0]
    # Invariable between languages
    node_id = i18n.international_string_to_string(node['name'], default_language)
    print(f"Processing {node_type}: {node_id}")

    if 'dataset' in node:
        dataset_url = node['dataset']['selfLink']['href'] + ".json"
        print(f"Downloading dataset from: {dataset_url}")
        data = json.download(dataset_url)
        create_opensdg_data(data, f'data/indicator_{kebab_case(indicator_id)(node_id)}', config)
        create_opensdg_meta(data, f'meta/{kebab_case(node_id)}', config, node_id)
        create_opensdg_meta(data, f'meta/{kebab_case(node_id)}', config, node_id, parent_node)

    if 'nodes' in node and 'node' in node['nodes']:
        for child_node in node['nodes']['node']:
            process_node(child_node, config, level + 1)
            process_node(child_node, config, node, level + 1)            

def urn_to_url(base_url, urn):
    # Extraer la organización y el resourceID de la URN
    parts = urn.split('=')
    if len(parts) != 2:
        raise ValueError("URN format is incorrect")

    base_url += '/v1.0'
    resourceType = parts[0]
    if resourceType == 'urn:siemac:org.siemac.metamac.infomodel.statisticalresources.Collection':
        base_url += '/collections'
    else:
        raise ValueError("Resource type is not supported")
    organization, resource_id = parts[1].split(':')

    url = f"{base_url}/{organization}/{resource_id}.json"

    return url

def create_opensdg_data(data, output_filepath, config):   
     
    observations = data['data']['observations'].split(" | ")
    
    unit_measure_attribute = next(attr for attr in data['data']['attributes']['attribute'] if attr['id'] == config['unit_measure_id'])
    unit_measure_attribute_values = unit_measure_attribute['value'].split(" | ")

    series_orden_attribute = next(attr for attr in data['data']['attributes']['attribute'] if attr['id'] == series_orden_attribute_id)
    series_orden_attribute_values = series_orden_attribute['value'].split(" | ")

    dimensions = data['data']['dimensions']['dimension']
    metadata_dimensions = data['metadata']['dimensions']['dimension']
    totals = [dimension['representations']['total'] for dimension in dimensions]
    
    pointer = 0
    records = []
    records_by_serie = {}
    additional_columns = set()
    translations = {}   
    # Python has a pythonic way to iterate a n-dimensional array via itertools.product
    # https://stackoverflow.com/questions/45737880/how-to-iterate-over-this-n-dimensional-dataset
    # https://docs.python.org/3/library/itertools.html#itertools.product
    for idx in itertools.product(*[range(s) for s in totals]):
        # Sample idx value: (1, 11, 12, 0, 2, 0, 0, 0, 0, 0, 0, 0)
        value = observations[pointer]
        units = unit_measure_attribute_values[pointer]
        pointer += 1
        if (value == ''):
            continue

        record = {}
        record['Units'] = 'UNIDAD_MEDIDA.' + units
        record['Value'] = value

        for dimension_index, representation_index in enumerate(idx):
            dimension = dimensions[dimension_index]
            metadata_dimension = metadata_dimensions[dimension_index]            
            code = dimension['representations']['representation'][representation_index]['code']

            # Predetermined columns, they always need to exist
            header_columns = {
                'TIME_PERIOD': 'Year',
                'REF_AREA': 'general.territorio',
                'SERIES': 'SERIE_TEMPORAL.Encabezado'
            }

            dimension_id = dimension['dimensionId']
            header_column = header_columns.get(dimension_id, 'DIM_DES.' + dimension_id)
            is_obligatory_column = dimension_id in header_columns.keys()
            is_single_value = dimension['representations']['total'] == 1
            needs_translation = dimension_id not in ['TIME_PERIOD', 'REF_AREA']
            if (is_obligatory_column or not is_single_value):
                if (not is_obligatory_column): 
                    additional_columns.add('DIM_DES.' + dimension_id)
                    i18n.update_translations(translations, 'DIM_DES.' + dimension_id, metadata_dimension['name'])
                if (dimension_id == 'SERIES'):
                    # We´ll construct it like this to reuse existing translations
                    record['Serie'] = 'SERIE.SERIE_' + series_orden_attribute_values[representation_index]
                    dimension_id = 'SERIE_TEMPORAL'     
          
                representation_code = code
                if needs_translation:
                    representation_code = dimension_id + '.' + code
                    dimension_values = metadata_dimension['dimensionValues']['value']
                    dimension_value = next((val for val in dimension_values if val['id'] == code), None)
                    i18n.update_translations(translations, representation_code, dimension_value['name'])

                record[header_column] = representation_code                    

        print(record)
        records.append(record)
        record_by_serie = {
            'Year': record['Year'],
            'Units': record['Units'],
            'general.territorio': record['general.territorio'],
            'Value': record['Value']
        }
        if record['Serie'] not in records_by_serie:
            records_by_serie[record['Serie']] = []
        records_by_serie[record['Serie']].append(record_by_serie)
     
    clean_disaggregated_values(records, additional_columns)

    # Creating base CSV
    df = pandas.DataFrame(records)    
    # Trying to match order of rows and columns the same way as the original CSVs
    column_order = ['Year', 'Units', 'general.territorio', 'Serie', 'SERIE_TEMPORAL.Encabezado'] + list(additional_columns) + ['Value']
    df = df.sort_values(by=['Serie', 'Year', 'general.territorio', 'SERIE_TEMPORAL.Encabezado'], ascending=[True, True, True, True])
    df.to_csv(output_filepath + ".csv", index=False, columns=column_order)

    i18n.update_translation_files(translations)

    # Creating series CSVs
    for serie, records in records_by_serie.items():
        df = pandas.DataFrame(records)
        serie_letter = serie.split('_')[1]        
        # Trying to match order of rows and columns the same way as the original CSVs
        column_order = ['Year', 'Units', 'general.territorio', 'Value']
        df = df.sort_values(by=['Year', 'Units', 'general.territorio'], ascending=[True, True, True])      
        df.to_csv(output_filepath + '-SERIE-' + serie_letter + '.csv', index=False, columns=column_order)

# OpenSDG will show a filter facet whenever there are values for that combination, but business logic has decided against
# showing the filter for single value dimensions. This behaviour was implemented before taking into account
# both Units and SERIE_TEMPORAL. Because SERIE_TEMPORAL is no longer a group of series, we´ll only clean
# based on Units.
def clean_disaggregated_values(records, additional_columns):
    units_groups = {}
    for record in records:
        units = record.get('Units')
        if units not in units_groups:
            units_groups[units] = []
        units_groups[units].append(record)
    
    for units, units_records in units_groups.items():
        for column in additional_columns:
            unique_values = set(record.get(column, None) for record in units_records)
            if len(unique_values) == 1:
                print(f"Column {column} in unit {units} have single value: {unique_values}")
                for record in units_records:
                    if column in record:
                        record[column] = ''

# A yaml file inside a md file
def create_opensdg_meta(data, output_filepath, config, indicator_id, node):
    metadata = data['metadata']
    indicator_key = kebab_case(indicator_id)
    goal = indicator_id.split('.')[0]
    target = goal + '.' + indicator_id.split('.')[1]
    translations = {}

    meta = {
        'graph_title': i18n.update_translations(translations, f'global_indicators.{indicator_key}-graph-title', data['name']),
        'indicator_number': indicator_id,
        'indicator_name': i18n.update_translations(translations, f'global_indicators.{indicator_key}-title', node['description']),
        'indicator_sort_order': generate_indicator_sort_order(indicator_key),
        'sdg_goal': goal,
        'target_id': target,
    }

    # Convert the dictionary to a YAML string
    yaml_content = yaml.dump(meta, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
    
    # Wrap the YAML content with ---
    markdown_content = f"---\n{yaml_content}---\n"
    
    with open(output_filepath + '.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)

    i18n.update_translation_files(translations)

# Example
# indicator_id = "2.4.1"
# filename = kebab_case(indicator_id)(node_id)
# print(filename)  # Output: indicator_2-4-1
def kebab_case(indicator_id):
    return indicator_id.replace('.', '-')

# Example
# indicator_key = "2-4-1"
# output = "02-04-01"
def generate_indicator_sort_order(indicator_key):
    padded_parts = [part.zfill(2) for part in indicator_key.split('-')]
    return '-'.join(padded_parts)