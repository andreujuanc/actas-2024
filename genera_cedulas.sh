#!/bin/bash

# Define el rango de números
start=1000000
end=30000000

# Genera los números en el rango y los guarda en un archivo
for ((i=start; i<=end; i++))
do
  echo $i
done > numeros.txt

# Organiza los números de forma aleatoria usando awk y sort
awk 'BEGIN {srand()} {print rand() "\t" $0}' numeros.txt | sort -k1,1n | cut -f2- > cedulas.txt

echo "Lista de números generada y organizada de forma aleatoria en el archivo cedulas.txt"
