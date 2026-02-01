from flask import Flask, request, jsonify, send_from_directory
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Use absolute path based on script location for IIS compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "scrap website data", "meu_data.json")
CHUNKS = []

def load_data():
    """Loads JSON and creates text chunks for retrieval."""
    global CHUNKS
    print("Loading data...")
    if not os.path.exists(DATA_FILE):
        print("Data file not found!")
        return

    expected_path = os.path.join(os.getcwd(), DATA_FILE)
    if not os.path.exists(expected_path):
         # Try absolute path from previous context if relative fails
         expected_path = r"e:\Projects\chatBot v.3\scrap website data\meu_data.json"

    with open(expected_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Chunking Strategy
    
    # 1. Admin/About Info
    if "about" in data:
        about = data["about"]
        # President
        if "president_message" in about:
            pm = about["president_message"]
            text = f"University President (رئيس الجامعة): {pm.get('president_name', 'Unknown')}. Message: {pm.get('message', '')}"
            CHUNKS.append(text)
        
        # Board of Trustees
        if "board_of_trustees" in about:
            bot = about["board_of_trustees"]
            members = ", ".join(bot.get("members", []))
            CHUNKS.append(f"Board of Trustees Chairman (رئيس مجلس الأمناء): {bot.get('chairman', 'Unknown')}. Members: {members}")

        # Board of Directors
        if "board_of_directors" in about:
            bod = about["board_of_directors"]
            members = ", ".join(bod.get("members", []))
            CHUNKS.append(f"Board of Directors Chairman (رئيس هيئة المديرين): {bod.get('chairman', 'Unknown')}. Members: {members}")

        # Deans
        if "council_of_deans" in about:
             members = ", ".join(about["council_of_deans"].get("members", []))
             CHUNKS.append(f"The Council of Deans (مجلس العمداء) members are: {members}")

        # Contact Info
        if "contact" in data:
            contact = data["contact"]
            phones = contact.get("phone", {})
            addr = contact.get("address", {})
            
            phone_str = f"Landline: {phones.get('landline')}, Mobile/WhatsApp: {phones.get('mobile')}"
            addr_str = f"{addr.get('ar')} ({addr.get('en')})"
            email = contact.get("email")
            work_hours = contact.get("working_hours")
            
            contact_chunk = (
                f"University Contact Information (معلومات التواصل): "
                f"Phone Numbers (أرقام الهواتف): {phone_str}. "
                f"Address (العنوان): {addr_str}. "
                f"Email (البريد الإلكتروني): {email}. "
                f"Working Hours (ساعات الدوام): {work_hours}."
            )
            CHUNKS.append(contact_chunk)

    # 2. Key Figures
    if "key_figures" in data:
        for role, name in data["key_figures"].items():
            CHUNKS.append(f"Key Figure - {role.replace('_', ' ').title()}: {name}")

    # 3. Admission
    if "admission" in data:
        adm = data["admission"]
        if "master_procedures" in adm:
            mp = adm["master_procedures"]
            steps = " ".join(mp.get("steps", []))
            reqs = " ".join(mp.get("requirements", []))
            # keywords: admission, master, قبول, ماجستير, تسجيل
            CHUNKS.append(f"Master's Degree Admission Procedures (إجراءات قبول الماجستير): {steps}. Requirements: {reqs}")

    # 4. International Programs
    if "uk_degrees" in data:
        uk = data["uk_degrees"]
        progs = ", ".join(uk.get("programs", []))
        # keywords: international, uk, programs, برامج, دولية, بريطانية
        CHUNKS.append(f"International Programs / UK Degrees / Hosted Programs (البرامج الدولية): {progs}. {uk.get('description', '')}")

    # 5. Bachelor Programs (The bulk of the data)
    bachelor_names = []
    faculty_map = {} # Map faculty_name -> list of majors

    if "ebooklet" in data and "bachelor_programs" in data["ebooklet"]:
        for prog in data["ebooklet"]["bachelor_programs"]:
            name = prog.get("name_ar", "Unknown Program")
            eng_name = prog.get("id", "") 
            bachelor_names.append(f"{name} ({eng_name})")
            
            # Pricing
            price_jod = prog.get("credit_hour_price_jod", "N/A")
            price_usd = prog.get("credit_hour_price_usd", "N/A")
            
            # Faculty
            faculty_ar = prog.get("faculty_ar", "General")
            faculty_en = prog.get("faculty", "General")
            
            # Add to faculty map for summary chunks
            if faculty_ar not in faculty_map:
                faculty_map[faculty_ar] = {"en": faculty_en, "majors": []}
            faculty_map[faculty_ar]["majors"].append(f"{name}")

            # Requirements (summarized)
            reqs = ""
            if "admission_requirements_parsed" in prog:
                reqs = " ".join(prog["admission_requirements_parsed"])
            
            # Fees (General)
            fees_list = prog.get("fees", [])
            fees_text = ""
            if fees_list:
                # Join and clean newlines
                fees_text = " | ".join([f.replace("\n", " ") for f in fees_list])

            # Construct chunk
            chunk = (
                f"Program (تخصص): {name} ({eng_name}). "
                f"Faculty (الكلية): {faculty_ar} ({faculty_en}). "
                f"Type: Bachelor (بكالوريوس). "
                f"Price per credit hour (سعر الساعة): {price_jod} JOD / {price_usd} USD. "
                f"Additional Fees (رسوم إضافية): {fees_text}. "
                f"Admission Requirements (شروط القبول): {reqs}"
            )
            CHUNKS.append(chunk)

        # Create Faculty Summary Chunks
        for f_ar, data_obj in faculty_map.items():
            f_en = data_obj["en"]
            majors_list = ", ".join(data_obj["majors"])
            # This chunk is specifically designed to answer "What majors are in X?"
            summary = (
                f"Faculty (الكلية): {f_ar} ({f_en}). "
                f"List of Majors/Programs (قائمة التخصصات): {majors_list}. "
                f"Degrees offered: Bachelor (بكالوريوس)."
            )
            CHUNKS.append(summary)
            
        # Add Bachelor Summary Chunk (Aggregate all names)
        if bachelor_names:
            full_list = ", ".join(bachelor_names)
            CHUNKS.append(f"List of all Bachelor Programs (تخصصات البكالوريوس المتاحة): {full_list}")

    # 6. Master Programs
    master_names = []
    if "ebooklet" in data and "master_programs" in data["ebooklet"]:
        for prog in data["ebooklet"]["master_programs"]:
            name = prog.get("name_ar", "Unknown Program")
            eng_name = prog.get("id", "")
            master_names.append(f"{name} ({eng_name})")
            
            # Pricing
            price_jod = prog.get("credit_hour_price_jod", "N/A")
            price_usd = prog.get("credit_hour_price_usd", "N/A")
            
            # Requirements
            reqs = ""
            if "admission_requirements_parsed" in prog:
                reqs = " ".join(prog["admission_requirements_parsed"])
            
            # Fees (General)
            fees_list = prog.get("fees", [])
            fees_text = ""
            if fees_list:
                fees_text = " | ".join([f.replace("\n", " ") for f in fees_list])

            # Construct chunk
            chunk = (
                f"Program (تخصص): {name} ({eng_name}). "
                f"Type: Master (ماجستير). "
                f"Price per credit hour (سعر الساعة): {price_jod} JOD / {price_usd} USD. "
                f"Additional Fees (رسوم إضافية): {fees_text}. "
                f"Admission Requirements (شروط القبول): {reqs}"
            )
            CHUNKS.append(chunk)

        # Add Master Summary Chunk
        if master_names:
            full_list = ", ".join(master_names)
            CHUNKS.append(f"List of all Master Programs (تخصصات الماجستير المتاحة): {full_list}")

    # 7. Diploma Programs
    diploma_names = []
    if "ebooklet" in data and "diploma_programs" in data["ebooklet"]:
        for prog in data["ebooklet"]["diploma_programs"]:
            name = prog.get("name_ar", "Unknown Program")
            eng_name = prog.get("id", "")
            diploma_names.append(f"{name} ({eng_name})")
            
            price_jod = prog.get("credit_hour_price_jod", "N/A")
            price_usd = prog.get("credit_hour_price_usd", "N/A")
            
            reqs = ""
            if "admission_requirements_parsed" in prog:
                reqs = " ".join(prog["admission_requirements_parsed"])
            
            # Fees (General)
            fees_list = prog.get("fees", [])
            fees_text = ""
            if fees_list:
                fees_text = " | ".join([f.replace("\n", " ") for f in fees_list])
            
            chunk = (
                f"Program (تخصص): {name} ({eng_name}). "
                f"Type: Diploma (دبلوم). "
                f"Price per credit hour (سعر الساعة): {price_jod} JOD / {price_usd} USD. "
                f"Additional Fees (رسوم إضافية): {fees_text}. "
                f"Admission Requirements (شروط القبول): {reqs}"
            )
            CHUNKS.append(chunk)
            
        # Add Diploma Summary Chunk
        if diploma_names:
            full_list = ", ".join(diploma_names)
            CHUNKS.append(f"List of all Diploma Programs (تخصصات الدبلوم المتاحة): {full_list}")

    # 8. Developer Info (Hardcoded)
    dev_info = "تم تطويري من قبل دائرة تكنولوجيا المعلومات في جامعة الشرق الاوسط. I was developed by the IT Department at Middle East University."
    CHUNKS.append(f"Question: Who made you? Who developed you? من صنعك؟ Answer: {dev_info}")

    print(f"Data loaded. {len(CHUNKS)} chunks created.")

def initialize_knowledge_base():
    """Initializes the knowledge base if not already loaded."""
    global CHUNKS, CHUNK_EMBEDDINGS
    if CHUNKS: 
        return
        
    print("Initializing knowledge base...")
    load_data()
    generate_embeddings()

CHUNK_EMBEDDINGS = []

def generate_embeddings():
    """Generates embeddings for all chunks."""
    global CHUNK_EMBEDDINGS
    print("Generating embeddings for knowledge base...")
    try:
        # Batch processing would be better for many chunks, but for ~50 loop is okay or small batches
        # Let's do a simple loop for clarity and error handling per chunk, or one big batch if small.
        # OpenAI handles list of strings.
        if not CHUNKS:
            return
            
        response = client.embeddings.create(input=CHUNKS, model="text-embedding-3-small")
        # Ensure order is preserved
        CHUNK_EMBEDDINGS = [data.embedding for data in response.data]
        print(f"Generated {len(CHUNK_EMBEDDINGS)} embeddings.")
    except Exception as e:
        print(f"Error generating embeddings: {e}")

def cosine_similarity(v1, v2):
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a*b for a, b in zip(v1, v2))
    magnitude_v1 = sum(a*a for a in v1) ** 0.5
    magnitude_v2 = sum(b*b for b in v2) ** 0.5
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    return dot_product / (magnitude_v1 * magnitude_v2)

def retrieve_context(query):
    """Semantic retrieval using Cosine Similarity."""
    """Semantic retrieval using Cosine Similarity."""
    # Lazy Load: Ensure data is loaded before retrieval
    if not CHUNKS:
        initialize_knowledge_base()

    if not CHUNK_EMBEDDINGS:
        # Fallback to keyword if embeddings failed
        return []

    try:
        # Embed query
        query_response = client.embeddings.create(input=query, model="text-embedding-3-small")
        query_embedding = query_response.data[0].embedding
        
        scored_chunks = []
        for i, chunk_embedding in enumerate(CHUNK_EMBEDDINGS):
            score = cosine_similarity(query_embedding, chunk_embedding)
            # Threshold can be adjusted. 0.3 is usually decent for semantic match, 
            # but let's just take top 3 regardless of threshold for now, or use a low one.
            scored_chunks.append((score, CHUNKS[i]))
            
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Debug printing
        print(f"Top match: {scored_chunks[0][0]} -> {scored_chunks[0][1][:50]}...")
        
        # Return top 7 matches to ensure we cover enough ground (e.g. all majors in a faculty)
        return [chunk for score, chunk in scored_chunks[:7]]
    except Exception as e:
        print(f"Error in semantic retrieval: {e}")
        return []

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# load_data() removed from global scope to prevent IIS startup timeout

@app.route("/")
def index():
    return send_from_directory('templates', 'index.html')

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Retrieve context
    context_chunks = retrieve_context(user_message)
    
    # Always include top level admin info if no specific match found, 
    # OR if the score is low? For now, let's just use what we found.
    # But if empty, we MUST provide something or the bot fails.
    
    if not context_chunks:
        # Fallback: Provide general info about valid topics so GPT can at least say "I can answer X, Y, Z"
        context_text = (
            "Context: Middle East University (MEU) in Jordan. "
            "Available Data: President, Board of Trustees, Board of Directors, Council of Deans, "
            "Master's Admission Procedures, International Programs, and various Bachelor Programs. "
            "The specific query did not match any keywords in the database."
        )
    else:
        context_text = "\n\n".join(context_chunks)

    system_prompt = (
        "You are a helpful assistant for Middle East University (MEU) in Jordan. "
        "Use the following context to answer the user's question. "
        "If the answer is not in the context, say you don't have that information. "
        "Be concise and verified.\n\n"
        f"--- Context ---\n{context_text}\n----------------"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Cost effective model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Running locally")
    initialize_knowledge_base()
    app.run(debug=False, port=4000)
