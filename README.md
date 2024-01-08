# ID2223_Project
Project in the course ID2223 at KTH.

## Overview
This project aims at geolocalise images in Stockholm.  
It is divided into two parts.

The first part collects images from google street view.  
It does so using the timemachine and can therefore get  
images that were taken at the same location but years  
apart.

The second part builds a CNN model to try to convert  
the images to a vector represenation and then to search  
for similar images. The ideal being that the most similar  
images should be either from the same place, but at a  
different time of year and so on, or from a similar,  
maybe close by place.

### I dont have time to finish the description completely but everything will be finished by the time I present.

## Directory tree
``` bash
.
├── README.md                                           -- You are here
├── Feature-Pipeline.ipynb                              -- Create features from the images and save them in a feature store
├── Training_Pipeline.ipynb                             -- train models, special datagenerator and save them on drive
├── Inference_Pipeline.ipynb                            -- logic to 
├── data                                                
│   └── images                                          --
│       ├── Cropped_Test_v1_buffer_75
│       ├── Cropped_Test_v2_buffer60
│       ├── Cropped_Training_v1_buffer_100
│       ├── Cropped_Training_v2_buffer_100
│       ├── Cropped_Validation_v1_buffer_35
│       └── Cropped_Validation_v2_buffer_50
├── data_collection_process
│   ├── create_grid_with_possible_locations
│   │   ├── All_GridPoints_in_GeoJSON.csv
│   │   ├── Stockholm.geojson
│   │   ├── create_grid.ipynb
│   │   ├── example images
│   │   │   └── Screenshot 2023-11-28 at 13.50.37.png
│   │   └── locations.csv
│   ├── create_ordered_locations_based_on_buffers
│   │   ├── buffer_csvs
│   │   │   ├── new_order_buffer_100.csv
│   │   │   ├── new_order_buffer_35.csv
│   │   │   ├── new_order_buffer_45.csv
│   │   │   ├── new_order_buffer_50.csv
│   │   │   ├── new_order_buffer_60.csv
│   │   │   └── new_order_buffer_75.csv
│   │   ├── create_buffers_csvs.ipynb
│   │   └── locs_sorted_dist.csv
│   ├── filter_for_actual_GSV_locations_using_google_api
│   │   ├── csvs
│   │   │   ├── locations.csv
│   │   │   ├── no_response_locations.csv
│   │   │   └── streetview_metadata.csv
│   │   └── metadataCheck.py
│   └── scrape_files_for_container
│       ├── log.txt
│       ├── mybrowser.py
│       ├── new_order_buffer_100.csv
│       ├── result_log.csv
│       ├── scrape_and_capture_locations.py
│       └── switch_ip.py
└── image_preprocessing
    ├── Cropped_example images
    │   ├── 2041_0_0_September 2022_2024-01-06 19:01:18.855241.jpg
    │   └── 2041_3_2_May 2017_2024-01-06 19:03:27.771793.jpg
    ├── crop_and_rescale_images.ipynb
    └── example images
        ├── 2041_0_0_September 2022_2024-01-06 19:01:18.855241.png
        └── 2041_3_2_May 2017_2024-01-06 19:03:27.771793.png
```