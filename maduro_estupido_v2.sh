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
    # https://nodito01.democraciaactivas.com/api/Search/GetStates
    
    response=$(curl -s "$base_url" )
    echo $response

    url=$(echo "$response" | jq -r '.url')
    
    if [ "$url" != "null" ]; then
        echo "Data found for V$random_number at $filename"
        # filename=$(basename $url)
        # if [-f "./actas_raw/$filename"]; then
        #     echo "File already exists, skipping"
        #     continue;
        # fi

        # curl -s "$url" --output "./actas_raw/$filename"

    fi
done