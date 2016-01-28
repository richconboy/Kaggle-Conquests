# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 13:08:57 2015

@author: Rich
"""

from __future__ import print_function
import pandas as pd
import numpy as np

import requests
#Define a function that returns a JSON object from the Giant Bomb API
def pull_info(resource_type, resource_id='', offset=0):
    bomb = 'http://www.giantbomb.com/api/'
    resource_type = resource_type + '/'
    if resource_id != "":
        resource_id = resource_id + '/'
    api_key = '?api_key=98fade4b69e9695cee10f3d8a8f9cb69a5d03c55'
    json = '&format=json'
    offset = '&offset=' + str(offset)
    
    bomb += resource_type
    bomb += resource_id
    bomb += api_key
    bomb += json
    bomb += offset
    
    bomb_output = requests.get(bomb)
    bomb_json = bomb_output.json()
    
    return bomb_json

#Define a function that uses our JSON object to create our data
def create_full_db(resource_type, resource_id='', offset=0):
    game_dict = {'names': [], 'decks': [], 'platforms' : [], 'releases' : []}
    bomb_length = pull_info(resource_type, resource_id, 0)
    pages = (bomb_length['number_of_total_results']/100) + 1
    #pages = 5
    for page in range(pages):
        bomb_data = pull_info(resource_type, resource_id, page*100)        
        for game in bomb_data['results']:
            if game['deck'] != None:
                game_dict['names'].append(game['name'])
                game_dict['decks'].append(game['deck'])
                game_dict['platforms'].append(game['platforms'])
                game_dict['releases'].append(game['original_release_date'])
    return game_dict
game_data = create_full_db('games')    

    
import nltk 
import re
import string
#Define a new tokenizer for clustering
def tokenize_and_stem(text):
    snowball = nltk.stem.snowball.SnowballStemmer('english')
    punc = re.compile('[%s]' % re.escape(string.punctuation))
    tokens = []
    stems = []
    text = text.lower()
    text = punc.sub('', text)
    tokens.append(nltk.word_tokenize(text))
    for token in tokens:
        for word in token:
            stems.append(snowball.stem(word))
    return stems
    
#Define another tokenizer that doesn't stem so we can match stems to words later  
def tokenize_no_stem(text):
    punc = re.compile('[%s]' % re.escape(string.punctuation))
    tokens = []
    words = []
    text = text.lower()
    text = punc.sub('', text)
    tokens.append(nltk.word_tokenize(text))
    for token in tokens:
        for word in token:
            words.append(word)
    return words

#Create list of stemmed an non-stemmed words to match up
def vocab(text):
    totalvocab_stemmed = []
    totalvocab_tokenized = []
    for i in text:
        allwords_stemmed = tokenize_and_stem(i) #for each item in 'synopses', tokenize/stem
        totalvocab_stemmed.extend(allwords_stemmed) #extend the 'totalvocab_stemmed' list
        allwords_tokenized = tokenize_no_stem(i)
        totalvocab_tokenized.extend(allwords_tokenized)    
            
    vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index = totalvocab_stemmed)
    return vocab_frame
vocab_frame = vocab(game_data['decks'])

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

#Create stop words and add a bunch of words not relevant to our genre clusters
stop_words = nltk.corpus.stopwords.words('english')
stop_words.append('featur')
stop_words.append('sequel')
stop_words.append('originally')
stop_words.append('set')
stop_words.append('based')
stop_words.append('franchis')
stop_words.append('seri')
stop_words.append('instal')
stop_words.append('first')
stop_words.append('one')
stop_words.append('second')
stop_words.append('two')
stop_words.append('2')
stop_words.append('third')
stop_words.append('final')
stop_words.append('version')
stop_words.append('entri')
stop_words.append('new')
stop_words.append('develop')
stop_words.append('publish')
stop_words.append('releas')
stop_words.append('pc')
stop_words.append('playstat')
stop_words.append('nintendo')
stop_words.append('wii')
stop_words.append('ds')
stop_words.append('ios')
stop_words.append('famicom')
stop_words.append('sega')
stop_words.append('xbox')
stop_words.append('live')
stop_words.append('origin')
stop_words.append('japan')
stop_words.append('boy')
stop_words.append('color')
stop_words.append('must')
stop_words.append('base')
stop_words.append('name')
stop_words.append('terms')
stop_words.append('play')
stop_words.append('player')
stop_words.append('popular')
stop_words.append('onli')
stop_words.append('use')
stop_words.append('control')
stop_words.append('take')
stop_words.append('super')
stop_words.append('made')
stop_words.append('creat')
stop_words.append('exclus')
stop_words.append('includ')
stop_words.append('tri')
stop_words.append('video')
stop_words.append('studio')
stop_words.append('like')
stop_words.append('system')



#Define vectorizer parameters
tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words, max_df=0.3, min_df = 0.01,
                                 use_idf=True, tokenizer=tokenize_and_stem)

#Create TFIDF Matrix
tfidf_matrix = tfidf_vectorizer.fit_transform(game_data['decks'])
print(tfidf_matrix.shape)
terms = tfidf_vectorizer.get_feature_names()
#dist = 1 - cosine_similarity(tfidf_matrix)


#KMeans Clustering
num_clusters = int(round(np.sqrt(len(terms)/2)))
km = KMeans(n_clusters = num_clusters, random_state=3)
km.fit(tfidf_matrix)
clusters = km.labels_.tolist()

        
print("Top terms per cluster:")
print()
#sort cluster centers by proximity to centroid
order_centroids = km.cluster_centers_.argsort()[:, ::-1] 

for i in range(num_clusters):
    print("Cluster %d words:" % i, end='')
    
    for ind in order_centroids[i, :3]: #replace 6 with n words per cluster
        print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0], end=',')
    print() 
    



    