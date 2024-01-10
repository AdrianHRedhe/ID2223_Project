# ID2223_Project
Project in the course ID2223 at KTH.

## Overview
This project aims at geolocalising images in Stockholm.  
It is divided into two parts. Data collection of street view  
images; and the subsequent fine-tuning of a resnet50  
retrieval model. You can find one of the results of the  
project on this gradio [here](https://huggingface.co/spaces/AdrianHR/geolocalisation_retrieval_stockholm) where you can also play  
around with the models and dataset.

The first part collects images from google street view.  
It does so using the timemachine and can therefore get  
images that were taken at the same location but years  
apart. It also collects images in this manner in all four  
directions. See some examples below:

<p float="left">
  <img src="image_preprocessing/example images/2041_1_1_July 2020_2024-01-06 19:02:03.729659.png" width="200" />
  <img src="image_preprocessing/example images/2041_1_2_May 2017_2024-01-06 19:02:10.773088.png" width="200" />
  <img src="image_preprocessing/example images/2041_1_3_July 2014_2024-01-06 19:02:17.705572.png" width="200" />
  <img src="image_preprocessing/example images/2041_1_4_July 2011_2024-01-06 19:02:24.588806.png" width="200" />
</p>

The second part builds a CNN model to try to convert  
the images to a vector represenation and then to search  
for similar images. The ideal being that the most similar  
images should be either from the same place, but at a  
different time of year and so on, or from a similar other  
place, the idea being that similar structures could exist  
close to each other. It is important to not that the 
"query" images are of course not part of the database  
before we search for them and they are also not seen by  
the CNN model.

## Table of Contents
1. [File structure](#file-structure)
2. [How to run](#how-to-run)

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
How to run this project is based on what you want to do.  
It depends on whether you want to do the data collection  
or the model-building part or both. 

### Data-collection
The data collection is split into four steps
#### Create Grid with locations over Stockholm 
#### Find actual GSV locations using GSV-metadata-api
#### Split the locations into Buffer-CSVs


### Model-building

### Gradio-Demo
