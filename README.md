# Text Paraphraser

A Python script that paraphrases input text by replacing words with their synonyms using the NLTK library.

## Features

-   Paraphrases input text using NLTK and WordNet for synonym replacement.
-   Randomly decides whether to replace a word with a synonym to provide variation.
-   Simple command-line interface (CLI) for ease of use.
-   Handles NLTK resource (WordNet, Punkt) downloads automatically on first run if they are not found.

## Setup

1.  **Install NLTK:**
    If you don't have NLTK installed, you can install it using pip:
    ```bash
    pip install nltk
    ```

2.  **NLTK Resource Downloads (WordNet & Punkt):**
    The script is designed to automatically download the necessary NLTK resources (WordNet for synonyms and Punkt for tokenization) if they are not found on your system. When you run the script for the first time, it will check for these resources and download them if required. You might see download progress messages from NLTK in your console during this one-time setup.

## Usage

You can run the `textparaphraser.py` script from your command line.

1.  **With a text argument:**
    Provide the text you want to paraphrase directly as a command-line argument. Make sure to enclose the text in quotes if it contains spaces.
    ```bash
    python textparaphraser.py "This is the sentence I want to paraphrase."
    ```
    The script will output both the original and the paraphrased text.

2.  **Without a text argument (interactive mode):**
    If you run the script without providing any text as an argument, it will prompt you to enter the text:
    ```bash
    python textparaphraser.py
    ```
    It will then display:
    ```
    Please enter the text you want to paraphrase: 
    ```
    Type or paste your text and press Enter. The script will then output the original and paraphrased text.

## Testing

The script comes with a suite of unit tests to ensure its core functionality works as expected.

1.  **Navigate to the directory:**
    Make sure you are in the same directory as `textparaphraser.py` and `test_textparaphraser.py`.

2.  **Run the tests:**
    Execute the following command in your terminal:
    ```bash
    python -m unittest test_textparaphraser.py
    ```
    This will discover and run all tests defined in `test_textparaphraser.py`. You should see output indicating the number of tests run and whether they passed or failed.

    Alternatively, if your test file is directly executable (which it is, due to `if __name__ == '__main__': unittest.main()`), you might also be able to run it as:
    ```bash
    python test_textparaphraser.py
    ```
    Both commands should achieve the same result of running the test suite.
