

import numpy as np
import torch
import torchaudio

from .dl_model import raga_resnet



def predict(ex_file, state_dict_path = './model_weights/trained_modelamplitude_added_and_lower_mels_resnet18.tar'):
    label_to_name = {0: 'AbhEri', 1: 'shuddhadhanyAsi'}

    model = raga_resnet('cpu', num_ragas = 2)
    device = torch.device('cpu')
    model.load_state_dict(torch.load(state_dict_path, map_location=device))
    model.eval()

    waveform, sample_rate = torchaudio.load(ex_file)
    if len(waveform.shape) > 1:
        waveform = waveform.mean(axis = 0).reshape((1,-1))
    len_index_30_sec = int(30 / (1 / sample_rate))
    # trim first and last 30 seconds if long enough
    if waveform.shape[1] > 2 * len_index_30_sec:
        waveform = waveform[:, len_index_30_sec:-len_index_30_sec]
        # get random start index
        start_index = np.random.randint(low = 0, high = waveform.shape[1] - len_index_30_sec)
        waveform = waveform[:, start_index:start_index + 2*(len_index_30_sec)]
    else:
        waveform = waveform[:,0: 2 * len_index_30_sec]
        print('too short', waveform.shape, sample_rate)
    effects = [
            [ "rate", "44100"]
            ]
    waveform, sample_rate = torchaudio.sox_effects.apply_effects_tensor(
        waveform, sample_rate, effects)
    len_index_30_sec = int(30 / (1 / sample_rate))
    waveform = waveform[:, 0:len_index_30_sec]


    with torch.no_grad():
        vals = model(waveform.unsqueeze(0)).squeeze()
        # print(vals)
        return label_to_name[int(torch.argmax(vals))]




# import requests
#
#
# class Movie(object):
#     def __init__(self, omdb_json, detailed=False):
#         if detailed:
#             self.genres = omdb_json["Genre"]
#             self.director = omdb_json["Director"]
#             self.actors = omdb_json["Actors"]
#             self.plot = omdb_json["Plot"]
#             self.awards = omdb_json["Awards"]
#
#         self.title = omdb_json["Title"]
#         self.year = omdb_json["Year"]
#         self.imdb_id = omdb_json["imdbID"]
#         self.type = "Movie"
#         self.poster_url = omdb_json["Poster"]
#
#     def __repr__(self):
#         return self.title
#
#
# class MovieClient(object):
#     def __init__(self, api_key):
#         self.sess = requests.Session()
#         self.base_url = f"http://www.omdbapi.com/?apikey={api_key}&r=json&type=movie&"
#
#     def search(self, search_string):
#         """
#         Searches the API for the supplied search_string, and returns
#         a list of Media objects if the search was successful, or the error response
#         if the search failed.
#
#         Only use this method if the user is using the search bar on the website.
#         """
#         search_string = "+".join(search_string.split())
#         page = 1
#
#         search_url = f"s={search_string}&page={page}"
#
#         resp = self.sess.get(self.base_url + search_url)
#
#         if resp.status_code != 200:
#             raise ValueError(
#                 "Search request failed; make sure your API key is correct and authorized"
#             )
#
#         data = resp.json()
#
#         if data["Response"] == "False":
#             raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')
#
#         search_results_json = data["Search"]
#         remaining_results = int(data["totalResults"])
#
#         result = []
#
#         ## We may have more results than are first displayed
#         while remaining_results != 0:
#             for item_json in search_results_json:
#                 result.append(Movie(item_json))
#                 remaining_results -= len(search_results_json)
#             page += 1
#             search_url = f"s={search_string}&page={page}"
#             resp = self.sess.get(self.base_url + search_url)
#             if resp.status_code != 200 or resp.json()["Response"] == "False":
#                 break
#             search_results_json = resp.json()["Search"]
#
#         return result
#
#     def retrieve_movie_by_id(self, imdb_id):
#         """
#         Use to obtain a Movie object representing the movie identified by
#         the supplied imdb_id
#         """
#         movie_url = self.base_url + f"i={imdb_id}&plot=full"
#
#         resp = self.sess.get(movie_url)
#
#         if resp.status_code != 200:
#             raise ValueError(
#                 "Search request failed; make sure your API key is correct and authorized"
#             )
#
#         data = resp.json()
#
#         if data["Response"] == "False":
#             raise ValueError(f'Error retrieving results: \'{data["Error"]}\' ')
#
#         movie = Movie(data, detailed=True)
#
#         return movie
#
#
# ## -- Example usage -- ###
# if __name__ == "__main__":
#     import os
#
#     client = MovieClient(os.environ.get("OMDB_API_KEY"))
#
#     movies = client.search("guardians")
#
#     for movie in movies:
#         print(movie)
#
#     print(len(movies))
