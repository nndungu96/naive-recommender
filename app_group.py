import streamlit as st
import pandas as pd
import template as t
import authenticate as a
import json
from itertools import cycle
from random import random
import pickle
#!pip install streamlit_authenticator 

st.set_page_config(layout="wide")

## Sidebar  ##
st.sidebar.title('Welcome to ')
st.sidebar.image('https://is4-ssl.mzstatic.com/image/thumb/Purple113/v4/a9/0d/a6/a90da68c-83cc-6dac-c03a-67376e3f180a/AppIcon-0-0-1x_U007emarketing-0-0-0-7-0-0-sRGB-0-0-0-GLES2_U002c0-512MB-85-220-0-0.png/246x0w.png',use_column_width=True)


with st.sidebar.expander('How the recommendation system works'):
  st.markdown('''
The idea of establishing a recommendation system is governed by the principle of assisting
users in the selection of content of interest to them. With that in mind, when the user
selects one of the video genres, the system filters the content by selecting 6 videos
from the category. The selection is random and can be renewed by refreshing the page.
Once the user selects a video to watch, the system recommends, based on the video
description, category, director, cast, presenter, and keywords, if applicable, six videos
similar to the one chosen by the user. The user can choose to diversify the content shown by choosing
"Balanced" or "More similar" on the right hand side of the screen. The more similar option will show videos
that are deemed different from the current video boased on the video
description, category, director, cast, presenter, and keywords.
The balanced option presents some similar and some different shows.
The category of recommendations called "Users similar to you enjoyed these shows" presents shows that were watched
or rated highly by users who have watched and rated similar shows to you. 

Due to the importance of cultural representation in Australia and to the ABC,
the platform offers a category of indigenous content, where the user will find a random
recommendation of indigenous videos.
If you are wondering why random selection is used, we inform you that this feature allows
the user to increase the diversity of options to choose from, which due to the
personalization of the experience can be reduced.

Finally, we inform you that the recommendation system does not consider sensitive
variables such as the user's ethnicity or gender to make recommendations.
''')

## create session states##
if 'ID' not in st.session_state:
  st.session_state['ID'] = 6889

if 'Category' not in st.session_state:
  st.session_state['Category'] = 'news'

if 'user' not in st.session_state:
  st.session_state['user'] = 0

# open the activities json file
with open('activities.json') as json_file:
  users_activities = json.load(json_file)

if 'activities' not in st.session_state:
    st.session_state['activities'] = users_activities

## Authentication ##
a.authenticate()

## Datasets ##

# Videos #
df = pd.read_csv('df_recommen_ABC.csv')

# Users #
df_users = pd.read_json('users.json')

#Predictions#
df_pred = pd.read_csv('collab_predictions.csv')

#Similarities
similarity = pickle.load(open('similarity.pkl','rb'))


## Get Categories ##
categories = df['Category'].unique().tolist()

## Retrieve category and title from category state ##
df_title = df[df['ID'] == st.session_state['ID']]
df_category = df[df['Category'] == st.session_state['Category']]
df_title = df_title.iloc[0]
if st.session_state['user']>0:
  df_user=df_pred[df_pred['user_id'] == st.session_state['user']]

def recs(df, id):
  index = df[df['ID'] == id].index[0]
  distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
  l = len(distances)
  if values == 'Balanced':
    recommended_show_names = []
    for i in distances[1:4] + distances[l-3:l]:
      recommended_show_names.append([df.iloc[i[0]].ID, df.iloc[i[0]].title,df.iloc[i[0]].image, df.iloc[i[0]].description])
    r = pd.DataFrame(recommended_show_names, columns = ['ID','title','image','description'])
  elif values == 'More diverse': 
    recommended_show_names = []
    for i in distances[l-6:l]:
      recommended_show_names.append([df.iloc[i[0]].ID, df.iloc[i[0]].title,df.iloc[i[0]].image, df.iloc[i[0]].description])
    r = pd.DataFrame(recommended_show_names, columns = ['ID','title','image','description'])
  elif values == 'More similar':
    recommended_show_names = []
    for i in distances[1:7]:
      recommended_show_names.append([df.iloc[i[0]].ID, df.iloc[i[0]].title,df.iloc[i[0]].image, df.iloc[i[0]].description])
    r = pd.DataFrame(recommended_show_names, columns = ['ID','title','image','description'])
        
  return r


col1, col2, col3 = st.columns((2,2,1))

with col1:
  st.image(df_title['image'], use_column_width='always')

with col2:
  st.title(df_title['title'])
  st.caption(df_title['description'])
  st.button('▶', key=random(), on_click=t.activity, args=(st.session_state['ID'], 'Watch'))
  st.button('👍', key=random(), on_click=t.activity, args=(st.session_state['ID'], 'Like'))
  st.button('👎', key=random(), on_click=t.activity, args=(st.session_state['ID'], 'Dislike'))
  st.button('Add to Watchlist', key=random(), on_click=t.activity, args=(st.session_state['ID'], 'Watchlist'))


with col3:
  values = st.radio('Would you prefer more accurate or more diverse recommendations?', 
                           options = ['More diverse', 'Balanced', 'More similar'], index = 1)

with st.expander("Categories"):
  cols = cycle(st.columns(6))
  for category in categories:
    next(cols).button(category, key=category, on_click=t.select_category, args=(category, ))

st.subheader("Titles in this category")
t.tiles(df_category.sample(6))

st.subheader("Indigenous Content")
t.tiles(df[df['diversity'] == 1].sample(6))

st.subheader("Recommended based on current selection and preferences")
r=recs(df, st.session_state['ID'])
t.tiles(r)
  
st.subheader("Users similar to you enjoyed these shows")
if(st.session_state['user'] == 0):
  st.markdown('''Please login to get user-based recommendations''')
else:
  t.tiles(df_user.sort_values(by='prediction', ascending=False).head(6))
  
  
