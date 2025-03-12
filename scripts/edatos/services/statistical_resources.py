import itertools

import pandas
import edatos.utils.i18n as i18n
import edatos.utils.json as json

series_orden_attribute_id = 'SERIES_ORDEN'

def process_nodes(collection, config):
    if 'data' in collection and 'nodes' in collection['data'] and 'node' in collection['data']['nodes']:
        for node in collection['data']['nodes']['node']:
            process_node(node, config)

def process_node(node, config, level=1):
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
    node_id = i18n.international_string_to_string(node['name'], default_language)
    print(f"Processing {node_type}: {node_id}")

    if 'dataset' in node:
        dataset_url = node['dataset']['selfLink']['href'] + ".json"
        print(f"Downloading dataset from: {dataset_url}")
        data = json.download(dataset_url)
        transform_dataset_json_to_csvs(data, 'data/' + format_filename(node_id), config)

    if 'nodes' in node and 'node' in node['nodes']:
        for child_node in node['nodes']['node']:
            process_node(child_node, config, level + 1)

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

def transform_dataset_json_to_csvs(data, output_filepath, config):   
     
    observations = data['data']['observations'].split(" | ")
    
    unit_measure_attribute = next(attr for attr in data['data']['attributes']['attribute'] if attr['id'] == config['unit_measure_id'])
    unit_measure_attribute_values = unit_measure_attribute['value'].split(" | ")

    series_orden_attribute = next(attr for attr in data['data']['attributes']['attribute'] if attr['id'] == series_orden_attribute_id)
    series_orden_attribute_values = series_orden_attribute['value'].split(" | ")

    dimensions = data['data']['dimensions']['dimension']
    totals = [dimension['representations']['total'] for dimension in dimensions]
    pointer = 0
    records = []
    records_by_serie = {}
    additional_columns = set()
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
                if (dimension_id == 'SERIES'):
                    record['Serie'] = dimension_id.upper() + '.' + series_orden_attribute_values[representation_index]
                    dimension_id = 'SERIE_TEMPORAL'     
          
                representation_code = code
                if needs_translation:
                    representation_code = dimension_id + '.' + code

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


    # Creating series CSVs
    for serie, records in records_by_serie.items():
        df = pandas.DataFrame(records)
        serie_letter = serie.split('.')[1]        
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

# Example
# node_id = "2.4.1"
# filename = format_filename(node_id)
# print(filename)  # Output: indicator_2-4-1
def format_filename(node_id):
    formatted_id = node_id.replace('.', '-')
    return f"indicator_{formatted_id}"

