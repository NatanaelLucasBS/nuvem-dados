import time
import scrapy
from scrapy.crawler import CrawlerRunner
from crochet import setup, wait_for

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
            # Forca o reactor compativel instalado pelo Crochet
            'TWISTED_REACTOR': 'twisted.internet.epollreactor.EPollReactor'
        }
        
        # Em Windows, o EPollReactor não funciona, precisamos contornar isso se não estivermos no Linux
        import sys
        if sys.platform == 'win32':
            settings['TWISTED_REACTOR'] = 'twisted.internet.selectreactor.SelectReactor'

        runner = CrawlerRunner(settings)
        return runner.crawl(WikiSpider, start_urls=urls)
        
    def extract(self, terms):
        global SCRAPY_RESULTS
        SCRAPY_RESULTS = [] # Limpeza de cache de execucoes anteriores
        
        start_time = time.time()
        valid_urls = []
        valid_count = 0
        failed_terms = []
        
        # Validacao previa das URLs para evitar timeouts no crawler
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
