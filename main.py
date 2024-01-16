import json
import spacy
import os
import string
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO)


def read_data_from_file(file_path):
    """
    Reads data from a JSON file and returns the parsed content.

    Parameters:
    - file_path (str): The path to the JSON file.

    Returns:
    - dict or list: The parsed data from the JSON file.

    Opens the specified JSON file in read mode with UTF-8 encoding.
    Parses the JSON content using the `json.load` function.
    Closes the file automatically using the 'with' statement.
    Returns the parsed data, which can be a dictionary or a list.
    """

    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def create_corpus(data):
    """
    Creates a text corpus from a list of items containing opinions.

    Parameters:
    - data (list): A list of items, each containing an "opinions" key with a list of opinions.

    Returns:
    - list: A list of preprocessed and lowercased opinions without punctuation.

    Iterates through each item in the provided data list.
    For each opinion in the "opinions" key of the item, removes punctuation using
    string.punctuation and converts the opinion to lowercase.
    Appends the preprocessed opinion to the corpus list.
    Returns the resulting text corpus.
    """

    corpus = []
    for item in data:
        for opinion in item["opinions"]:
            opinion_without_punctuation = "".join(
                char for char in opinion if char not in string.punctuation
            )
            lowercase_opinion = opinion_without_punctuation.lower()
            corpus.append(lowercase_opinion)
    return corpus


def tokenize(corpus, nlp):
    """
    Tokenizes the given text corpus using a natural language processing (NLP) pipeline.

    Parameters:
    - corpus (list): A list of text strings to be tokenized.
    - nlp (spacy.Language): The Spacy NLP pipeline used for tokenization.

    Returns:
    - list: A flat list of tokens extracted from the input corpus.

    Tokenizes each text string in the provided corpus using the specified NLP pipeline.
    Extends the 'tokens' list with the individual token texts from each processed document.
    Returns the resulting flat list of tokens.
    """

    tokens = []
    for text in corpus:
        doc = nlp(text)
        tokens.extend([token.text for token in doc])
    return tokens


def remove_stop_words(tokens, nlp):
    """
    Removes stop words from a list of tokens using a natural language processing (NLP) pipeline.

    Parameters:
    - tokens (list): A list of tokens from which stop words will be removed.
    - nlp (spacy.Language): The Spacy NLP pipeline used for stop word identification.

    Returns:
    - list: A list of tokens with stop words filtered out.

    Removes stop words from the input list of tokens based on the stop words provided by the
    specified NLP pipeline. The resulting list contains only tokens that are not stop words.
    """

    stop_words = nlp.Defaults.stop_words
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
    return filtered_tokens


def lemmatize(tokens, nlp):
    """
    Lemmatizes a list of tokens using a natural language processing (NLP) pipeline.

    Parameters:
    - tokens (list): A list of tokens to be lemmatized.
    - nlp (spacy.Language): The Spacy NLP pipeline used for lemmatization.

    Returns:
    - list: A list of lemmas corresponding to the input tokens.

    Lemmatizes each token in the input list using the specified NLP pipeline.
    The resulting list contains lemmas corresponding to each token in the input list.
    """

    doc = nlp(" ".join(tokens))
    lemmas = [token.lemma_ for token in doc]
    return lemmas


def stem_text(tokens):
    """
    Stems a list of tokens using the Porter stemming algorithm.

    Parameters:
    - tokens (list): A list of tokens to be stemmed.

    Returns:
    - list: A list of stemmed tokens using the Porter stemming algorithm.

    Stems each token in the input list using the Porter stemming algorithm.
    The resulting list contains stemmed versions of each token in the input list.
    """

    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens


def analyze_and_visualize(corpus, top_percentage=5):
    """
    Analyzes and visualizes the given text corpus.

    Parameters:
    - corpus (list): A list of text strings for analysis and visualization.
    - top_percentage (int, optional): The percentage of top words to include in the visualization. Defaults to 5.

    Performs the following analyses and visualizations:
    1. Prints the total number of words and unique words in the corpus.
    2. Generates and displays a word cloud based on the entire corpus.
    3. Creates a bar chart displaying the top words and their frequencies.

    Saves the generated visualizations as PNG files in the 'results' directory.

    Note: Requires the 'wordcloud' library and 'matplotlib' for visualization.

    Returns:
    - None
    """
    flattened_tokens = [token for token in corpus]

    word_count = len(flattened_tokens)
    unique_words = len(set(flattened_tokens))
    print(f"Total Words: {word_count}")
    print(f"Unique Words: {unique_words}")

    wordcloud = WordCloud(width=800, height=400).generate(" ".join(flattened_tokens))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("results/7_visualize_1.png", bbox_inches="tight")
    plt.show()

    count_vectorizer = CountVectorizer()

    count_matrix = count_vectorizer.fit_transform(corpus)

    vocabulary = count_vectorizer.get_feature_names_out()
    word_frequencies = count_matrix.sum(axis=0).A1

    top_word_indices = (-word_frequencies).argsort()[
        : int(top_percentage / 100 * len(vocabulary))
    ]

    top_words = [vocabulary[i] for i in top_word_indices]
    top_frequencies = word_frequencies[top_word_indices]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(top_words)), top_frequencies, tick_label=top_words)
    plt.xlabel("Słowa")
    plt.ylabel("Częstość występowania")
    plt.title(f"Top {top_percentage}% najczęściej występujących słów w tekście")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig("results/7_visualize_2.png", bbox_inches="tight")
    plt.show()


def vectorize_text(corpus):
    """
    Vectorizes a text corpus using the CountVectorizer.

    Parameters:
    - corpus (list): A list of text strings to be vectorized.

    Returns:
    - scipy.sparse.csr.csr_matrix: A sparse matrix representing the vectorized text.

    Uses the CountVectorizer to convert the input list of text strings into a
    sparse matrix representation, where each row corresponds to a document in
    the corpus and each column corresponds to a unique word in the vocabulary.
    """

    vectorizer = CountVectorizer()
    vectorized_text = vectorizer.fit_transform(corpus)
    return vectorized_text


if not os.path.exists("results"):
    os.makedirs("results")


def write_tokens_to_file(file_path, tokens):
    """
    Writes a list of tokens to a text file.

    Parameters:
    - file_path (str): The path to the output text file.
    - tokens (list): A list of tokens to be written to the file.

    Returns:
    - None

    Writes each token in the input list to the specified text file, separating tokens
    with newline characters. Logs information about the file writing process using
    the logging module, indicating the file path when the operation is successful.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(["".join(token) for token in tokens]))
    logging.info(f"File written: {file_path}")


def process_data():
    """
    Process data from an input JSON file, perform text preprocessing, and visualize the results.

    Reads data from the specified JSON file containing opinions.
    Utilizes Spacy for natural language processing, including tokenization, lemmatization, and stop word removal.
    Creates and saves intermediate results, including a text corpus, tokenized text, lemmatized text, stemmed text,
    filtered text, and visualizations of word cloud and top word frequencies.
    Finally, vectorizes the text corpus using CountVectorizer and saves the result to a file.

    Parameters:
    - None

    Returns:
    - None
    """
    file_path = "results/1_opinions.json"
    data = read_data_from_file(file_path)

    nlp = spacy.load("pl_core_news_sm")
    nlp.max_length = 2500000

    corpus = create_corpus(data)
    write_tokens_to_file("results/2_corpus.txt", corpus)

    tokens = tokenize(corpus, nlp)
    write_tokens_to_file(
        "results/3_tokenized.txt", ["".join(token) for token in tokens]
    )

    lemmatized_tokens = lemmatize(tokens, nlp)
    write_tokens_to_file(
        "results/4_lemmatized.txt", ["".join(token) for token in lemmatized_tokens]
    )

    stemmed_tokens = stem_text(tokens)
    write_tokens_to_file(
        "results/5_stemmed.txt", ["".join(token) for token in stemmed_tokens]
    )

    filtered_tokens = remove_stop_words(lemmatized_tokens, nlp)
    write_tokens_to_file(
        "results/6_filtered.txt", ["".join(token) for token in filtered_tokens]
    )

    analyze_and_visualize(filtered_tokens, top_percentage=0.3)

    vectorized_text = vectorize_text(corpus)
    with open("results/8_vectorized.txt", "w") as file:
        file.write(str(vectorized_text))


if __name__ == "__main__":
    process_data()
