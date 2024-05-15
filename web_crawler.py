import requests
from bs4 import BeautifulSoup
import json
import os

# Conjunto para almacenar las URLs visitadas y evitar procesar la misma URL más de una vez
visited_urls = set()

# Profundidad máxima de recursión para el crawler
max_depth = 5

# Nombre del archivo donde se almacenará la información extraída
output_file = 'crawled_data.json'

def web_crawler(initial_url):
    # Elimina el archivo de salida si ya existe
    if os.path.exists(output_file):
        os.remove(output_file)
    # Inicia el proceso de crawling
    crawl(initial_url, 0)

def crawl(url, depth):
    # Verifica si la URL ya fue visitada o si se ha alcanzado la profundidad máxima
    if url in visited_urls or depth > max_depth:
        return

    # Añade la URL al conjunto de URLs visitadas
    visited_urls.add(url)
    print(f'Crawling: {url} at depth: {depth}')

    try:
        # Realiza una solicitud HTTP GET a la URL
        response = requests.get(url)
        # Lanza una excepción para errores HTTP
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Imprime el error y retorna si la solicitud falla
        print(f"Request failed: {e}")
        return

    # Analiza el contenido HTML de la página
    soup = BeautifulSoup(response.text, 'html.parser')
    # Encuentra todos los enlaces <a> con el atributo href
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

    # Extrae el contenido de las etiquetas <h1> y <p>
    page_data = {
        'h1': [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
        'p': [p.get_text(strip=True) for p in soup.find_all('p')]
    }

    # Guarda los datos extraídos en el archivo JSON
    save_data(url, page_data)

    # Repite el proceso para cada enlace encontrado en la página actual, incrementando la profundidad
    for link in links:
        crawl(link, depth + 1)

def save_data(url, data):
    try:
        # Si el archivo JSON no existe, lo crea y escribe un objeto JSON vacío
        if not os.path.exists(output_file):
            with open(output_file, 'w') as f:
                json.dump({}, f)

        # Abre el archivo JSON en modo lectura/escritura
        with open(output_file, 'r+') as f:
            # Carga los datos existentes del archivo JSON
            crawled_data = json.load(f)
            # Añade o actualiza la información de la URL actual
            crawled_data[url] = data
            # Vuelve al inicio del archivo y guarda los datos actualizados
            f.seek(0)
            json.dump(crawled_data, f, indent=4)
    except Exception as e:
        # Imprime un mensaje de error si ocurre algún problema al guardar los datos
        print(f"Error saving data: {e}")

if __name__ == "__main__":
    # URL inicial para comenzar el proceso de crawling
    initial_url = 'https://es.wikipedia.org/wiki/Kimetsu_no_Yaiba'  # Reemplaza con la URL inicial que quieras rastrear
    # Inicia el crawler
    web_crawler(initial_url)
