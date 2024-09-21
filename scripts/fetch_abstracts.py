
##### Fetch abstracts #####

import os
import sys
import argparse
from langdetect import detect
from Bio import Entrez

Entrez.email = "YOUR_EMAIL"

# Fetch PubMed records
def get_set_articles(records):
    return records["PubmedArticle"]

def get_pmid(record):
    return record["MedlineCitation"]["PMID"]

def get_abstract_text(record):
    all_abstracttexts = []
    try:
        texts = []
        texts.append(record["MedlineCitation"]["Article"]['Abstract']['AbstractText'])
        if 'OtherAbstract' in record["MedlineCitation"]:
            for item in record["MedlineCitation"]['OtherAbstract']:
                texts.append(item['AbstractText'])
        abstracttext = ""
        for text in texts:
            if len(text) > 1:
                abstracttext = ""
                for part in text:
                    label = part.attributes.get('Label', 'None')
                    part = part.replace('"', "'")
                    abstracttext += part + " "
            else:
                abstracttext = text[0].replace('"', "'")
            all_abstracttexts.append(abstracttext.strip())
    except Exception as e:
        print(f"PMID {get_pmid(record)} - abstract not found! Error: {e}")
    return all_abstracttexts

def build_article(record):
    articles = []    
    langs = []
    all_abstracttexts = get_abstract_text(record)
    
    for index in range(len(all_abstracttexts)):
        article = {}
        article["pmid"] = get_pmid(record)
        article["abstracttext"] = all_abstracttexts[index]
        
        # Detect language of abstract text
        try:
            lang = detect(article["abstracttext"])
        except:
            lang = "unknown"
        
        article["lang"] = lang
        langs.append(lang)
        articles.append(article)
    
    return articles, langs

def fetch_pubmed_articles(ids):
    ids = ",".join(ids)
    try:
        handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        set_articles = []
        set_langs = []
        for record in get_set_articles(records):
            article, langs = build_article(record)
            set_articles.append(article)
            set_langs.append(langs)
        return set_articles, set_langs
    except Exception as e:
        print(f"Error fetching PubMed articles: {e}")
        return [], []

def fetch_multiple_articles(pmids, out_dir, lang1, lang2):
    print(f"Fetching articles for PMIDs: {pmids}")
    set_articles, set_langs = fetch_pubmed_articles(pmids)
    
    if not set_articles:
        print(f"No articles found for PMIDs: {pmids}")
        return
    
    for index in range(len(set_articles)):
        langs = set_langs[index]
        if len(langs) < 2 or lang1 not in langs or lang2 not in langs:
            continue
        
        article = set_articles[index]
        for item in article:
            if item["lang"] not in {lang1, lang2}:
                continue
            
            print(f"Saving article {item['pmid']} with language {item['lang']}")
            with open(os.path.join(out_dir, f"{item['pmid']}_{item['lang']}.txt"), "w") as writer:
                writer.write(item["abstracttext"] + "\n")

# Language mapping (en and pt)
map_langs = {
    "eng": "en",
    "por": "pt",
}

def get_lang1_lang2():
    return "en", "pt"  pyt

def retrieve_abstracts(input_file_path, out_dir):
    lang1, lang2 = get_lang1_lang2()
    
    pmids = []
    with open(input_file_path, "r") as reader:
        lines = reader.readlines()
        for line in lines:
            pmid = line.strip()
            pmids.append(pmid)
            
            if len(pmids) >= 100:  # Fetch in batches of 100 PMIDs
                fetch_multiple_articles(pmids, out_dir, lang1, lang2)
                pmids = []  # Reset list after batch processing
    
    if pmids:
        fetch_multiple_articles(pmids, out_dir, lang1, lang2)

def main(input_file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    retrieve_abstracts(input_file_path, output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch PubMed abstracts.")
    parser.add_argument('input_file', help="Path to the input file containing PMIDs")
    parser.add_argument('output_dir', help="Path to the output directory for saving abstracts")
    args = parser.parse_args()
    
    main(args.input_file, args.output_dir)

