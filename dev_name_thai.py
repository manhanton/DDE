import csv
import requests
from io import StringIO
import string
from math import sqrt

# Tokenize and preprocess the sentences
def preprocess(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    tokens = sentence.split()
    return tokens

# Create a bag-of-words vector for each sentence
def create_vector(tokens, unique_words):
    vector = []
    for word in unique_words:
        if word in tokens:
            vector.append(tokens.count(word))
        else:
            vector.append(0)
    return vector

# Calculate the cosine similarity between two vectors
def cosine_similarity(v1, v2):
    dot_product = sum([v1[i] * v2[i] for i in range(len(v1))])
    magnitude_v1 = sqrt(sum([x**2 for x in v1]))
    magnitude_v2 = sqrt(sum([x**2 for x in v2]))
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    else:
        return dot_product / (magnitude_v1 * magnitude_v2)

# Read the developer names from a CSV file
def read_developer_names(file_url):
    response = requests.get(file_url)
    csv_buffer = StringIO(response.content.decode('utf-8'))
    csv_reader = csv.reader(csv_buffer, delimiter=',')
    # Skip the header row
    next(csv_reader)
    # Extract the developer names from the CSV file
    developer_names = [row[0] for row in csv_reader]
    return developer_names

# Calculate the similarity between each pair of developer names
def calculate_similarity(developer_names):
    # Tokenize and preprocess the developer names
    tokenized_names = [preprocess(name) for name in developer_names]
    # Create a set of all unique words in all names
    unique_words = set()
    for tokens in tokenized_names:
        unique_words.update(tokens)
    # Create a bag-of-words vector for each name
    vectors = [create_vector(tokens, unique_words) for tokens in tokenized_names]
    # Calculate the cosine similarity between each pair of names
    similarities = []
    for i in range(len(developer_names)):
        for j in range(i+1, len(developer_names)):
            similarity = cosine_similarity(vectors[i], vectors[j])
            similarities.append((i, j, similarity))
    return similarities

# Main function
def main():
    file_url = "https://raw.githubusercontent.com/manhanton/DDE/main/dev_name.csv"
    developer_names = read_developer_names(file_url)
    similarities = calculate_similarity(developer_names)
    # Print the similarity scores
    for i, j, similarity in similarities:
        print(f"Similarity between developer {i+1} and developer {j+1}: {similarity:.2f}")

if __name__ == "__main__":
    main()
