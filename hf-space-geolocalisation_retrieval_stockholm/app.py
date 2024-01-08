import os
import cv2
import numpy as np
import pandas as pd
import gradio as gr
from git import Repo  # pip install gitpython
from PIL import Image
from os import listdir
from datetime import datetime
import matplotlib.pyplot as plt
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

def load_image_model():
    return from_pretrained_keras('AdrianHR/model_V6_freeze0_DenseLayerTrue_OutDim512_rescalingTrue_batch32_epochs6')

def load_embeddings(version):
    dataset = load_dataset("AdrianHR/embeddings_model_6")['test']
    dataset = dataset.to_pandas()
    #dataset[('dataset_version' == version) & ('dataset_type' == type)]
    #dataset = dataset[('dataset_version' == version)] #& ('dataset_type' == type)]
    
    query = dataset[dataset['is_query_image'] == True]
    database = dataset[dataset['is_query_image'] == False]
    return query, database

def createSearchModel(database):
    embeddings =  [string_row_to_array(e)
                    for e
                    in database.embeddings.to_list()
                  ]
    
    return KDTree(np.array(embeddings))

def pick_query(queries):
    rand_index = np.random.randint(0,len(queries))
    rand_query = queries.iloc[rand_index]
    rand_query_img = from_path_to_image(rand_query.path_to_image)
    rand_query_img = np.array(rand_query_img).reshape(-1,224,224,3)
    print(f'Querying: {rand_index}')
    return rand_query_img

def find_nearest_and_visualise(rand_query_img, model, kdtree, database):
    query_embedding = model.predict(rand_query_img)
    distances, indices = kdtree.query(query_embedding, k=5)
    
    paths = database.iloc[indices].path_to_image
    images = [from_path_to_image(path) for path in paths]
    nearest_neighbours = [neighbor_info(f'{i+1} closest',images[i],distances[0][i]) for i in range(5)]
    fig = viz_neigbors_imgs(rand_query_img.reshape(224,224,3), 'Actual', nearest_neighbours, show=False)
    
    path_to_fig = 'last_nns.png'
    fig.savefig(path_to_fig)
    return path_to_fig

def inference(given_index, version):
    clone_git_repo()
    model = load_image_model()
    queries, database = load_embeddings(version)
    
    sim_search_model = createSearchModel(database)
    
    if given_index == 0:
        rand_query_img = pick_query(queries)
    else:
        rand_query_img = pick_query(queries)
        
    find_nearest_and_visualise(rand_query_img, model, sim_search_model)
    print(version)
    path_to_fig = 'last_nns.png'

    return gr.Image(path_to_fig)


iface = gr.Interface(fn=inference,
                     inputs=[
                         #gr.Dropdown(['test','training','validation'], label='Dataset type'),
                         gr.Dropdown(['v1','v2'], label='Testset version'),
                         gr.Slider(label='Choosen query index (random if left at 0)')
                         ],
                     outputs=gr.Image()
                     )
iface.launch()


# Implement Hopswork read at a later date
# def read_metadata_from_hopsworks:
    #import hopsworks
    #project = hopsworks.login(api_key_value='3AUfzmkHodq2ve3J.kh15KYDb6Xckmn3QZnS5VN9JlX8BHYgAs8jO9xRXggnMEnW2Y9M2JQDZybAM8IX9')
    #fs = project.get_feature_store()

    #image_meta_data_fg = fs.get_feature_group('image_metadata_fg',version = 1)
    #metadata_df = image_meta_data_fg.read(read_options={"use_hive": True})
    # return metadata_df
