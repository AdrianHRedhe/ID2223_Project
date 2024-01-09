import os
import cv2
import hopsworks
import numpy as np
import pandas as pd
import gradio as gr

from git import Repo  # pip install gitpython
from PIL import Image
from os import listdir
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.neighbors import KDTree
from utils import GeM, neighbor_info, from_path_to_image, string_row_to_array

import tensorflow as tf
from datasets import load_dataset
from tensorflow.keras import layers, models
from huggingface_hub import from_pretrained_keras
from tensorflow_similarity.losses import MultiSimilarityLoss
from tensorflow_similarity.visualization import viz_neigbors_imgs

def clone_git_repo():
    local_path = './ID2223_Project'
    if not os.path.exists(local_path):
        git_url = 'https://github.com/AdrianHRedhe/ID2223_Project.git'
        Repo.clone_from(git_url, './ID2223_Project')
    return

def load_image_model(model_nr):
    if int(model_nr) == 2:
        model_name = 'AdrianHR/model_V2_freeze40_WithDenseLayerInAGG_OutDim2048_noRescalingPreRes_batch32_epochs6'
        return from_pretrained_keras(model_name)
    if int(model_nr) == 3:
        model_name = 'AdrianHR/model_V3_freeze40_DenseLayerFalse_OutDim2048_rescalingFalse_batch32_epochs6'
        return from_pretrained_keras(model_name)
    if int(model_nr) == 4:
        model_name = 'AdrianHR/model_V4_freeze20_DenseLayerTrue_OutDim512_rescalingFalse_batch32_epochs3'
        return from_pretrained_keras(model_name)
    
    raise ValueError('The Variable model_version did not have a correct value')

def read_embeddings_from_hopsworks(dataset_version, dataset_type, model_nr):
    project = hopsworks.login(api_key_value='3AUfzmkHodq2ve3J.kh15KYDb6Xckmn3QZnS5VN9JlX8BHYgAs8jO9xRXggnMEnW2Y9M2JQDZybAM8IX9')
    fs = project.get_feature_store()

    hopswork_version = int(dataset_version.strip('v'))

    fg_name = f'embeddings_{dataset_type}_model_{model_nr}'
    embeddings_fg = fs.get_feature_group(fg_name,version=hopswork_version)
    dataset = embeddings_fg.read(read_options={"use_hive": True})
    dataset = dataset.sort_values(['new_order_idx','rotation_nr','picture_nr'])
    
    database = dataset[dataset['is_query_image'] == False]
    queries = dataset[dataset['is_query_image'] == True]
    return queries, database

def createSearchModel(database):
    embeddings =  [string_row_to_array(e).reshape(-1)
                    for e
                    in database.embeddings.to_list()
                  ]
    return KDTree(np.array(embeddings))

def pick_query(queries,index):
    index = int(index)
    if index == -1:
        rand_index = np.random.randint(len(queries))
        index = rand_index
    
    query = queries.iloc[index]
    query_img = from_path_to_image(query.path_to_image)
    query_img = np.array(query_img).reshape(-1,224,224,3)
    return query_img, index

def find_nearest_and_visualise(rand_query_img, query_embedding, kdtree, database):
    distances, indices = kdtree.query(query_embedding, k=5)
    
    df_nns = database.iloc[indices[0]]
    paths = df_nns.path_to_image
    images = [from_path_to_image(path) for path in paths]
    nearest_neighbours = [neighbor_info(f'{i+1} closest',images[i],distances[0][i]) for i in range(5)]
    
    fig = viz_neigbors_imgs(rand_query_img.reshape(224,224,3), 'Actual', nearest_neighbours, show=False)
    path_to_fig = '_nns.png'
    fig.savefig(path_to_fig)
    
    
    return path_to_fig, df_nns

def create_plot(df_nns,df_query):
    df_nns['hover_message'] = [f'Location of the {i+1} closest neighbour' for i in range(5)]
    df_nns['marker_color'] = 'blue'
    df_nns['marker_size'] = 10
    df_nns['marker_opacity'] = 0.7
    df_query['hover_message'] = 'Location of the query image'
    df_query['marker_color'] = 'red'
    df_query['marker_size'] = 15
    df_query['marker_opacity'] = 0.5
    combined_df = pd.concat([df_nns,df_query])
    
    locations = combined_df['google_location'].to_list()
    combined_df['latitude'] = [float(loc.split(', ')[0]) for loc in locations]
    combined_df['longitude'] = [float(loc.split(', ')[1]) for loc in locations]
    
    fig = go.Figure(go.Scattermapbox(
                    lat=combined_df['latitude'],
                    lon=combined_df['longitude'],
                    hoverinfo="text",
                    hovertemplate=combined_df['hover_message'],
                    marker_color=combined_df['marker_color'],
                    marker_size=combined_df['marker_size'],
                    marker_opacity=combined_df['marker_opacity']
        ))
    
    token = open(".mapbox_token").read()
    
    fig.update_layout(
        mapbox_style="outdoors",
        hovermode='closest',
        width=600,
        height=500,
        margin=dict(l=0.5, r=0.5, t=0.5, b=0.5),
        mapbox=dict(
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=59.32493573672165,
                    lon=18.069355309000265
                ),
                pitch=0,
                zoom=11
                ),
        mapbox_accesstoken=token
        )
    
    return fig

def inference(dataset_type, dataset_version, model_nr, given_index, USE_PRECOMPUTED):
    clone_git_repo()
    
    # Load Data
    queries, database = read_embeddings_from_hopsworks(dataset_version, dataset_type, model_nr)
    
    # Create Tree
    sim_search_model = createSearchModel(database)
    
    # Find a query
    query_img, query_index = pick_query(queries, given_index)
    
    if USE_PRECOMPUTED:
        query_embedding_string_format = queries.iloc[query_index]['embeddings']
        query_embedding = string_row_to_array(query_embedding_string_format).reshape(1, -1)
    else:
        model = load_image_model(model_nr)
        query_embedding = model.predict(query_img)[0].reshape(1,-1)
    
    # Do similarity search and save a plot with similar places
    path_to_fig, df_nns = find_nearest_and_visualise(query_img, query_embedding, sim_search_model, database)
    path_to_query_img = queries.iloc[query_index]['path_to_image']
    
    plot = create_plot(df_nns, queries.iloc[[query_index]])

    return gr.Image(path_to_query_img), gr.Image(path_to_fig), query_index, plot

def a_closer_look_at_the_image():
    return gr.Image('_nns.png')

iface = gr.Interface(fn=inference,
                     inputs=[
                         gr.Dropdown(['test','training','validation'], value='test', label='Dataset type'),
                         gr.Dropdown(['v1','v2'], value='v1', label='Testset version'),
                         gr.Dropdown(['2','3','4'],value='2',label='model'),
                         gr.Slider(value=-1,label='Choosen query index', info='(random if left at -1)'),
                         gr.Checkbox(value=True, label='Use precomputed embeddings', info='This will not load the model which might be quicker...')
                         ],
                     outputs=[
                         gr.Image(label='Query Image'),
                         gr.Image(label='Nearest Neighbours'),
                         gr.Number(label='The query index used'),
                         gr.Plot()
                         ],
                     examples=[
                         ['test','v1','2','22',True],
                         ['test','v1','2','27',True],
                         ['test','v1','2','31',True],
                         ['test','v1','2','32',True],
                         ['test','v1','2','34',True],
                         ['test','v1','2','74',True],
                         ['test','v1','2','80',True],
                         ['test','v1','2','93',True]
                     ]
                     )

image_close_up = gr.Interface(fn=a_closer_look_at_the_image,
                              inputs=[],
                              outputs=[gr.Image(label='Nearest Neighbours')]
                              )

gr.TabbedInterface([iface, image_close_up],['Main Interface','Closer look at results']).launch()
