# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 12:18:31 2015

@author: Rich
"""

import dota2api
import pandas as pd
import matplotlib.pyplot as plt
import urllib
from matplotlib.offsetbox import  OffsetImage

api = dota2api.Initialise(api_key='B59489C4C44B40A0DE123404D406577E')
hist = api.get_match_history(account_id=37483323)

#Create empty lists

match_list=[]
match_details_list=[]
hero_pics=[]

#Gets match details from all of my games and appends each hero I've played to match_list
for match in hist['matches']:
    details = api.get_match_details(match['match_id'])
    for player in details['players']:
        if player['account_id'] == 37483323:
            match_details_list=[]
            match_details_list.append(player['hero_name'])
            match_details_list.append(player['kills'])
            match_details_list.append(player['deaths'])
            hero_pic_url = "http://cdn.dota2.com/apps/dota2/images/heroes/" + player['hero_name'].lower() + "_vert.jpg"
            hero_pic_url2 = player['hero_name'].lower() + "_vert.jpg"
            hero_pics.append(urllib.urlretrieve(hero_pic_url, hero_pic_url2))
    match_list.append(match_details_list)

dota_df = pd.DataFrame(match_list, columns=['hero_name', 'kills', 'deaths'])

#View the head of the DataFrame and all its columns
from IPython.display import display
with pd.option_context('display.max_columns', None):
        display(dota_df)

#Number of games played by hero
#hero_counts = dota_df['hero_name'].value_counts()
#hero_counts.plot(kind='barh')

kills_by_hero = dota_df.pivot_table(columns='hero_name', values='kills', aggfunc='sum')
sorted_kills_by_hero = kills_by_hero.order()
kills_graph = sorted_kills_by_hero.plot(kind='bar', width = 1)
plt.title("Kills by Hero - All Time")
plt.ylim(0, 100)

dota_pic = plt.imread(hero_pics[0][0])
img = OffsetImage(dota_pic, zoom=0.09)
img.set_offset((340,290))
kills_graph.add_artist(img)