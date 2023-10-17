import csv
import sys
import requests
import json

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
    return response['results']



if __name__=='__main__':    
    fileName = sys.argv[1] if len(sys.argv) == 2 else "movie_list.csv"

    print("Processo iniciado...", end='')
    with open(fileName) as file:
        lines = file.readlines()

        with open('trainingset.csv', 'a+', newline='') as csvfile:
            csvWriter = csv.DictWriter(csvfile, fieldnames=['Title','Original Title','Synopsis','Genre','Release Date'], delimiter=';')
            csvWriter.writeheader()

            for movie in lines:
                data = consumeTMDB_API(movie)
                for item in data:
                    filter = [x for x in genres['genres'] if x['id'] in item['genre_ids']]
                    strGenres = ''
                    for f in filter:
                        strGenres = strGenres + f['name'] + ','
                    strGenres = strGenres[:-1]

                    row = {
                        'Title': item['title'],
                        'Original Title': item['original_title'],
                        'Synopsis': item['overview'],
                        'Genre': strGenres,
                        'Release Date': item['release_date']
                    }
                    csvWriter.writerow(row)
    print(" OK!")