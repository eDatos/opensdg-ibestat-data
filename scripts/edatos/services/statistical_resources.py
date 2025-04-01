from io import StringIO
import itertools

import pandas
from edatos.utils import i18n, json, urn as urn_utils
from edatos.utils.yaml import yaml
from edatos.services import structural_resources

SERIES_ORDEN_ATTRIBUTE_ID = 'SERIES_ORDEN'

def process_nodes(collection, config, meta_from_csv, organisation):
    if 'data' in collection and 'nodes' in collection['data'] and 'node' in collection['data']['nodes']:
        for node in collection['data']['nodes']['node']:
            process_node(node, config, meta_from_csv, organisation)

def process_node(node, config, meta_from_csv, organisation, parent_node = None, level=1):
    node['parent'] = parent_node   
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
        dataset_url = node['dataset']['selfLink']['href'] + ".json?fields=+dimension.description"
        indicator_key = kebab_case(node_id)
        print(f"Downloading dataset from: {dataset_url}")
        data = json.download(dataset_url)
        create_opensdg_data(data, f'data/indicator_{indicator_key}', config) 
        node_meta_from_csv = meta_from_csv.get(indicator_key, {})
        create_opensdg_meta(data, f'meta/{indicator_key}', config, node_id, node, node_meta_from_csv, organisation)

    if 'nodes' in node and 'node' in node['nodes']:
        for child_node in node['nodes']['node']:
            process_node(child_node, config, meta_from_csv, organisation, node, level + 1)            

def urn_to_url(base_url, urn):
    prefix, agency_id, item_scheme_id, version, resource_id = urn_utils.split_urn(urn, False)
    base_url += '/v1.0'
    if prefix == 'urn:siemac:org.siemac.metamac.infomodel.statisticalresources.Collection':
        return f"{base_url}/collections/{agency_id}/{item_scheme_id}.json"
    else:
        raise ValueError("Resource type is not supported")

def create_opensdg_data(data, output_filepath, config):   
     
    observations = data['data']['observations'].split(" | ")
    
    unit_measure_attribute = next(attr for attr in data['data']['attributes']['attribute'] if attr['id'] == config['unit_measure_id'])
    unit_measure_attribute_values = unit_measure_attribute['value'].split(" | ")

    series_orden_attribute = next(attr for attr in data['data']['attributes']['attribute'] if attr['id'] == SERIES_ORDEN_ATTRIBUTE_ID)
    series_orden_attribute_values = series_orden_attribute['value'].split(" | ")

    dimensions = data['data']['dimensions']['dimension']
    dimensions_metadata = data['metadata']['dimensions']['dimension']
    totals = [dimension['representations']['total'] for dimension in dimensions]
    
    pointer = 0
    records = []
    records_by_serie = {}
    additional_columns = set()
    translations = {}   
    # Python has a pythonic way to iterate a n-dimensional array via itertools.product
    # https://stackoverflow.com/questions/45737880/how-to-iterate-over-this-n-dimensional-dataset
    # https://docs.python.org/3/library/itertools.html#itertools.product
    for idx in itertools.product(*[range(total) for total in totals]):
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
            metadata_dimension = dimensions_metadata[dimension_index]            
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
def create_opensdg_meta(data, output_filepath, config, indicator_id, indicator_node, node_meta_from_csv, organisation):

    translations = {}    
    default_language = config['languages'][0]

    organisation_name, organisation_url, organisation_id = structural_resources.extract_organisation_info(organisation)

    indicator_key = kebab_case(indicator_id)
    
    target_node = indicator_node['parent']
    target_id = i18n.international_string_to_string(target_node['name'], default_language)

    goal_node = target_node['parent']
    sgd_goal = i18n.international_string_to_string(goal_node['name'], default_language)    

    indicator_meta = {
        'data_non_statistical': False, # Always False

        'goal_meta_link': node_meta_from_csv.get('goal_meta_link'),
        'goal_meta_link_text': node_meta_from_csv.get('goal_meta_link_text'),

        'graph_title': i18n.update_translations(translations, f'global_indicators.{indicator_key}-graph-title', data['name']),
        'graph_type': 'line', # Always line for indicators

        'indicator_number': indicator_id,
        'indicator_definition': '', # Always empty, not found in built web
        'indicator_name': i18n.update_translations(translations, f'global_indicators.{indicator_key}-title', indicator_node['description']),
        'indicator_sort_order': generate_indicator_sort_order(indicator_key),

        'data_show_map': calculate_data_show_map(data), 
        'published': node_meta_from_csv.get('published'), # Must be True to publish
        # Use 'complete' to published indicators. Available values: notapplicable, notstarted, inprogress, complete
        'reporting_status': node_meta_from_csv.get('reporting_status'),

        'sdg_goal': sgd_goal,
        'target_name': i18n.update_translations(translations, f'global_targets.{kebab_case(target_id)}-title', target_node['description']),
        'target_id': target_id,

        'un_custodian_agency': node_meta_from_csv.get('un_custodian_agency'),
        'un_designated_tier': node_meta_from_csv.get('un_designated_tier'),
        'national_geographical_coverage': config['organisation_config']['national_geographical_coverage'],

        # Up to 12 sources of information can be added following the nomenclature source_active_N, source_organisation_N, etc. being N a number from 1 to 12
        'source_active_1': True, # Enable or disable the source
        'source_organisation_1': i18n.update_translations(translations, 'organisation.name', organisation_name),
        'source_url_1': organisation_url,
        'source_url_text_1': organisation_id,

        # Unit measure that will appear in the footer of the graph.
        'computation_units': calculate_computation_units(data, config),

        # Navigation
        'prev_indicator': node_meta_from_csv.get('previous_indicator'),
        'next_indicator': node_meta_from_csv.get('next_indicator')
    }

    # Convert the dictionary to a YAML string
    stream = StringIO()
    yaml.dump(indicator_meta, stream)
    yaml_content = stream.getvalue()
    
    # Wrap the YAML content with ---
    markdown_content = f"---\n{yaml_content}---\n"
    
    with open(output_filepath + '.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)

    i18n.update_translation_files(translations)

def calculate_computation_units(data, config):
    """
    Examines data['data']['attributes']['attribute'] to find the attribute with id config['unit_measure_id'], normally 'UNIDAD_MEDIDA'
    and checks the values of the attribute. If there is only one non-empty value, it returns it. Otherwise, it returns ''

    :param data: The dataset containing attributes.
    :return: The single non-empty value of 'UNIDAD_MEDIDA', or '' if not found or invalid.
    """
    # Find the attribute by it's id
    unit_measure_attribute = next(
        (attr for attr in data['data']['attributes']['attribute'] if attr['id'] == config['unit_measure_id']),
        None
    )

    if not unit_measure_attribute:
        print(f"Attribute '{config['unit_measure_id']}' not found.")
        return ''

    unit_measure_values = set(value.strip() for value in unit_measure_attribute['value'].split(" | ") if value.strip())

    if len(unit_measure_values) == 1:
        return unit_measure_values[0]
    else:
        print(f"No single value for attribute '{config['unit_measure_id']}'. Existing values: {unit_measure_values}")
        return ''

def calculate_data_show_map(data):
    """
    Examines the metadata and data dimensions to determine if a map should be shown.
    Filters geographic dimension values based on their presence in the data dimensions.

    :param data: The dataset containing metadata and data dimensions.
    :return: True if there are multiple geographic granularity values, False otherwise.
    """
    geographic_values_by_granularity = {}

    # Search GEOGRAPHIC_DIMENSION dimensions
    for metadata_dimension in data['metadata']['dimensions']['dimension']:
        if metadata_dimension['type'] == 'GEOGRAPHIC_DIMENSION':

            # Find data representations for the geographic dimension
            geographic_data_dimension = next((dim for dim in data['data']['dimensions']['dimension'] if dim['dimensionId'] == metadata_dimension['id']), None)
            if not geographic_data_dimension:
                return False
            
            valid_geographic_representations = [rep['code'] for rep in geographic_data_dimension['representations']['representation']]
    
            # Group dimensionValues by geographicGranularity
            for dimension_value in metadata_dimension['dimensionValues']['value']:
                if dimension_value['id'] in valid_geographic_representations:
                    granularity = dimension_value['geographicGranularity']['id']
                    if granularity not in geographic_values_by_granularity:
                        geographic_values_by_granularity[granularity] = []
                    geographic_values_by_granularity[granularity].append(dimension_value)
            break

    # If for any granularity we have more than one value, we should show the map
    for granularity, values in geographic_values_by_granularity.items():
        if len(values) > 1:
            return True

    return False

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