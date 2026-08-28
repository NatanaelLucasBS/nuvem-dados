import streamlit as st
import os

from core.nlp_processor import NLPProcessor
from engines.bs4_engine import BS4Engine
from engines.scrapy_engine import ScrapyEngine
from core.text_processor import TextProcessor

class AppUI:
    """
    Interface principal do Data App: orquestra as chamadas dos motores,
    gerencia inputs do usuario e renderiza paineis de metricas e visualizacao.
    """
    
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
            
            # Painel com as 3 metricas requeridas
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric(label="Tempo de Execução", value=f"{exec_time:.4f} s")
            with col_m2:
                st.metric(label=f"Ocorrências de '{search_word}'", value=freq)
            with col_m3:
                st.metric(label="Páginas Processadas", value=f"{count}/5")
            
            st.markdown("### Nuvem de Palavras Formatada")
            if clean_text.strip():
                fig = TextProcessor.generate_wordcloud(clean_text, colormap=colormap, mask_path='assets/images/homem_aranha.png')
                st.pyplot(fig)
            else:
                st.warning("O texto extraído e limpo está vazio. Não foi possível gerar a nuvem de palavras.")

    def run(self):
        st.set_page_config(page_title="Data Scraper Pro", layout="wide")
        
        col_img, col_title = st.columns([1, 4])
        with col_img:
            if os.path.exists("assets/images/spiderlogo.png"):
                st.image("assets/images/spiderlogo.png", width=120)
            else:
                st.info("assets/images/spiderlogo.png não encontrado no diretório.")
                
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
        st.write("Escolha um dos métodos abaixo para extrair os textos e gerar a nuvem de palavras.")
        
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
