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

# Example
# node_id = "2.4.1"
# filename = format_filename(node_id)
# print(filename)  # Output: indicator_2-4-1
def format_filename(node_id):
    formatted_id = node_id.replace('.', '-')
    return f"indicator_{formatted_id}"

