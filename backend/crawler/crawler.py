import os
import PyPDF2
from bs4 import BeautifulSoup
import requests

GUTENBERG_BOOKS = {
    "quijote.txt": "https://www.gutenberg.org/cache/epub/2000/pg2000.txt",
    "celestina.txt": "https://www.gutenberg.org/cache/epub/1619/pg1619.txt",
    "lazarillo.txt": "https://www.gutenberg.org/cache/epub/320/pg320.txt"
}

WIKIPEDIA_PAGES = {
    "recuperacion_informacion.txt": "https://es.wikipedia.org/wiki/B%C3%BAsqueda_y_recuperaci%C3%B3n_de_informaci%C3%B3n",
    "ingenieria_informatica.txt": "https://es.wikipedia.org/wiki/Ingenier%C3%ADa_inform%C3%A1tica",
    "inteligencia_artificial.txt": "https://es.wikipedia.org/wiki/Inteligencia_artificial",
    "aprendizaje_automatico.txt": "https://es.wikipedia.org/wiki/Aprendizaje_autom%C3%A1tico"
}


def download_gutenberg_docs():
    base_dir = os.path.dirname(__file__)
    docs_path = os.path.abspath(os.path.join(base_dir, "..", "..", "docs"))

    os.makedirs(docs_path, exist_ok = True)

    for filename, url in GUTENBERG_BOOKS.items():
        file_path = os.path.join(docs_path, filename)

        if os.path.exists(file_path):
            print(f"El archivo {filename} ya existe.")
            continue

        print(f"Descargando {filename}...")
        try:
            response = requests.get(url, timeout = 30)
            if response.status_code == 200:
                with open(file_path, "w", encoding = "utf-8", errors = "ignore") as f:
                    f.write(response.text)
                print(f"{filename} descargado correctamente.")
            else:
                print(f"Error al descargar {filename}: código {response.status_code}")
            
        except Exception as e:
            print(f"Error al descargar{filename}: {e}")

def download_wikipedia_docs():
    base_dir = os.path.dirname(__file__)
    docs_path = os.path.abspath(os.path.join(base_dir, "..", "..", "docs"))
    os.makedirs(docs_path, exist_ok = True)

    API_URL = "https://es.wikipedia.org/w/api.php"

    for filename, page_title in WIKIPEDIA_PAGES.items():
        file_path = os.path.join(docs_path, filename)

        if os.path.exists(file_path):
            print(f"El archivo {filename} ya existe.")
            continue

        print(f"Descargando artículo de wikipedia: {page_title}...")

        params = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "extracts",
            "explaintext": True,
            "exsectionformat": "plain"
        }

        try:
            response = requests.get(API_URL, params = params, timeout = 30)
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))
            text = page.get("extract", "")

            if text.strip():
                with open(file_path, "w", encoding = "utf-8", errors = "ignore") as f:
                    f.write(text)
                print(f"{filename} descargado correctamente.")
            else:
                print(f"No se ha encontrado contenido para {page_title}.")
        
        except Exception as e:
            print(f"Error al descargar {filename}: {e}")

def download_wikipedia_docs_html():
    base_dir = os.path.dirname(__file__)
    docs_path = os.path.abspath(os.path.join(base_dir, "..", "..", "docs"))
    os.makedirs(docs_path, exist_ok = True)

    headers = {
        "User-agent": "RI-Práctica/1.0"
    }

    for filename, url in WIKIPEDIA_PAGES.items():
        file_path = os.path.join(docs_path, filename)

        if os.path.exists(file_path):
            print(f"El archivo {filename} ya fue descargado.")
            continue

        print(f"Descargado wikipedia (html): {url}")

        try:
            response = requests.get(url, headers = headers, timeout = 30)

            if response.status_code != 200:
                print(f"Error HTTP {response.status_code} para {url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            content = soup.find("div", class_="mw-parser-output")
            if content is None:
                print(f"No se ha encontrado el contenido principal en {url}")
                continue

            paragraphs = content.find_all("p")
            text = "\n".join(p.get_text() for p in paragraphs)

            if not text.strip():
                print(f"Texto vacío en {url}")
                continue

            with open(file_path, "w", encoding = "utf-8", errors = "ignore") as f:
                f.write(text)
            
            print(f"{filename} descargado correctamente.")
        
        except Exception as e:
            print(f"Error al descargar {url}: {e}")

def read_txt(filepath):
    with open(filepath, "r", encoding = "utf-8", errors = "ignore") as f:
        return f.read()

def read_pdf(filepath):
    text = ""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error leyendo PDF {filepath}: {e}")
    
    return text

def read_html(filepath):
    try:
        with open(filepath, "r", encoding = "utf-8", errors = "ignore") as f:
            html = f.read()
        
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator = " ")
    except Exception as e:
        print(f"Error leyendo HTML {filepath}: {e}")
        return ""

def load_docs() -> list:
    base_dir = os.path.dirname(__file__)
    docs_path = os.path.abspath(os.path.join(base_dir, "..", "..", "docs"))

    documents = []

    if not os.path.exists(docs_path):
        print(f"Carpeta no encontrada: {docs_path}")
        return documents
    
    doc_id = 0

    for filename in os.listdir(docs_path):
        filepath = os.path.join(docs_path, filename)
        text = ""

        if filename.lower().endswith(".txt"):
            text = read_txt(filepath)
        
        elif filename.lower().endswith(".pdf"):
            text = read_pdf(filepath)
        
        elif filename.lower().endswith(".html") or filename.lower().endswith(".htm"):
            text = read_html(filepath)
        
        else:
            continue

        if text.strip():
            documents.append({
                "id": doc_id,
                "name": filename,
                "text": text
            })
            doc_id += 1
    
    return documents


