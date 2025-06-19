import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ---------------------------------------
# 1. Extraer enlaces internos
# ---------------------------------------
def extract_all_internal_links(base_url):
    seen = set()
    try:
        resp = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")
        base_domain = urlparse(base_url).netloc

        for a in soup.find_all('a', href=True):
            href = a['href'].strip().split('#')[0]
            full_url = urljoin(base_url, href)
            if base_domain in full_url and full_url not in seen:
                seen.add(full_url)
    except Exception as e:
        st.error(f"❌ Error extrayendo enlaces: {e}")
    return sorted(seen)

# ---------------------------------------
# 2. Extraer texto estructurado
# ---------------------------------------
def extraer_texto_estructurado(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        # Eliminar menú, script, estilo, footer, etc.
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()
        for tag in soup.select("header, footer, nav, .menu, .navbar, .main-nav, .footer"):
            tag.decompose()

        contenido = ""
        secciones = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li'])
        for tag in secciones:
            nombre_tag = tag.name.lower()
            texto = tag.get_text(strip=True)
            if not texto:
                continue
            if nombre_tag == 'h1':
                contenido += f"\n\n# {texto}\n"
            elif nombre_tag == 'h2':
                contenido += f"\n\n## {texto}\n"
            elif nombre_tag == 'h3':
                contenido += f"\n\n### {texto}\n"
            elif nombre_tag == 'h4':
                contenido += f"\n\n#### {texto}\n"
            elif nombre_tag == 'li':
                contenido += f"- {texto}\n"
            else:
                contenido += f"{texto}\n"
        return contenido.strip()
    except Exception as e:
        return f"❌ Error procesando [{url}]: {e}"

# ---------------------------------------
# 3. Interfaz Streamlit
# ---------------------------------------
st.set_page_config(page_title="🌐 Web Scraper Estructurado", layout="centered")
st.title("🧭 Extractor y Organizador Web")

url_input = st.text_input("🔗 Ingresa la URL del sitio", "https://www.sitesbarranquilla.com/es/")

if st.button("🌟 Ejecutar todo"):
    st.info("🔍 Extrayendo enlaces internos y procesando cada contenido…")

    enlaces = extract_all_internal_links(url_input)
    if not enlaces:
        st.warning("⚠️ No se encontraron enlaces internos.")
    else:
        st.success(f"✅ {len(enlaces)} enlaces encontrados.")

        for i, link in enumerate(enlaces, start=1):
            st.markdown("---")
            st.markdown(f"## {i}. 🔗 [{link}]({link})")
            texto = extraer_texto_estructurado(link)
            st.markdown(texto)

        st.markdown("---")
        st.success("👏 Proceso completado.")
