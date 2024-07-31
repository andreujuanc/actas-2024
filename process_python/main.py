import image_pr
import qr_process
import analize
import json
import os

# Define the path to the folder containing the images
folder_path = '../actas'

# List of valid image extensions
valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

# Loop through the folder and get the paths of the image files
totals= {}
actas = 0
actas_np = 0

for filename in os.listdir(folder_path):
    # Check if the file is an image based on its extension
    try:
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            image_path = os.path.join(folder_path, filename)
            qr = image_pr.find_qr(image_path,filename)
            qr_string = qr_process.do(qr)
            analize.update(qr_string, totals)
            actas += 1
            print(f'Maduro Dictador: {totals["NICOLAS MADURO"]} , Edmundo: {totals["EDMUNDO GONZALEZ"]}, Actas: {actas} , Actas no procesadas: {actas_np}')
    except Exception as e:
        print(e)
        print(filename)
        actas_np += 1
        pass
# Save the object to a JSON file
totals["ACTAS"] = actas
totals["ACTAS NO PROCESADAS"] = actas_np
with open('resultados.json', 'w') as json_file:
    json.dump(totals, json_file, indent=4)

