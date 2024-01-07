import requests
import csv
import os
import pandas as pd
import time

def get_street_view_metadata(api_key, location, size="600x300", fov=90, heading=0, pitch=0):
    base_url = "https://maps.googleapis.com/maps/api/streetview/metadata"

    params = {
        "size": size,
        "location": location,
        "fov": fov,
        "heading": heading,
        "pitch": pitch,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        print(f"Error: {response.status_code}")
        return None

def save_to_csv(results, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Location', 'Copyright', 'Date', 'Latitude', 'Longitude', 'PanoID', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

def save_checkpoint(index, filename):
    with open(filename, 'w') as file:
        file.write(str(index))

def load_checkpoint(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return int(file.read())
    else:
        return 0

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual Google API key
    api_key = ''

    # Specify the input file containing locations (one per line)
    path_to_dir = '/Users/adrian/Desktop/ThesisPreStudy/FindCoordsForGSVImages/'
    input_filename = f'{path_to_dir}/csvs/locations.csv'
    output_filename = f'{path_to_dir}/csvs/streetview_metadata.csv'
    no_response_filename = f'{path_to_dir}/csvs/no_response_locations.csv'

    # Specify the number of requests per batch
    n_requests = 100

    # Read locations from the input file
    locations = pd.read_csv(input_filename)
    results = pd.read_csv(output_filename)
    no_response_locations = pd.read_csv(no_response_filename)
    
    # Load the last successfully processed location index
    max_idx_results = results.Location_idx.max()

    if type(no_response_locations.Location_idx.max()) == int:
        max_idx_no_response = no_response_locations.Location_idx.max()
    else:
        max_idx_no_response = 0

    start_index=max(max_idx_results,max_idx_no_response)+1

    # Iterate through locations and make API calls
    for i in range(start_index, min(start_index + n_requests, len(locations))):
        current_idx = i
        time.sleep(0.75)
        location = locations.iloc[i].locations
        metadata = get_street_view_metadata(api_key, location)
        if metadata and metadata.get('status') == 'OK':
            result_entry = {
                'Location_idx': i,
                'Location': location,
                'Copyright': metadata['copyright'],
                'Date': metadata['date'],
                'Latitude': metadata['location']['lat'],
                'Longitude': metadata['location']['lng'],
                'PanoID': metadata['pano_id'],
                'Status': metadata['status']
            }
            result_df = pd.DataFrame(result_entry,index=[0])
            results = pd.concat([results, result_df], axis=0)
        elif metadata and metadata.get('status') == 'ZERO_RESULTS':
            other_df = pd.DataFrame({'Location_idx': i, 'Location': location},index=[0])
            no_response_locations = pd.concat([no_response_locations, other_df], axis=0)
        else:
            print(f"Failed to retrieve metadata for location: {location} with idx: {i}")

    results.to_csv(output_filename,index=False)
    no_response_locations.to_csv(no_response_filename,index=False)

    print("Processing complete. Results saved to", output_filename)
    print("Locations with no response saved to", no_response_filename)
    print(f'Currently at {current_idx} / {len(locations)} or {round(current_idx/len(locations),3)} %')
    print(f'Has no_response {round(len(no_response_locations)/(len(results)+len(no_response_locations)),4)} %')
