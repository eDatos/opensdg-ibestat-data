import edatos.utils.i18n as i18n

def process_nodes(collection, languages):
    if 'data' in collection and 'nodes' in collection['data'] and 'node' in collection['data']['nodes']:
        for node in collection['data']['nodes']['node']:
            process_node(node, languages)

def process_node(node, languages, level=1):
    if level == 1:
        node_type = 'objective'
    elif level == 2:
        node_type = 'meta'
    elif level == 3:
        node_type = 'indicator'
    else:
        print(f"Unsupported level {level}")
        return

    default_language = languages[0]
    node_id = i18n.international_string_to_string(node['name'], default_language)
    print(f"Processing {node_type}: {node_id}")

    if 'dataset' in node:
        dataset_url = node['dataset']['selfLink']['href'] + ".json"
        print(f"Downloading dataset from: {dataset_url}")
        # download_and_transform_json_to_csv(dataset_url, 'data/' + format_filename(node_id))

    if 'nodes' in node and 'node' in node['nodes']:
        for child_node in node['nodes']['node']:
            process_node(child_node, languages, level + 1)

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