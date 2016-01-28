# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 15:46:07 2015

@author: Rich
"""


#Blizzard API
import requests
from PIL import Image
from StringIO import StringIO


def pull_info(realm, char):
   
    base_url = 'https://us.api.battle.net/wow/character/'
    locale = '?locale=en_US'
    api_key = '&apikey=fvkv5558kkca6ctja86hhzy62pjsk8sq'
    fields = '&fields=progression'
    
    full_url = base_url + realm + '/' + char + locale + api_key + fields
    
    char_info = requests.get(full_url).json()
    return char_info
    
lograr = pull_info('Illidan', 'Lograr')

img = requests.get('http://render-api-us.worldofwarcraft.com/static-render/us/illidan/176/134424240-profilemain.jpg')
Image.open(StringIO(img.content))




