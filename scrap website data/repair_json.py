
import json
import re
from bs4 import BeautifulSoup
import requests

def clean_js_string(js_str):
    """
    Parses the massive JS string found in 'admission_requirements' 
    and returns a clean dictionary of requirements per program ID.
    """
    try:
        # Extract the 'bachelorFaculties' array
        match = re.search(r'const\s+bachelorFaculties\s*=\s*(\[[\s\S]*?\]);', js_str)
        if not match:
            return None
        
        json_str = match.group(1)
        # Remove comments // ...
        json_str = re.sub(r'//.*', '', json_str)
        # Fix keys that might not be quoted (simple fix, might need more)
        # Actually the scraper likely saved it fairly clean, let's try direct parse
        # If it's pure JS object syntax (keys not quoted), json.loads will fail.
        # We might need a loose parser or just regex for specific fields.
        
        # Let's try to extract requirements for each ID using regex to be safe
        # Pattern: id: "eng-lit" ... requirements: [...]
        
        reqs_map = {}
        
        # Split by program/course definitions roughly
        # This is a bit hacky but safer than writing a full JS parser
        programs = json_str.split('id:')
        
        for prog in programs[1:]: # skip first empty chunk
            # extract ID
            id_match = re.search(r'["\']([\w-]+)["\']', prog)
            if not id_match: continue
            prog_id = id_match.group(1)
            
            # extract requirements array
            req_match = re.search(r'requirements:\s*\[([\s\S]*?)\]', prog)
            if req_match:
                req_content = req_match.group(1)
                # clean up quotes and commas to make it a list
                req_lines = [line.strip().strip('"\'').strip(',') for line in req_content.split('\n') if line.strip()]
                reqs_map[prog_id] = req_lines
                
        # Also try to extract pricing data
        pricing_map = {}
        price_match = re.search(r'const\s+pricingData\s*=\s*(\[[\s\S]*?\]);', js_str)
        if price_match:
            try:
                # This is usually valid JSON (list of dicts) if we clean comments
                p_str = price_match.group(1)
                p_str = re.sub(r'//.*', '', p_str)
                # JS keys might not be quoted, use regex specifically for this structure
                # { courseId: "eng-lit", basePriceJOD: 80, basePriceUSD: 115 }
                
                # Simple extraction strategy: split by '}'
                items = p_str.split('}')
                for item in items:
                    cid_m = re.search(r'courseId:\s*["\']([\w-]+)["\']', item)
                    jod_m = re.search(r'basePriceJOD:\s*(\d+)', item)
                    usd_m = re.search(r'basePriceUSD:\s*(\d+)', item)
                    
                    if cid_m and jod_m:
                        pricing_map[cid_m.group(1)] = {
                            "jod": int(jod_m.group(1)),
                            "usd": int(usd_m.group(1)) if usd_m else 0
                        }
            except:
                pass
                
        return reqs_map, pricing_map
    except Exception as e:
        print(f"Error parsing JS: {e}")
        return None

def fetch_missing_about_data():
    """
    Fetches the missing About pages.
    """
    urls = {
        "president_message": "https://www.meu.edu.jo/about-2019/message-from-the-president/",
        "board_of_trustees": "https://www.meu.edu.jo/about-2019/board-of-trustees/",
        "council_of_deans": "https://www.meu.edu.jo/about-2019/council-of-deans/",
        "dean_research": "https://www.meu.edu.jo/deanships/deanship-of-graduate-studies-and-scientific-research/",
        "all_deanships": "https://www.meu.edu.jo/deanships/" 
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    results = {}
    
    for key, url in urls.items():
        print(f"Fetching {key}...")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                # Try to find the main content
                content = soup.find('div', class_='entry-content') or soup.find('div', class_='wpb_wrapper') or soup.body
                if content:
                    text = content.get_text(separator='\n', strip=True)
                    results[key] = {
                        "url": url,
                        "text": text[:5000] # limit size
                    }
        except Exception as e:
            print(f"Failed to fetch {key}: {e}")
            
    return results

def main():
    path = "e:\\Projects\\chatBot v.3\\scrap website data\\meu_data.json"
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("Loaded JSON.")
    
    # 1. Parse hidden requirements
    # We'll grab the JS string from the first bachelor program (it seems repeated)
    # or just iterate until we find one.
    
    js_source = None
    for prog in data.get('ebooklet', {}).get('bachelor_programs', []):
        if 'admission_requirements' in prog and 'const bachelorFaculties' in prog['admission_requirements']:
            js_source = prog['admission_requirements']
            break
            
    if js_source:
        print("Found JS source code. Parsing requirements...")
        reqs_map, pricing_map = clean_js_string(js_source)
        
        if reqs_map:
            print(f"Extracted requirements for {len(reqs_map)} programs.")
            print(f"Extracted pricing for {len(pricing_map)} programs.")
            
            # Update structure
            for prog in data['ebooklet']['bachelor_programs']:
                pid = prog.get('id')
                
                # Requirements
                if pid in reqs_map:
                    prog['admission_requirements_parsed'] = reqs_map[pid]
                    # Also try to extract GPA if possible
                    txt = " ".join(reqs_map[pid])
                    # Match both 60% and %60 (Arabic style)
                    gpa_match = re.search(r'(?:%(\d+)|(\d+)%)', txt)
                    if gpa_match:
                        # group 1 is %60, group 2 is 60%
                        val = gpa_match.group(1) or gpa_match.group(2)
                        prog['admission_gpa'] = int(val)
                
                # Pricing
                if pid in pricing_map:
                    prog['pricing_merged'] = pricing_map[pid]
                    # Also set top level fields if missing
                    if 'credit_hour_price_jod' not in prog:
                         prog['credit_hour_price_jod'] = str(pricing_map[pid]['jod'])
                    if 'credit_hour_price_usd' not in prog:
                         prog['credit_hour_price_usd'] = str(pricing_map[pid]['usd'])
    
    # 2. Add missing About Data
    print("Fetching missing administrative data...")
    about_data = fetch_missing_about_data()
    data['administrative_updates'] = about_data
    
    # Save
    new_path = "e:\\Projects\\chatBot v.3\\scrap website data\\meu_data_fixed.json"
    with open(new_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved fixed data to {new_path}")

if __name__ == "__main__":
    main()
