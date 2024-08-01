#Análisis de Datos Electorales de Venezuela

## Visión General

Este proyecto está diseñado para recopilar, procesar y analizar datos de las elecciones venezolanas del 28 de Julio de 2024. Incluye scripts para la recolección de datos, procesamiento de imágenes y tabulación de votos a partir de actas digitales con el fin de preservar y defender nuestros votos como venezolanos de ataques malicioso contra las bases de datos principales.

URL del repositorio: [https://github.com/andreujuanc/actas-2024](https://github.com/andreujuanc/actas-2024)

## Componentes

### 1. Scripts de Recolección de Datos

- `maduro_estupido.sh`: Recolecta datos de votación de una API específica.
- `maduro_estupido_v2.sh`: Una versión actualizada del script de recolección de datos.

Estos scripts generan aleatoriamente números de cédula venezolanos y consultan una API para recuperar los registros de votación correspondientes.

### 2. Procesamiento de Imágenes

- `postprocess.sh`: Optimiza imágenes JPEG de actas, reduciendo el tamaño de los archivos a 85KB.

### 3. Análisis de Datos

- `main.go`: El script principal de análisis escrito en Go. Procesa imágenes de actas, extrae datos de códigos QR y genera un archivo CSV con los resultados de la votación.

### 4. Scripts de Utilidad

- `stage_new.sh`: Un script de utilidad de Git para preparar (stage) archivos recién añadidos.

## Configuración y Uso

1. Asegúrate de tener instaladas las siguientes dependencias:
   - Go
   - jpegoptim
   - curl
   - jq

2. Clona el repositorio:
   ```
   git clone https://github.com/andreujuanc/actas-2024.git
   cd actas-2024
   ```

3. Ejecuta el script de recolección de datos:
   ```
   ./maduro_estupido_v2.sh [cantidad] [min] [max]
   ```
   Reemplaza `[cantidad]`, `[min]` y `[max]` con valores apropiados.

4. Procesa las imágenes recolectadas y las pone en la carpeta `actas`:
   ```
   ./postprocess.sh
   ```

5. Analiza los datos:
   ```
   go run qr/main.go
   ```

## Resultado

El script de análisis (`main.go`) genera un archivo CSV llamado `resultados.csv` que contiene la siguiente información para cada acta procesada:

- Nombre del archivo del acta
- Código del acta
- Votos para Maduro
- Votos para Edmundo González
- Votos para otros candidatos
- Total de votos válidos
- Total de votos nulos
- Total de votos inválidos


## Contribuciones

Las contribuciones para mejorar los scripts o ampliar el análisis son bienvenidas. Por favor, envía un pull request o abre un issue para discutir los cambios propuestos.


