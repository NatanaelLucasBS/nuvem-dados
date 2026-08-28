import re
import nltk
from nltk.corpus import stopwords

class NLPProcessor:

    
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
