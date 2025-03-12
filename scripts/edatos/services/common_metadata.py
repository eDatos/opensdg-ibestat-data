import yaml
import requests

def initialize_properties(config):
    with open(config, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    common_metadata = config['edatos']['common_metadata']
    
    unit_measure_id_key = common_metadata['keys']['unit_measure_id']
    statistical_resources_rest_key = common_metadata['keys']['statistical_resources_rest']
    root_collection_key = common_metadata['keys']['root_collection']
    languages_key = common_metadata['keys']['languages']
    
    base_url =  common_metadata['rest']
        
    unit_measure_id_value = get_property(base_url, unit_measure_id_key)
    statistical_resources_rest_value = get_property(base_url, statistical_resources_rest_key)
    root_collection_value = get_property(base_url, root_collection_key)
    languages_value = get_property(base_url, languages_key)
    
    return {
        'unit_measure_id': unit_measure_id_value, # 'UNIDAD_MEDIDA'
        'statistical_resources_rest': statistical_resources_rest_value, # 'https://pre.ibestat.es/edatos/apis/statistical-resources'
        'root_collection': root_collection_value, # 'urn:siemac:org.siemac.metamac.infomodel.statisticalresources.Collection=IBESTAT:C00124A_000001',
        'languages': [lang.strip() for lang in languages_value.split(',')] # ['ca', 'es', 'en']
    }

def get_property(base_url, key):
    url = f"{base_url}/properties/{key}.json"
    response = requests.get(url)
    response.raise_for_status()
    if 'value' not in response.json():
        return None
    return response.json()['value']