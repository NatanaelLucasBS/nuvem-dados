# Script para Google Colab

Você pode copiar os blocos de código abaixo e colá-los sequencialmente no seu Google Colab. Eles já incluem o comando mágico `%%writefile` para gerar os arquivos diretamente no ambiente do Colab antes de rodar o Streamlit.

### 1. Instalação de Dependências
```python
!pip install streamlit requests beautifulsoup4 scrapy crochet wordcloud matplotlib nltk pillow numpy
```

### 2. url_resolver.py
```python
%%writefile url_resolver.py
import requests

class WikiURLResolver:
    """
    Resolve URLs da Wikipedia aplicando headers de navegacao real para evitar
    bloqueios (403/404) e heuristicas de correcao de caixa para URLs quebradas.
    """
    
    @staticmethod
    def get_valid_content(term):
        base_url = "https://pt.wikipedia.org/wiki/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        term_clean = term.strip()
        tentativas = [
            term_clean.replace(" ", "_"),
            term_clean.capitalize().replace(" ", "_"),
            term_clean.title().replace(" ", "_")
        ]
        
        for fmt in tentativas:
            url = f"{base_url}{fmt}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return url, response.text
            except requests.RequestException:
                continue
                
        return None, None
```

### 3. nlp_processor.py
```python
%%writefile nlp_processor.py
import re
import nltk
from nltk.corpus import stopwords

class NLPProcessor:
    """
    Processamento de linguagem natural: limpeza por regex, filtragem de stopwords
    e analise de frequencia de termos.
    """
    
    def __init__(self):
        nltk.download('stopwords', quiet=True)
        self.stopwords_pt = set(stopwords.words('portuguese'))
        
    def clean_text(self, text):
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', text)
        
        words = text.lower().split()
        clean_words = [w for w in words if w not in self.stopwords_pt and len(w) > 2]
        return " ".join(clean_words)
        
    def count_frequency(self, clean_text, target_word):
        if not target_word:
            return 0
        return clean_text.split().count(target_word.lower().strip())
```

### 4. text_processor.py
```python
%%writefile text_processor.py
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud

class TextProcessor:
    """
    Renderizacao visual: constroi a WordCloud aplicando mascaras vetoriais
    ou matriciais baseadas em imagem PNG.
    """
    
    @staticmethod
    def generate_wordcloud(text, colormap='viridis', mask_path='homem_aranha.png'):
        mask_array = None
        
        if os.path.exists(mask_path):
            img = Image.open(mask_path)
            
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')
                img_array = np.array(img)
                alpha = img_array[:, :, 3]
                mask_array = np.where(alpha < 128, 255, 0).astype(np.uint8)
            else:
                img = img.convert('L')
                mask_array = np.array(img)
                mask_array = np.where(mask_array > 200, 255, 0).astype(np.uint8)

        if mask_array is not None and len(np.unique(mask_array)) > 1:
            wc = WordCloud(
                width=800, 
                height=800, 
                background_color='white', 
                colormap=colormap,
                mask=mask_array,
                contour_width=1,
                contour_color='red'
            ).generate(text)
        else:
            wc = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                colormap=colormap
            ).generate(text)

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        return fig
```

### 5. bs4_engine.py
```python
%%writefile bs4_engine.py
import time
from bs4 import BeautifulSoup
from url_resolver import WikiURLResolver

class BS4Engine:
    """
    Motor sincrono: utiliza Requests para envio HTTP sequencial e BeautifulSoup
    para parsing de DOM nas tags <p>.
    """
    
    def extract(self, terms):
        start_time = time.time()
        combined_text = ""
        valid_count = 0
        failed_terms = []
        
        for term in terms:
            url, html = WikiURLResolver.get_valid_content(term)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for p in soup.find_all('p'):
                    combined_text += p.get_text() + " "
                valid_count += 1
            else:
                failed_terms.append(term)
                
        exec_time = time.time() - start_time
        return combined_text, exec_time, valid_count, failed_terms
```

### 6. scrapy_engine.py
```python
%%writefile scrapy_engine.py
import time
import scrapy
from scrapy.crawler import CrawlerRunner
from crochet import setup, wait_for
from url_resolver import WikiURLResolver

setup()

SCRAPY_RESULTS = []

class WikiSpider(scrapy.Spider):
    name = "wiki_spider"
    
    def parse(self, response):
        paragraphs = response.css('p::text').getall()
        SCRAPY_RESULTS.append(" ".join(paragraphs))

class ScrapyEngine:
    
    @wait_for(timeout=60)
    def _run_spider(self, urls):
        settings = {
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'LOG_LEVEL': 'ERROR',
            'ROBOTSTXT_OBEY': False,
            'TWISTED_REACTOR': 'twisted.internet.epollreactor.EPollReactor'
        }
        
        import sys
        if sys.platform == 'win32':
            settings['TWISTED_REACTOR'] = 'twisted.internet.selectreactor.SelectReactor'

        runner = CrawlerRunner(settings)
        return runner.crawl(WikiSpider, start_urls=urls)
        
    def extract(self, terms):
        global SCRAPY_RESULTS
        SCRAPY_RESULTS = []
        
        start_time = time.time()
        valid_urls = []
        valid_count = 0
        failed_terms = []
        
        for term in terms:
            url, _ = WikiURLResolver.get_valid_content(term)
            if url:
                valid_urls.append(url)
                valid_count += 1
            else:
                failed_terms.append(term)
                
        if valid_urls:
            self._run_spider(valid_urls)
            
        exec_time = time.time() - start_time
        return " ".join(SCRAPY_RESULTS), exec_time, valid_count, failed_terms
```

### 7. app.py
```python
%%writefile app.py
import streamlit as st
import os

from nlp_processor import NLPProcessor
from bs4_engine import BS4Engine
from scrapy_engine import ScrapyEngine
from text_processor import TextProcessor

class AppUI:
    
    def __init__(self):
        self.nlp = NLPProcessor()
        self.bs4 = BS4Engine()
        self.scrapy = ScrapyEngine()

    def render_results(self, raw_text, exec_time, count, fails, search_word, colormap, engine_name):
        for fail in fails:
            st.error(f"Erro de resolucao para o termo '{fail}'. Pagina não localizada (404/Erro).")
            
        if count > 0:
            clean_text = self.nlp.clean_text(raw_text)
            freq = self.nlp.count_frequency(clean_text, search_word)
            
            st.markdown(f"### Resultados da Execução ({engine_name})")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric(label="Tempo de Execução", value=f"{exec_time:.4f} s")
            with col_m2:
                st.metric(label=f"Ocorrências de '{search_word}'", value=freq)
            with col_m3:
                st.metric(label="Páginas Processadas", value=f"{count}/5")
            
            st.markdown("### Nuvem de Palavras Formatada")
            if clean_text.strip():
                fig = TextProcessor.generate_wordcloud(clean_text, colormap=colormap, mask_path='homem_aranha.png')
                st.pyplot(fig)
            else:
                st.warning("O texto extraído e limpo está vazio. Não foi possível gerar a nuvem de palavras.")

    def run(self):
        st.set_page_config(page_title="Data Scraper Pro", layout="wide")
        
        col_img, col_title = st.columns([1, 4])
        with col_img:
            if os.path.exists("homem_aranha.png"):
                st.image("homem_aranha.png", width=120)
            else:
                st.info("homem_aranha.png não encontrado no diretório. A máscara não será aplicada.")
                
        with col_title:
            st.title("Plataforma de Inteligência Web")
            st.markdown("Extração e análise comparativa de dados da Wikipedia. (Data App)")

        st.markdown("---")
        
        st.write("Digite 5 termos separados por vírgula para processar. Exemplo do professor:")
        st.code("Universidade Federal do Rio Grande do Norte, Ciência de Dados, Aprendizado de Máquina, Engenharia de Software, Armazém de Dados")
        
        terms_input = st.text_input(
            "Insira exatamente 5 termos separados por vírgula:", 
            placeholder="Ex: Startups, Inteligência Artificial, Banco de Dados, Investimento anjo, Python"
        )
        search_word = st.text_input("Palavra-chave para busca de frequência no texto extraído:", placeholder="Ex: dados")
        
        terms = [t.strip() for t in terms_input.split(',')] if terms_input else []
        is_valid = len(terms) == 5 and search_word != ""

        st.markdown("### Testes de Motores de Extração")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Teste 1: Requests + BeautifulSoup", use_container_width=True):
                if not is_valid:
                    st.warning("Verifique os campos: é obrigatório inserir 5 termos separados por vírgula e 1 palavra-chave.")
                else:
                    with st.spinner("Processando via requisições síncronas (BS4)..."):
                        raw, tempo, count, fails = self.bs4.extract(terms)
                        self.render_results(raw, tempo, count, fails, search_word, 'viridis', 'Requests + BeautifulSoup')

        with col2:
            if st.button("Teste 2: Scrapy Assíncrono", use_container_width=True):
                if not is_valid:
                    st.warning("Verifique os campos: é obrigatório inserir 5 termos separados por vírgula e 1 palavra-chave.")
                else:
                    with st.spinner("Processando via motor assíncrono (Scrapy)..."):
                        raw, tempo, count, fails = self.scrapy.extract(terms)
                        self.render_results(raw, tempo, count, fails, search_word, 'plasma', 'Scrapy')

if __name__ == "__main__":
    app = AppUI()
    app.run()
```

### 8. Subir Imagem (Importante)
No Colab, faça o upload manual do arquivo `homem_aranha.png` para a raiz do seu ambiente (no painel de arquivos lateral esquerdo) para que ele seja usado como máscara da nuvem de palavras.

### 9. Execução do Servidor Streamlit (Cloudflare)
```bash
!pkill -f streamlit
!pkill -f cloudflared
!wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
!chmod +x cloudflared-linux-amd64
!nohup streamlit run app.py --server.headless true > logs.txt 2>&1 &
!sleep 3
!nohup ./cloudflared-linux-amd64 tunnel --url http://localhost:8501 > tunnel.log 2>&1 &
!sleep 8
!echo "=== LINK DE ACESSO ==="
!grep -o 'https://.*\.trycloudflare.com' tunnel.log
```
