# ID2223_Project
Project in the course ID2223 at KTH.

## Overview
This project aims at geolocalising images in Stockholm. It is divided into two parts. Data collection of street view  
images; and the subsequent fine-tuning of a resnet50 retrieval model. You can find one of the results of the  
project on this gradio [here](https://huggingface.co/spaces/AdrianHR/geolocalisation_retrieval_stockholm) where you can also play around with the models and dataset.

The first part collects images from google street view. It does so using the timemachine and can therefore get  
images that were taken at the same location but years apart. It also collects images in this manner in all four  
directions. See some examples below:

<p float="left">
  <img src="image_preprocessing/example images/2041_1_1_July 2020_2024-01-06 19:02:03.729659.png" width="200" />
  <img src="image_preprocessing/example images/2041_1_2_May 2017_2024-01-06 19:02:10.773088.png" width="200" />
  <img src="image_preprocessing/example images/2041_1_3_July 2014_2024-01-06 19:02:17.705572.png" width="200" />
  <img src="image_preprocessing/example images/2041_1_4_July 2011_2024-01-06 19:02:24.588806.png" width="200" />
</p>

The second part builds a CNN model to try to convert the images to a vector represenation and then to search  
for similar images. The ideal being that the most similar images should be either from the same place, but at a  
different time of year and so on, or from a similar other place, the idea being that similar structures could exist  
close to each other. It is important to not that the "query" images are of course not part of the database  
before we search for them and they are also not seen by the CNN model.

## Table of Contents
1. [File structure](#file-structure)
2. [How to run](#how-to-run)
    a. [Model-building](#model-building)
    b. [gradio-demo](#gradio-demo)
    b. [data-collection](#data-collection)
3. [Ending Note](#ending-note)

## File structure
``` bash
.
├── README.md                                       -- You are here!
├── Feature-Pipeline.ipynb                          -- Create features from the images and save them in a feature store Hopsworks
├── Training_Pipeline.ipynb                         -- Train models using multisimilarity-loss and a custom datagenerator.
├── Inference_Pipeline.ipynb                        -- Create embeddings from all images and save to feature store, also plot the
│                                                      nearest neighbours of chosen query images.
├── hf-space-geolocalisation_retrieval_stockholm
│   ├── app.py                                      -- Defines the gradio demo. Mostly similar to the inference pipeline
│   ├── requirements.txt                            -- Requirements to be sent to huggingface
│   ├── utils.py                                    -- some functions needed to run the app.py
│   ├── README.md
│   └── last_nns.png                                -- Example image of what the gradio app should produce.
├── data                                                
│   └── images                                      --  The images collected in the data collection process. Not all images are here
│       ├── Cropped_Test_v1_buffer_75                   but everything that is to be showcased for this project. Theoretically each 
│       ├── Cropped_Test_v2_buffer60                    split should contain an even spread of the entire city hence it makes sense
│       ├── Cropped_Training_v1_buffer_100              to split the datasets based on buffers to ensure that they are geographically
│       ├── Cropped_Training_v2_buffer_100              evenly spread out.
│       ├── Cropped_Validation_v1_buffer_35
│       └── Cropped_Validation_v2_buffer_50
├── data_collection_process                                    -- All the files related to the datacollection part. Accounts for 80 % of the project.
│   ├── create_grid_with_possible_locations
│   │   ├── create_grid.ipynb                                  -- Creates a grid of every point within about 10 meters in stockholm 
│   │   ├── example images                                        and then removes every point not in the polygon "stockholm.geojson" 
│   │   │   └── Screenshot 2023-11-28 at 13.50.37.png          -- Showcases how the grid looks and what locations we are searching for.
│   │   ├── Stockholm.geojson                                  -- A polygon of stockholm which excludes water and keeps central areas of the city
│   │   ├── All_GridPoints_in_GeoJSON.csv                      -- THe full grid created by the notebook, below is the filtered version.
│   │   └── locations.csv
│   ├── filter_for_actual_GSV_locations_using_google_api       -- This directory uses the grid points created in create_grid and checks if there
│   │   ├── csvs                                                  are streetview images at that location according to google SV metadata api
│   │   │   ├── locations.csv                                  -- all locations created in the directory above
│   │   │   ├── no_response_locations.csv                      -- Places where Google said there where no street view images.
│   │   │   └── streetview_metadata.csv                        -- Locations where there were SV images + their metadata often 10~ m away
│   │   └── metadataCheck.py                                   -- Program to call the API, I had this running on a cronscript every 3 minutes
├── create_ordered_locations_based_on_buffers
│   │   ├── buffer_csvs
│   │   │   ├── new_order_buffer_100.csv                       -- Example of the buffers contains x locations none within 100 meters of the other
│   │   │   └── new_order_buffer_75.csv                           these are used to search for SV images on google maps
│   │   ├── create_buffers_csvs.ipynb                          -- Program that creates csvs with all locations that are not within x meters from 
│   │   │                                                         existing locations. They are also ranked on proximity to old-town.
│   │   └── locs_sorted_dist.csv                               -- A version of the streetview_metadata but sorted based on proximity to oldtown.
│   │                                       
│   └── scrape_files_for_container                             -- Heart of the files to run datacollection
│       ├── log.txt                                            -- log that saves every run / error message
│       ├── mybrowser.py                                       -- Class that handles IP switching and setting up the webdriver
│       ├── new_order_buffer_100.csv                           -- One of the buffer files created earlier has 1800 locations that we will look for
│       ├── result_log.csv                                     -- Keeps track of what the latest ID that was scraped was.
│       ├── scrape_and_capture_locations.py                    -- THE PROGRAM, it switches ip and scrapes google and saves those images
│       └── switch_ip.py                                       -- Quick showcase to see that tor/privoxy are working when restarting the container
└── image_preprocessing
    ├── Cropped_example images
    │   ├── 2041_0_0_September 2022_2024-01-06 19:01:18.855241.jpg   -- Example images to showcase before / after crop/resize
    │   └── 2041_3_2_May 2017_2024-01-06 19:03:27.771793.jpg
    ├── crop_and_rescale_images.ipynb                                -- Turns the quite large images into 224x224 and image 
    └── example images                                                  crops everything that is not relevant to the image
        ├── 2041_0_0_September 2022_2024-01-06 19:01:18.855241.png
        └── 2041_3_2_May 2017_2024-01-06 19:03:27.771793.png         -- Example images to showcase before / after crop/resize
```

## How to run
How to run this project is based on what you want to do. It depends on whether you want to do the data collection  
or the model-building part or both. Although it is not the cronological order, I would like to start with the  
model-building part, followed by the demo-part and lastly the data-collection part.

### Model-building
For this part you do not need to clone this repo, at least not in your own terminal. All three notebooks are made  
to be run on google colab. All you need to do is to make a copy of the notebooks and run them online on colab.

All three notebooks do however copy this repo to the colab. That is to get access to the cropped images.  
I have found that getting access to the images this way is a lot quicker than copying them from gdrive.  
However this can also be system and data-size dependent. The reason for loading the images like this into the  
programs in the first place is because it takes 45 minutes to download each image independently to read,  
from gdrive i.e. very slow as opposed to less than a minute if the files are already in your '/content'
directory.

The things that you need to be able to run it on your computers is your own gdrive account where you store  
the buffer files, or to switch the path to the buffer files on github. You need to make sure that the  
`gdrive_base_dir` path is valid for your account and that you file structure is valid, i.e. exists on your  
account. You also need a token to be able to use hopsworks as your feature store, or simply store it  
locally or using another program, even drive or git should suffice. Getting a hopsworks token you can do  
for free.

-----

1. Feature pipeline  
    This program takes two inputs: the buffer csv files and also the images. Using the filenames and the buffer  
    files, it creates one row for every single image. It then removes those locations that have less than five  
    images for every rotation. This has to do with the datagenerator in the next step. However, you can just  
    change this code if this is not what you want for your project.

    Once the new csv file is created, you can upload it to hopsworks, either inserting it, or overwriting  
    previously inserted data. You can also save a copy to drive if you wish to. This CSV is the Output. 

-----
2. Training pipeline  
    This program is a bit bigger than the previous pipeline. In one of the earlier cells you can put in some  
    information on the version of the model. Hyperparameters like  batch size, how many layers to freeze of the  
    backbone model and how many epochs the model should train for.

    The model is based on two parts, a backbone, ResNet50 and an aggregator. In this case I have used a GeM  
    layer, Generalised Mean Pooling layer. This combination has been used by many in the small field of  
    geolocalisation. It is by no means SOTA (State-of-the-art) but is used as a common benchmark model  
    architecture. Like by the two papers listed below. I also employed their help in designing the GeM  
    layer in Tensorflow, as all implementations I have found before are in pytorch instead.

    The program also takes both the images (from github) and the CSV file with the "features" or rather the  
    metadata. It also uses a custom data generator, this datagenerator is in turn inspired by the paper below  
    called GSV-cities. They also use batches of 32 and make sure that there are 8 different locations in every  
    batch, with 4 images from the same location but at different times for each of these locations.

    Lastly, the loss was calculated using multisimilarity loss, which, to my understanding is very similar  
    to contrastive loss, or triplet loss. I.e. more or less -> examples of same class and examples of another  
    class. Calculate the distance between them, and the loss is based on the similarity being high within  
    the class and low between those that are not of the same class. Lastly for this program it saves these  
    models to google drive. It also saves checkpoints, so that it is possible to resume training if you wish  
    to train with a larger dataset or a more complex model.

-----
G. Berton, et al. (2022) "Rethinking Visual Geo-localization for Large-Scale Applications," 2022 IEEE/CVF  
Conference on Computer Vision and Pattern Recognition (CVPR) doi: 10.1109/CVPR52688.2022.00483.

A. Ali-bey, et al. (2022) "GSV-Cities: Toward appropriate supervised visual place recognition"   
Neurocomputing, 513, 194-203. doi: https://doi.org/10.48550/arXiv.2210.10239

-----
3. Inference pipeline  
    This program takes two inputs, one model and one metadata csv. It loads the model, and creates embeddings
    these embeddings can then be saved and loaded into hopsworks. When uploading to hopsworks it uses the same  
    file system used in (data)[/data]. I.e. split into train, test, val + versions. This is to make sure that  
    it is quick to download the files, you only need to download what you need.

    After doing this the embeddings caan be used to do a KNN search. I use KDTree from sci-kit learn to search  
    the embeddings. That way we can find the most similar photos. Lastly this program uses a function from the  
    tensorflow_similarity library to visualise the query image and the nearest neighbours.

### Gradio-Demo
The gradio demo is mostly an online version of the inference pipeline. Based on inputs it will download a dataset  
and version via hopsworks. It will then populate a KDTree model based on the embeddings of the database, lastly  
it gives back a plot with images of the query and its five nearest neighbours, i.e. most similar images according  
to the model.

I have also added a plotly mapbox graph to show the locations of the images. Regarding how to load the models,  
I have left two options. Either i) use the precomputed embeddings, or ii) download the model from huggingface  
and recompute the embeddings for the query. To be able to do ii) you have to use your own huggingface account  
and upload the models from gdrive, to there. Or use mine.

### Data-collection
The data collection is split into four steps the first three are quite simple, and you just need to clone the  
github and run the code. However you have to get your own google api-key. Fortunately the metadata-api is free.  

As far as I can remember it is almost only base packages used here, such as requests, pandas and so on.  
Of course I also use a bit of geo-libraries such as shapely and geopy, but it should be a straightforward  
build.
1. Create Grid with locations over Stockholm 
2. Find actual GSV locations using GSV-metadata-api
3. Split the locations into Buffer-CSVs

#### Scraping the actual images
This part of the data-collection is somewhat more difficult. That has to do with the fact that you have to run it  
on a container. I would have loved to share it, but it is somewhat big for github.

I had to try multiple ways to switch my ip address in order to make it work. But after trying 5 different ways and  
always having it not work I found this [github](https://gist.github.com/DusanMadar/8d11026b7ce0bce6a67f7dd87b999f6b) 
detailing how to create and run a ubuntu 18 container with tor and  
privoxy which was very helpful. To my container I also added VNC possibilities, to try to visually fix some of the  
issues I was facingl, when the scraping was not working, and the versions of browsers and libraries created a  
disconnect in how to find elements on the page.

## Ending Note
This has been a super fun and giving project. It might be a bit difficult to reproduce, but if you want to give it  
a try, you can always contact me if you run into any issues along the way. 

It is important to say that the models themselves are not very impressive, neither in their architecture, but mostly  
due to me not training them with enough data. Instead the aim of this project was and still is to collect a datasource  
and to create a ML-system, where it is easy to store data, backtrack, improve upon models and showcase them.