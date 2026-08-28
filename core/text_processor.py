import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud

class TextProcessor:

    
    @staticmethod
    def generate_wordcloud(text, colormap='viridis', mask_path='assets/images/homem_aranha.png'):
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
