##### Translate text   #####
import os
import logging
import argparse
from transformers import MarianTokenizer, MarianMTModel
from nltk.tokenize import sent_tokenize
import nltk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

nltk.download('punkt')

def load_processed_files(translated_out_dir):
    """Loading the list of processed files"""
    checkpoint_file = os.path.join(translated_out_dir, "processed_files.txt")
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            return f.read().splitlines()
    return []

def save_processed_file(checkpoint_file, filename):
    """Append a filename to the processed files checkpoint"""
    with open(checkpoint_file, "a") as f:
        f.write(filename + "\n")

def setup_directories(input_dir, translated_out_dir):
    """Set up input and output directories"""
    os.makedirs(translated_out_dir, exist_ok=True)
    return input_dir, translated_out_dir

def load_model():
    """Translation model and tokenizer"""
    model_name = "Helsinki-NLP/opus-mt-tc-big-en-pt"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def translate_text(text, tokenizer, model):
    """Translate text from Eng to Por"""
    sentences = sent_tokenize(text)
    translated_sentences = []
    for sentence in sentences:
        tokens = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True).input_ids
        translated = model.generate(input_ids=tokens)
        translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        translated_sentences.append(translated_text)
    return " ".join(translated_sentences)

def process_files(input_dir, translated_out_dir, tokenizer, model):
    files = [f for f in os.listdir(input_dir) if f.endswith("_en.txt")]
    processed_files = load_processed_files(translated_out_dir)

    checkpoint_file = os.path.join(translated_out_dir, "processed_files.txt")

    for i, filename in enumerate(files):
        if filename in processed_files:
            continue

        logging.info(f"Translating {filename} ({i+1}/{len(files)})")
        pmid = filename.split("_")[0]

        try:
            with open(os.path.join(input_dir, filename), "r") as infile:
                abstract = infile.read()
            translated_abstract = translate_text(abstract, tokenizer, model)

            translated_filename = f"{pmid}_pt_translated.txt"
            with open(os.path.join(translated_out_dir, translated_filename), "w") as outfile:
                outfile.write(translated_abstract)

            save_processed_file(checkpoint_file, filename)
            logging.info(f"Finished translating {filename}")

        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Translate text files from English to Portuguese.")
    parser.add_argument("input_dir", type=str, help="Path to the directory containing input text files.")
    parser.add_argument("translated_out_dir", type=str, help="Path to the directory for saving translated files.")
    args = parser.parse_args()

    input_dir, translated_out_dir = setup_directories(args.input_dir, args.translated_out_dir)
    tokenizer, model = load_model()
    process_files(input_dir, translated_out_dir, tokenizer, model)

if __name__ == "__main__":
    main()

