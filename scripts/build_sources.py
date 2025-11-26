from edatos.services import common_metadata, statistical_resources, structural_resources
from edatos.utils import json, csv as csv_utils, opensdg

def build_sources():

    config = common_metadata.initialize_properties(config='config_data.yml')

    collection_url = statistical_resources.urn_to_url(config['statistical_resources_rest'], config['root_collection'])
    collection = json.download(collection_url) 
    
    organisation_url = structural_resources.urn_to_url(config['structural_resources_rest'], config['organisation'])
    organisation = json.download(organisation_url)
    
    meta_from_csv = csv_utils.load_indexed_csv('indicator_key', 'meta/meta.csv')
    meta_from_csv = opensdg.setup_indicators_navigation(meta_from_csv)
    
    statistical_resources.process_nodes(collection, config, meta_from_csv, organisation)

if __name__ == "__main__":

    build_sources()