import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

import requests
import json
import sys
import csv

apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4YTBlNjdiY2Y1YWUxMDExYjExMjAxNzEzMjA5ZTIzYiIsInN1YiI6IjY1MmU4ZTg3ZWE4NGM3MDBjYTEyNjk0YSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.BY1J5ufdmTAhF4RS74zk6RCtIs-eDbnH3QOia9emzvk"
genres = json.load(open('genres.json'))

def consumeTMDB_API(title):
    url = "https://api.themoviedb.org/3/search/movie?query="
    url += title
    url += "&include_adult=true&language=pt-BR"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + apiKey
    }
    print("Iniciando a API: " + title)
    response = requests.get(url, headers=headers).json()
    print("Encerrada a API")

    print("Processo iniciado...", end='')
    with open('trainingset.csv', 'a+', newline='') as csvfile:
        csvWriter = csv.DictWriter(csvfile, fieldnames=['Title','OriginalTitle','Synopsis','Genre','ReleaseDate'], delimiter=';')

        for item in response['results']:
            filter = [x for x in genres['genres'] if x['id'] in item['genre_ids']]
            strGenres = ''
            for f in filter:
                strGenres = strGenres + f['name'] + ','
            strGenres = strGenres[:-1]

            for g in strGenres.split(","): 
                row = {
                    'Title': str(item['title']).replace(";","."),
                    'OriginalTitle': str(item['original_title']).replace(";","."),
                    'Synopsis': str(item['overview']).replace(";","."),
                    'Genre': str(g),
                    'ReleaseDate': str(item['release_date'])
                }

                csvWriter.writerow(row)

# Train a Naive Bayes classifier
naive_bayes = MultinomialNB()

tfidf_vectorizer = TfidfVectorizer(max_features=5000)

# Preprocess the data
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return text

def learn():
    # Load the CSV file
    data = pd.read_csv('trainingset.csv', delimiter=';')

    data['Title'] = data['Title'].apply(clean_text)
    data['Synopsis'] = data['Synopsis'].apply(clean_text)

    # Combine 'Title' and 'Synopsis' into one text column
    data['Text'] = data['Title'] + " " + data['Synopsis']

    # Fill missing values in 'Text' with empty strings
    data['Text'].fillna('', inplace=True)

    # Initialize the TF-IDF vectorizer    
    X = tfidf_vectorizer.fit_transform(data['Text'])

    # Fill missing values in 'Genre' with a default label, e.g., "Unknown"
    data['Genre'].fillna('Indefinido', inplace=True)
    
    naive_bayes.fit(X, data['Genre'])

    print(data, naive_bayes)

# Function to predict genre based on user input
def predict_genre(user_title, user_synopsis):
    # Combine user input with title and synopsis
    user_input = user_title + " " + user_synopsis
    
    # Clean and preprocess the user input
    user_input = clean_text(user_input)
    
    user_input_vector = tfidf_vectorizer.transform([user_input])
    predicted_genre = naive_bayes.predict(user_input_vector)
    print(naive_bayes.predict_proba(user_input_vector))
    return predicted_genre

user_title = ""

title_list = []
with open('movie_list.csv', 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        line_t = re.sub(r'[^a-zA-Z0-9\s]', '', line).upper()
        title_list.append(line_t)

print(title_list)

file.close()


learn()

with open('movie_list.csv', 'a+') as f:
    while user_title != "SAIR":        
        # User input
        user_title = input("Enter the movie title: ")        

        if user_title != "SAIR":
            user_synopsis = input("Enter the movie synopsis: ")
            
            if re.sub(r'[^a-zA-Z0-9\s]', '', user_title).upper() not in (title_list):
                f.write(user_title + '\n')
                consumeTMDB_API(user_title)
            
            learn()
            # Predict the genre
            predicted_genre = predict_genre(user_title, user_synopsis)
            print(f"Predicted Genre: {predicted_genre}")            

    f.close()