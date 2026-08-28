# Plataforma de Inteligencia Web

Este projeto e uma aplicacao de dados que tem como objetivo processar textos de paginas da Wikipedia baseadas em termos de busca fornecidos pelo usuario e gerar uma nuvem de palavras. O sistema permite realizar testes comparativos de desempenho utilizando duas solucoes de web scraping:
1. Requests e BeautifulSoup (sincrono).
2. Scrapy (assincrono).

Os textos extraidos passam por um processo de limpeza, remocao de stopwords e sao consolidados em uma visualizacao de Nuvem de Palavras com uma mascara customizada. O projeto tambem permite buscar a frequencia de uma palavra-chave no texto final.

## Como rodar a aplicacao

Siga as instrucoes abaixo para executar o projeto localmente.

### 1. Pre-requisitos
Certifique-se de ter o Python instalado na sua maquina. E recomendado o uso de um ambiente virtual (venv).

### 2. Instalacao das dependencias
Abra o terminal na pasta raiz do projeto e instale as bibliotecas necessarias executando:
```bash
pip install -r requirements.txt
```

### 3. Imagens
Para o funcionamento correto da interface e da nuvem de palavras, certifique-se de que as seguintes imagens existam dentro da pasta `assets/images/`:
- `spiderlogo.png`: Logotipo exibido no topo da interface.
- `homem_aranha.png`: Mascara utilizada para moldar a nuvem de palavras.

### 4. Execucao
Para iniciar o servidor local da aplicacao, utilize o comando:
```bash
python -m streamlit run app.py
```

A aplicacao estara disponivel em `http://localhost:8501`. Na interface, digite 5 termos separados por virgula e a palavra-chave, em seguida clique no motor de sua escolha para iniciar a extracao.
