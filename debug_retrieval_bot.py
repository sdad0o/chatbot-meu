
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mocking the content loading part to see what chunks look like EXACTLY
DATA_FILE = r"scrap website data/meu_data.json"
CHUNKS = []

def load_data():
    global CHUNKS
    print("Loading data...")
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found at {DATA_FILE}")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "about" in data:
        about = data["about"]
        
        # Board of Trustees
        if "board_of_trustees" in about:
            bot = about["board_of_trustees"]
            members = ", ".join(bot.get("members", []))
            chunk_text = f"Board of Trustees Chairman (رئيس مجلس الأمناء): {bot.get('chairman', 'Unknown')}. Members: {members}"
            CHUNKS.append(chunk_text)
            print(f"DEBUG: Trustees Chunk: {chunk_text[:100]}...")

        # Council of Deans
        if "council_of_deans" in about:
             members = ", ".join(about["council_of_deans"].get("members", []))
             chunk_text = f"Council of Deans (مجلس العمداء): {members}"
             CHUNKS.append(chunk_text)
             # print(f"DEBUG: Deans Chunk: {chunk_text[:100]}...")

    print(f"Data loaded. {len(CHUNKS)} relevant chunks for this test.")

def test_retrieval():
    if not CHUNKS:
        return

    print("Generating embeddings...")
    response = client.embeddings.create(input=CHUNKS, model="text-embedding-3-small")
    embeddings = [data.embedding for data in response.data]

    query = "من هم اعضاء مجلس الامناء"
    print(f"Query: {query}")
    
    q_response = client.embeddings.create(input=query, model="text-embedding-3-small")
    q_embedding = q_response.data[0].embedding
    
    scores = []
    for i, emb in enumerate(embeddings):
        dot = sum(a*b for a, b in zip(q_embedding, emb)) # Simplified cosine if normalized
        # But let's use the same func as app.py roughly or just dot
        # OpenAI embeddings are normalized so dot product is cosine similarity
        scores.append((dot, CHUNKS[i]))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    
    print("\n--- Top Matches ---")
    for score, text in scores:
        print(f"{score:.4f} -> {text[:100]}...")

if __name__ == "__main__":
    load_data()
    test_retrieval()
