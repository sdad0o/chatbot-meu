import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_FILE = r"scrap website data/meu_data.json"
CHUNKS = []

def load_data():
    global CHUNKS
    print("Loading data...")
    if not os.path.exists(DATA_FILE):
        print("Data file not found!")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 5. Bachelor Programs (The bulk of the data)
    bachelor_names = []
    if "ebooklet" in data and "bachelor_programs" in data["ebooklet"]:
        for prog in data["ebooklet"]["bachelor_programs"]:
            name = prog.get("name_ar", "Unknown Program")
            eng_name = prog.get("id", "") 
            bachelor_names.append(f"{name} ({eng_name})")
            
            # Pricing
            price_jod = prog.get("credit_hour_price_jod", "N/A")
            price_usd = prog.get("credit_hour_price_usd", "N/A")
            
            # Faculty
            faculty_ar = prog.get("faculty_ar", "")
            faculty_en = prog.get("faculty", "")
            
            # Requirements (summarized)
            reqs = ""
            if "admission_requirements_parsed" in prog:
                reqs = " ".join(prog["admission_requirements_parsed"])
            
            # Construct chunk
            chunk = (
                f"Program (تخصص): {name} ({eng_name}). "
                f"Faculty (الكلية): {faculty_ar} ({faculty_en}). "
                f"Type: Bachelor (بكالوريوس). "
                f"Price per credit hour (سعر الساعة): {price_jod} JOD / {price_usd} USD. "
                f"Admission Requirements (شروط القبول): {reqs}"
            )
            CHUNKS.append(chunk)

    print(f"Data loaded. {len(CHUNKS)} chunks created.")

def cosine_similarity(v1, v2):
    dot_product = sum(a*b for a, b in zip(v1, v2))
    magnitude_v1 = sum(a*a for a in v1) ** 0.5
    magnitude_v2 = sum(b*b for b in v2) ** 0.5
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    return dot_product / (magnitude_v1 * magnitude_v2)

def debug_retrieval(query):
    print(f"\nQuery: {query}")
    
    # Embed chunks
    print("Embedding chunks...")
    response = client.embeddings.create(input=CHUNKS, model="text-embedding-3-small")
    chunk_embeddings = [data.embedding for data in response.data]
    
    # Embed query
    print("Embedding query...")
    query_response = client.embeddings.create(input=query, model="text-embedding-3-small")
    query_embedding = query_response.data[0].embedding
    
    scored_chunks = []
    for i, chunk_embedding in enumerate(chunk_embeddings):
        score = cosine_similarity(query_embedding, chunk_embedding)
        scored_chunks.append((score, CHUNKS[i]))
        
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    print("\nTop 5 Matches:")
    for i, (score, chunk) in enumerate(scored_chunks[:5]):
        print(f"{i+1}. Score: {score:.4f} | Chunk: ...{chunk[50:150]}...")

load_data()
debug_retrieval("ما تخصصات كلية تكنولوجيا المعلومات")
