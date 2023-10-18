import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load the CSV file
data = pd.read_csv('trainingset.csv', delimiter=';')

# Preprocess the data
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return text

data['Title'] = data['Title'].apply(clean_text)
data['Synopsis'] = data['Synopsis'].apply(clean_text)

# Combine 'Title' and 'Synopsis' into one text column
data['Text'] = data['Title'] + " " + data['Synopsis']

# Fill missing values in 'Text' with empty strings
data['Text'].fillna('', inplace=True)

# Initialize the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(max_features=5000)
X = tfidf_vectorizer.fit_transform(data['Text'])

# Fill missing values in 'Genre' with a default label, e.g., "Unknown"
data['Genre'].fillna('Indefinido', inplace=True)

# Train a Naive Bayes classifier
naive_bayes = MultinomialNB()
naive_bayes.fit(X, data['Genre'])

# Function to predict genre based on user input
def predict_genre(user_title, user_synopsis):
    # Combine user input with title and synopsis
    user_input = user_title + " " + user_synopsis
    
    # Clean and preprocess the user input
    user_input = clean_text(user_input)
    
    user_input_vector = tfidf_vectorizer.transform([user_input])
    predicted_genre = naive_bayes.predict(user_input_vector)[0]
    return predicted_genre

user_title = ""
with open('movie_list.csv', 'a+') as f:
    while user_title != "SAIR":        
        # User input
        user_title = input("Enter the movie title: ")
        user_synopsis = input("Enter the movie synopsis: ")

        if user_title != "SAIR":
            f.write(user_title + '\n')
            # Predict the genre
            predicted_genre = predict_genre(user_title, user_synopsis)
            print(f"Predicted Genre: {predicted_genre}")

    f.close()
with open('main.py') as sp:
    exec(sp.read())