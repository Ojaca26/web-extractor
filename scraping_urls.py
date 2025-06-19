import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_all_internal_links(base_url):
    seen = set()
    try:
        resp = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")
        base_domain = urlparse(base_url).netloc

        for a in soup.find_all('a', href=True):
            href = a['href'].strip().split('#')[0]
            if not href:
                continue
            full_url = urljoin(base_url, href)
            if base_domain in full_url and full_url not in seen:
                seen.add(full_url)
    except Exception as e:
        st.error(f"❌ Error al procesar la URL: {e}")
    return sorted(seen)

# Interfaz Streamlit
st.set_page_config(page_title="Extractor de Enlaces", layout="centered")
st.title("🧭 Explorador de Enlaces")

url_input = st.text_input("🔗 Ingresa la URL del sitio", "https://uc.edu.co/")

if st.button("Extraer enlaces"):
    st.info("🔍 Explorando el sitio...")
    links = extract_all_internal_links(url_input.strip())

    if links:
        st.success(f"✅ {len(links)} enlaces encontrados:")
        st.code("\n".join(links), language="text")
    else:
        st.warning("⚠️ No se encontraron enlaces en esa página.")
