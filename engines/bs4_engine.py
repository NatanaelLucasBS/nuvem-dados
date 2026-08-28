import time
from bs4 import BeautifulSoup
from core.url_resolver import WikiURLResolver

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
                # Coleta apenas conteudo de paragrafos principais
                for p in soup.find_all('p'):
                    combined_text += p.get_text() + " "
                valid_count += 1
            else:
                failed_terms.append(term)
                
        exec_time = time.time() - start_time
        return combined_text, exec_time, valid_count, failed_terms
