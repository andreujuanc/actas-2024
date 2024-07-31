# Scripts de procesamiento de actas

Este repositorio contiene dos scripts en Python diseñados para procesar imágenes de actas electorales, extrayendo información relevante y almacenándola en una base de datos SQLite.

## Descripción de los Scripts

### generate_votes_from_qrs.py

Este script se encarga de buscar códigos QR en las imágenes de las actas. Cada QR contiene información numérica que se extraerá y almacenará en una base de datos SQLite.

#### Funcionalidades:
- Escanea imágenes en busca de códigos QR.
- Extrae la información numérica contenida en los QR.
- Almacena la información extraída en una base de datos SQLite.

### generate_data_from_text.py

Este script utiliza OCR (Reconocimiento Óptico de Caracteres) para buscar y extraer información textual de las imágenes de las actas, como el estado, municipio y parroquia. Luego, actualiza la tupla correspondiente en la base de datos, utilizando el nombre de la imagen como referencia.

#### Funcionalidades:
- Utiliza OCR para extraer información textual de las imágenes.
- Busca datos específicos como estado, municipio y parroquia.
- Actualiza la base de datos SQLite con la información extraída, vinculando los datos por el nombre de la imagen.

## Instrucciones de Ejecución
Es importante estar en la carpeta "scripts-python" ya que va a buscar las actas a "../actas", aunque esto se puede mejorar.

1. **Ejecutar generate_votes_from_qrs.py primero:**

   Este script debe ejecutarse primero para asegurar que toda la información de los códigos QR se haya almacenado en la base de datos.

   ```bash
   cd scripts-python
   python generate_votes_from_qrs.py
   ```

2. **Ejecutar generate_data_from_text.py después:**

   Una vez que se haya ejecutado el primer script, ejecutar el segundo script para extraer y actualizar la información textual.

   ```bash
   cd scripts-python
   python generate_data_from_text.py
   ```

## Requisitos

- Python 3.x
- Librerías: 
  - `opencv-python`
  - `pyzbar`
  - `pytesseract`
  - `sqlite3`

Puedes instalar las dependencias necesarias utilizando `pip`:

```bash
pip install opencv-python pyzbar pytesseract sqlite3
```

## Tiempo de Ejecución

El procesamiento completo de las imágenes puede tardar algunas horas, dependiendo del número y tamaño de las imágenes.

## Datos Incluidos en el Repositorio
Como parte del repositorio, se incluye:

- Un fichero votes.db con la base de datos rellena después de ejecutar los scripts en la carpeta actas.
- Los mismos datos exportados a CSV y Excel para facilitar su análisis y manipulación.

## Notas

- Asegúrate de tener todas las imágenes de las actas en la carpeta correspondiente antes de ejecutar los scripts.
- La base de datos SQLite se creará automáticamente si no existe.

## Posibles mejoras

- Obtener la carpeta de las imágenes de las actas por parámetro.
- Unificar ambos scripts en uno solo.
- Limpiar la tabla para que no aparezcan las columnas "escuela" y "numero_colegio", ya que finalmente no se han utilizado.
- Comprobar en el primer script si la imagen ya ha sido tratada comprobando el nombre del imagen.
- ...