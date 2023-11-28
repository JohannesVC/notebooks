import openai
from utils.db import db
import os
import logging

def metricMeta(query):
    items = list(db.metricMeta.find({'title': {'$regex': query, '$options': 'i'}}))
    return items

def generate_embedding(text: str) -> list[float]:
    # logging.info('Creating embeddings for text', str(text))
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    resp = openai.Embedding.create(
		input=[text], 
		model="text-embedding-ada-002")
    return resp["data"][0]["embedding"] 

def semantic_metricMeta(query):
    logging.info('Querying vectordb')
    results = db.metricMeta.aggregate([
                {'$search': {
                    "index": "SemanticSearch",
                    "knnBeta": {
                        "vector": generate_embedding(query),
                        "k": 3,
                        "path": "embeddings"
                        }
                    }
                },
                {"$project": {
                    "_id": 0,
                    "title": 1,
                    "description": 1,
                    'type': 1,
                    'measure': 1,
                    'framework': 1,
                    'category': 1,
                    "score": { '$meta': "searchScore" }
                    }
                }])
    return list(results)

def filtered_semantic_metricMeta(query):
    # logging.info('Filtering semantic results for', str(query))
    results = semantic_metricMeta(query)
    filtered = []
    keywords = ["not", "non", "without", ]
    for result in results:
        if any(keyword in result['title'] for keyword in keywords):
            print("print: found keyword in title: ", result['title'])
            continue
        else: filtered.append(result)
    return filtered