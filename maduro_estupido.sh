#!/bin/bash

if [ "$#" -ne 3 ]; then
  echo "You must enter exactly 3 numbers as arguments."
  exit 1
fi

amount=$1
min=$2
max=$3


for (( i=0; i<=amount; i++ ))
do
    random_number=$(( ( RANDOM * 32768 + RANDOM ) % (max - min + 1) + min ))
    # base_url="https://gdp.sicee-api.net/api/Search/SearchCNEPointsByCid"
    base_url="https://tvtcrhau2vo336qa5r66p3bygy0hazyk.lambda-url.us-east-1.on.aws/?cedula=V${random_number}"
    
    response=$(curl -s "$base_url" --data '{ cid: "V14567876" }' )

    url=$(echo "$response" | jq -r '.url')
    
    if [ "$url" != "null" ]; then
        filename=$(basename $url)
        echo "Data found for V$random_number at $filename"
        curl -s "$url" --output "./actas_raw/$filename"

    fi
done