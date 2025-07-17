from ruamel.yaml import YAML

# Initialize ruamel.yaml
yaml = YAML()
yaml.default_flow_style = False
yaml.allow_unicode = True
yaml.width = 1000
yaml.sort_keys = False
yaml.preserve_quotes = True
