import nltk
import random
import argparse # Import argparse

# Download necessary NLTK data (if not already downloaded)
# WordNet is needed for finding synonyms.
# Punkt is needed for tokenizing text into words.
try:
    nltk.data.find('corpora/wordnet')
except nltk.downloader.DownloadError:
    nltk.download('wordnet')
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize

def paraphrase(text):
    """
    Paraphrases the input text by replacing some words with their synonyms.
    """
    words = word_tokenize(text)
    paraphrased_words = []
    for word in words:
        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        
        if synonyms:
            # Replace with a synonym, but keep the original word sometimes
            # Also, avoid replacing with multi-word synonyms for simplicity
            # and ensure the synonym is different from the original word.
            possible_replacements = [s for s in synonyms if '_' not in s and s.lower() != word.lower()]
            if possible_replacements and random.random() < 0.5: # 50% chance to replace
                paraphrased_words.append(random.choice(possible_replacements))
            else:
                paraphrased_words.append(word)
        else:
            paraphrased_words.append(word)
            
    return " ".join(paraphrased_words)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Paraphrase a given text.")
    parser.add_argument('text', nargs='?', default=None, help="The text to paraphrase. If not provided, the script will prompt for input.")
    
    args = parser.parse_args()
    
    input_text = ""
    if args.text:
        input_text = args.text
    else:
        input_text = input("Please enter the text you want to paraphrase: ")
        
    if input_text:
        paraphrased_text = paraphrase(input_text)
        print(f"Original: {input_text}")
        print(f"Paraphrased: {paraphrased_text}")
    else:
        print("No input text provided.")
