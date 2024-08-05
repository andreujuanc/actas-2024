#!/bin/bash

if [ "$#" -ne 3 ]; then
  echo "You must enter exactly 3 numbers as arguments."
  exit 1
fi

amount=$1
min=$2
max=$3

for (( i=0; i<amount; i++ ))
do
    random_number=$(( ( RANDOM * 32768 + RANDOM ) % (max - min + 1) + min ))
    base_url="https://gdp.theempire.tech/api/data?cdi=v${random_number}"

    response=$(curl -s "$base_url")
    
    # Check if the response is {"error":"not-found"}
    if [ "$response" == '{"error":"not-found"}' ]; then
        echo "Data not found for V$random_number"
        continue
    fi

    echo $response

    # Extracting DO_DS_NAME and DO_DS_BUCKET from the response
    do_ds_name=$(echo "$response" | jq -r '.acta.DO_DS_NAME')
    do_ds_bucket=$(echo "$response" | jq -r '.acta.DO_DS_BUCKET')

    if [ "$do_ds_name" != "null" ] && [ "$do_ds_bucket" != "null" ]; then
        # Constructing the download URL
        download_url="https://$do_ds_bucket.s3.amazonaws.com/$do_ds_name"
        filename=$(basename "$do_ds_name")

        # Check if the file already exists
        if [ -f "./actas2/$filename" ]; then
            echo "File $filename already exists, skipping"
            continue
        fi

        # Downloading the file
        curl -s "$download_url" --output "./actas2/$filename"
        echo "Downloaded $filename"
    else
        echo "Required data not found in the response for V$random_number"
    fi
done