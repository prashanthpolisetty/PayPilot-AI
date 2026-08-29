import math
import re
from typing import List, Dict, Any

class VectorCatalogService:
    @staticmethod
    def _get_text_embedding(text: str) -> Dict[str, int]:
        """Simple lightweight TF-IDF word frequency embedding for local vector similarity."""
        words = re.findall(r'\w+', text.lower())
        vec = {}
        for w in words:
            if len(w) > 2:
                vec[w] = vec.get(w, 0) + 1
        return vec

    @staticmethod
    def cosine_similarity(vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        """Calculates cosine similarity between two word frequency vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    @classmethod
    def rank_products_by_similarity(cls, query: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks products by semantic vector similarity to user query."""
        query_vec = cls._get_text_embedding(query)
        if not query_vec:
            return products

        scored_products = []
        for prod in products:
            prod_text = f"{prod.get('name', '')} {prod.get('category', '')} {prod.get('description', '')} {str(prod.get('attributes_json', ''))}"
            prod_vec = cls._get_text_embedding(prod_text)
            sim = cls.cosine_similarity(query_vec, prod_vec)
            prod_copy = dict(prod)
            prod_copy["similarity_score"] = round(sim, 3)
            scored_products.append((sim, prod_copy))

        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_products]
