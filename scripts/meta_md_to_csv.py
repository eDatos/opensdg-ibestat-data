import os
import yaml
import csv
import sys
from edatos.services.statistical_resources import generate_indicator_sort_order

# This script was generated with ChatGPT to be executed once to generate a CSV file 
# from the properties stored in .md files. It remains here as documentation and 
# could be useful for regenerating or iterating over this process.

def extract_yaml_from_md(md_file):
    """Extracts the YAML content from a Markdown file."""
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if lines[0].strip() == '---':
        yaml_lines = []
        for line in lines[1:]:
            if line.strip() == '---':
                break
            yaml_lines.append(line)
        return yaml.safe_load(''.join(yaml_lines))
    return None

def process_md_files(directory):
    """Processes all .md files in the specified directory and extracts the YAML metadata."""
    data = []
    all_keys = set()
    
    for filename in os.listdir(directory):
        if filename.endswith('.md') and 'SERIE' not in filename:
            file_path = os.path.join(directory, filename)
            yaml_data = extract_yaml_from_md(file_path)
            if yaml_data:
                yaml_data['indicator_key'] = filename[:-3]  # Remove .md extension
                data.append(yaml_data)
                all_keys.update(yaml_data.keys())
    
    return data, all_keys

def write_csv(data, keys, output_file):
    """Writes the extracted data to a CSV file."""
    valid_keys = [ 'indicator_key', 'published', 'reporting_status', 'goal_meta_link', 'un_custodian_agency', 'un_designated_tier' ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=(valid_keys))
        writer.writeheader()
        for row in data:
            writer.writerow({key: row.get(key, '') for key in writer.fieldnames})

def main():
    if len(sys.argv) != 2:
        print("Usage: python meta_md_to_csv.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print("Error: The specified directory does not exist.")
        sys.exit(1)
    
    data, all_keys = process_md_files(directory)
    data.sort(key=lambda d: generate_indicator_sort_order(d['indicator_key']))
    write_csv(data, all_keys, directory + '/meta2.csv')
    print("File meta2.csv generated successfully.")

if __name__ == "__main__":
    main()
