from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder():
    
    def __init__(self, model_type="medium"):
        """
        model = "medium"|"large"
        """
        model_name = {
            "medium": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
            "large": "intfloat/multilingual-e5-base"
                      }[model_type]
        
        self.model = SentenceTransformer(model_name)


    def text_to_vector(self, text: str):
        """
        Преобразует текст в вектор (массив чисел)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    

if __name__=="__main__":
    #Пример использования
    test = Embedder(model_type="medium")
    A = test.text_to_vector("Металл")
    B = test.text_to_vector("Metal")
    print(f"cos = {np.dot(A, B)/(np.linalg.norm(A) * np.linalg.norm(B))}")
    # cos = 0.9493443369865417 - одинаковые