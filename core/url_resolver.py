import requests

class WikiURLResolver:

    
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
