#!/bin/bash

# Check if cedulas.txt exists
if [ ! -f cedulas.txt ]; then
  echo "File cedulas.txt not found!"
  exit 1
fi

# Create the directory for downloads if it doesn't exist
mkdir -p actas

# Read the file line by line
while IFS= read -r cedula; do
  base_url="https://gdp.theempire.tech/api/data?cdi=v${cedula}"

  response=$(curl -s "$base_url")

  # Check if the response is {"error":"not-found"}
  if [ "$response" == '{"error":"not-found"}' ]; then
    echo "Data not found for V$cedula"
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
    if [ -f "./actas/$filename" ]; then
      echo "File $filename already exists, skipping"
      continue
    fi

    # Downloading the file
    curl -s "$download_url" --output "./actas/$filename"
    echo "Downloaded $filename"
  else
    echo "Required data not found in the response for V$cedula"
  fi
done < cedulas.txt
