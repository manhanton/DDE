import csv
import string
from math import sqrt

# Read the sentences from a CSV file
with open('dev_name.csv', 'r',encoding='cp1252') as file:
    reader = csv.reader(file)
    sentences = [row[0] for row in reader]

# Tokenize and preprocess the sentences
def preprocess(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    tokens = sentence.split()
    return tokens

tokenized_sentences = [preprocess(sentence) for sentence in sentences]

# Create a set of all unique words in all sentences
unique_words = set()
for tokens in tokenized_sentences:
    unique_words.update(tokens)

# Create a bag-of-words vector for each sentence
def create_vector(tokens):
    vector = []
    for word in unique_words:
        if word in tokens:
            vector.append(tokens.count(word))
        else:
            vector.append(0)
    return vector

vectors = [create_vector(tokens) for tokens in tokenized_sentences]

# Calculate the cosine similarity between each pair of sentences
def cosine_similarity(v1, v2):
    dot_product = sum([v1[i] * v2[i] for i in range(len(v1))])
    magnitude_v1 = sqrt(sum([x**2 for x in v1]))
    magnitude_v2 = sqrt(sum([x**2 for x in v2]))
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    else:
        return dot_product / (magnitude_v1 * magnitude_v2)


# Calculate the cosine similarity between each pair of sentences
similarities = []
for i in range(len(sentences)):
    for j in range(i+1, len(sentences)):
        similarity = cosine_similarity(vectors[i], vectors[j])
        similarities.append((i, j, similarity))

# Print the similarity scores
for i, j, similarity in similarities:
    print(f"Similarity between sentence {i+1} and sentence {j+1}: {similarity:.2f}")
