# Medline Articles Processing

## Project Overview
This project fetches abstracts from PubMed using provided PMIDs and translates the abstracts from English to Portuguese.

## Directory Structure:
- `data/`: Contains input data files.
- `output/abstracts/`: Contains the fetched PubMed abstracts.
- `output/translations/`: Contains the translated abstracts.
- `scripts/`: Contains Python scripts for fetching abstracts and translating texts.
- `requirements.txt`: List of required Python packages.
- `processed_files.txt`: Track which files have already been processed (used in `translate_texts.py` to avoid reprocessing).

## How to Set Up the Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/AnaluRRamos/medline_biomedical_translation.git
   cd medline_biomedical_translation

