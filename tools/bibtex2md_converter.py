import os
import yaml
from datetime import datetime
import time 
import argparse

class BibtexEntry:
    def __init__(self, entry_type, citation_key, fields):
      self.entry_type = entry_type
      self.citation_key = citation_key
      self.fields = fields

    def __repr__(self):
      return f"BibtexEntry(entry_type={self.entry_type}, citation_key={self.citation_key}, fields={self.fields})"

def parse_bibtex_entry(entry):
    lines = entry.strip().split('\n')
    entry_type, citation_key = lines[0][1:].split('{', 1)
    citation_key = citation_key.rstrip(',')
    fields = {}
    for line in lines[1:]:
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().rstrip(',').strip('{}')
            fields[key] = value
    return BibtexEntry(entry_type.strip(), citation_key.strip(), fields)

def parse_bibtex_file(file_path):
    #with open(file_path, 'r', encoding='utf-8',) as file:
    with open(file_path, mode='r', encoding = 'utf-8') as file:
        
        content = file.read()
        entries = content.split('@')[1:]
    return [parse_bibtex_entry('@' + entry) for entry in entries]

    # Example usage

    
def read_bib_file(file_name):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, file_name)
    
    with open(file_path, mode='r', encoding = 'utf-8') as file:
        content = file.read()
    
    return content

def bibtex_to_yml(bibtex_entry, output_file):
    yml_data = []
    yml_data.append(["a", "b", "c"])
    # for entry in bibtex_entry:
    yml_entry = {
        'entry_type': bibtex_entry.entry_type,
        'citation_key': bibtex_entry.citation_key,
        'fields': bibtex_entry.fields
    }
    yml_data.append(yml_entry)
    
    with open(output_file, 'w') as file:
        yaml.dump(yml_data, file, default_flow_style=False)
                

def clean_up_bibtex_entry(bibtex_entry):

    for key, value in bibtex_entry.fields.items():
        bibtex_entry.fields[key] = value.replace('{', '').replace('}', '') 
        print (key, value)
    return bibtex_entry

def bibtex_to_yml1(bibtex_entry, output_file):
    bibtex_entry = clean_up_bibtex_entry(bibtex_entry)
    
    month_str = bibtex_entry.fields.get('month', '1').capitalize()
    month_mapping = {
        "January": "01", "Jan": "01",
        "February": "02", "Feb": "02",
        "March": "03", "Mar": "03",
        "April": "04", "Apr": "04",
        "May": "05",
        "June": "06", "Jun": "06",
        "July": "07", "Jul": "07",
        "August": "08", "Aug": "08",
        "September": "09", "Sep": "09",
        "October": "10", "Oct": "10",
        "November": "11", "Nov": "11",
        "December": "12", "Dec": "12"
        }
    month = month_mapping.get(month_str, month_str)  # Use mapping if month is a string, else keep as is
    date_str = f"{bibtex_entry.fields.get('year', '')}-{month}-{bibtex_entry.fields.get('day', '1')}"
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        date_obj = None  # Handle invalid date formats gracefully
    
    pubtitle = ""
    match bibtex_entry.entry_type:
        case "inproceedings":
            pubtitle = bibtex_entry.fields.get('booktitle', "unknown")
            publisher_obj = bibtex_entry.fields.get('publisher', "")
            publisher_mapping = {
                "Association for Computing Machinery": "ACM",
                "Institute of Electrical and Electronics Engineers": "IEEE",
                "Springer Nature": "Springer",
            }
            publisher_obj = publisher_mapping.get(publisher_obj,publisher_obj)
        case "article":
            pubtitle = bibtex_entry.fields.get('year', "unknown") + " Vol. " + bibtex_entry.fields.get('volume', "") + " " + bibtex_entry.fields.get('journal', "")
            publisher_obj = bibtex_entry.fields.get('journal', "")
        case "phdthesis":
            pubtitle = bibtex_entry.fields.get('shorttitle', "unknown")
            publisher_obj = bibtex_entry.fields.get('school', "")
        case "patent":
            pubtitle = bibtex_entry.fields.get('year', "unknown") + " Patent" + " " + bibtex_entry.fields.get('number', "")
            publisher_obj = bibtex_entry.fields.get('institution', "")
        case _:
            publisher_obj = "unknown"

     
    print(bibtex_entry.fields.get('doi', ''))
    yml_entry = {
        'pubtype' : bibtex_entry.entry_type,
        'title': bibtex_entry.fields.get('title', '<todo>'),
        'author': bibtex_entry.fields.get('author', '').replace("Detzner, Peter", "**<ins>Detzner, Peter</ins>**"),
        'pubtitle': pubtitle,
        'doi': bibtex_entry.fields.get('doi', ''),
        'date': date_obj.strftime("%Y-%m-%d") if date_obj else '',
        'publisher': publisher_obj,
        #'externalLink' : '\"{0}\"'.format(bibtex_entry.fields.get('url', '')),
        'externalLink' : bibtex_entry.fields.get('url', ''),
        'proceedings_title': bibtex_entry.fields.get('location', 'unknown'),
       # 'eventtitle': bibtex_entry.fields.get('eventtitle', 'eventtitle'),
       # 'location': bibtex_entry.fields.get('location', ''),
    }
    
    with open(output_file, 'w') as file:
        yaml.dump(yml_entry, file, default_flow_style=False, explicit_start=True)
        file.write('---\n')
        file.write('#### ' + yml_entry['title'] + '\n')
        abstract = bibtex_entry.fields.get('abstract', 'No abstract')
        formatted_abstract = abstract.replace('. ', '.\n')
        file.write(formatted_abstract + '\n')
        file.write('---\n')
        file.write(f"# BibTeX Entry\n")
        file.write(f"@{bibtex_entry.entry_type}{{{bibtex_entry.citation_key},\n")
        for key, value in bibtex_entry.fields.items():
            file.write(f"  {key} = {{{value}}},\n")
        file.write("}\n")
        file.write('#### ' + yml_entry['title'] + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert BibTeX entries to YAML/Markdown format.")
    parser.add_argument("-i", type=str, help="Path to the BibTeX file to be converted.")
    args = parser.parse_args()
    x = 0
    bibtex_entries = parse_bibtex_file(args.i)
    for entry in bibtex_entries:
        #print(entry)
        #print(entry.fields.get("abstract", "No abstract"))
        #print("") 
        output_file = "../tmp42/content/pubs/" + entry.citation_key + '.md'
        bibtex_to_yml1(entry, output_file)
        x+=1
        #break
        #print(f"Bibtex entries have been converted to YML and saved to {output_file}")
        