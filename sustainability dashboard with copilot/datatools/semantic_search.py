import openai
from utils.db import db
import os
import logging
from bson.objectid import ObjectId

def generate_embedding(text: str) -> list[float]:
    # logging.info('Creating embeddings for text', str(text))
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    resp = openai.Embedding.create(
		input=[text], 
		model="text-embedding-ada-002")
    return resp["data"][0]["embedding"] 

def parse_ObjectID(results):
    for res in results:
        res['_id'] = str(res['_id'])
    return results

def semantic_metricMeta(query):
    logging.info('Querying semantic_metricMeta')
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
                    "embeddings": 0,
                    "score": { '$meta': "searchScore" }
                    }
                }])
    
    results_ = parse_ObjectID(list(results))
    return results_

def filtered_semMeta(query):
    results = semantic_metricMeta(query)
    filtered = []
    keywords = ["not", "non", "without", ]
    for result in results:
        if any(keyword in result['title'] for keyword in keywords):
            print("print: found keyword in title: ", result['title'])
            continue
        else: filtered.append(result)
    return filtered 

def semantic_metricMeta_ids(query):
    logging.info('Querying semantic_metricMeta_ids')
    results = db.metricMeta.aggregate([
                {'$search': {
                    "index": "SemanticSearch",
                    "knnBeta": {
                        "vector": generate_embedding(query),
                        "k": 10,
                        "path": "embeddings"
                        }
                    }
                },
                {"$project": {
                    "_id": 1,
                    "score": { '$meta': "searchScore" }
                    }
                }])
    
    results_ = parse_ObjectID(list(results))
    return results_