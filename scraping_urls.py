import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import hashlib

# Conjuntos globales para evitar duplicados
visited_urls = set()
content_hashes = set()

# Extraer texto limpio, eliminando líneas repetidas
def extraer_texto(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        # Filtrar cadenas cortas
        text = "\n".join([s.strip() for s in soup.stripped_strings if len(s.strip()) > 3])
        # Eliminar líneas duplicadas, preservando orden
        seen = set()
        unique_lines = []
        for line in text.split("\n"):
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)
        clean_text = "\n".join(unique_lines)
        return clean_text
    except Exception as e:
        return f"[ERROR] {e}"

# Procesar página principal con detección de enlaces únicos
def procesar_web(base_url):
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    titulos = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]

    estructura = {}
    nav = soup.find('nav')
    if nav:
        for li in nav.find_all('li', recursive=True):
            enlaces = li.find_all('a')
            if enlaces:
                padre = enlaces[0].get_text(strip=True)
                hijos = [a.get_text(strip=True) for a in enlaces[1:] if a.get_text(strip=True) != padre]
                estructura[padre] = {"submenus": hijos, "url": None}

    links = []
    for a in soup.find_all('a', href=True):
        texto = a.get_text(strip=True)
        href = urljoin(base_url, a['href'])
        if texto and len(texto) > 3 and href not in visited_urls:
            links.append({"texto": texto, "href": href})
            visited_urls.add(href)

    index_links = {item['texto']: item['href'] for item in links}

    estructura_contenido = {}
    for menu, data in estructura.items():
        menu_url = index_links.get(menu)
        contenido_menu = ""
        if menu_url:
            h = hashlib.md5(menu_url.encode()).hexdigest()
            if h not in content_hashes:
                contenido_menu = extraer_texto(menu_url)
                content_hashes.add(h)

        estructura_contenido[menu] = {
            "url": menu_url,
            "contenido": contenido_menu,
            "submenus": {}
        }

        for submenu in data["submenus"]:
            submenu_url = index_links.get(submenu)
            contenido_submenu = ""
            if submenu_url:
                h2 = hashlib.md5(submenu_url.encode()).hexdigest()
                if h2 not in content_hashes:
                    contenido_submenu = extraer_texto(submenu_url)
                    content_hashes.add(h2)
            estructura_contenido[menu]["submenus"][submenu] = {
                "url": submenu_url,
                "contenido": contenido_submenu
            }

    return {"titulos": titulos, "estructura": estructura_contenido}

# Interfaz Streamlit (igual que antes)
st.set_page_config(page_title="Scraper Jerárquico mejorado", layout="centered")
st.title("🌐 Scraper con Deduplicación")
st.markdown("Ahora evita URLs y líneas repetidas.")

url_input = st.text_input("🔗 Ingresa la URL principal")
if st.button("🚀 Procesar"):
    if url_input:
        with st.spinner("Analizando..."):
            resultado = procesar_web(url_input)
            st.success("✅ Listo.")
            st.subheader("📋 Títulos")
            st.write(resultado["titulos"])
            st.subheader("📂 Estructura")
            st.json(resultado["estructura"])
            json_str = json.dumps(resultado, ensure_ascii=False, indent=2)
            st.download_button("📥 Descargar JSON", json_str, "estructura_web.json", "application/json")
    else:
        st.warning("Por favor ingresa una URL válida.")
