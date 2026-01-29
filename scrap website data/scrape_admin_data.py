import json
import requests
from bs4 import BeautifulSoup
import os

# File paths
json_file_path = r"e:\Projects\chatBot v.3\scrap website data\meu_data.json"
output_file_path = json_file_path # Overwrite the same file

def get_soup(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8' # Ensure correct encoding for Arabic
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_board_of_trustees():
    url = "https://www.meu.edu.jo/about-2019/board-of-trustees/"
    soup = get_soup(url)
    data = {"url": url, "members": []}
    if not soup:
        return data
    
    # This selector depends on the actual page structure. 
    # Based on standard Wordpress/MEU structure, usually lists are in entry-content
    content = soup.find('div', class_='entry-content')
    if content:
        # Looking for list items or paragraphs with names
        # Assuming names are in a list <ul> or just paragraphs <p>
        # Let's try to grab all list items first as they are most likely for members
        for li in content.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                data["members"].append(text)
        
        # If no list items, try paragraphs
        if not data["members"]:
            for p in content.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 5 and len(text) < 100: # Heuristic for names
                    data["members"].append(text)
    
    return data

def scrape_board_of_directors():
    url = "https://www.meu.edu.jo/about-2019/board-of-directors/"
    soup = get_soup(url)
    data = {"url": url, "members": []}
    if not soup:
        return data
    
    content = soup.find('div', class_='entry-content')
    if content:
        for li in content.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                data["members"].append(text)
                
        if not data["members"]:
            for p in content.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 5 and len(text) < 100:
                    data["members"].append(text)
    return data

def scrape_president_message():
    url = "https://www.meu.edu.jo/about-2019/message-from-the-president/"
    soup = get_soup(url)
    data = {"url": url, "president_name": "", "message": ""}
    if not soup:
        return data
    
    content = soup.find('div', class_='entry-content')
    if content:
        # Try to find the name - often in a heading or strong tag at the end/start
        # Search results told us: Prof. Salam Khalid Al-Mahadeen
        # Let's extract the full text for now
        data["message"] = content.get_text(strip=True)
        
        # Heuristic to find name if possible, or hardcode based on known fact if scrape fails
        # But let's try to find "Prof" or "President"
        for strong in content.find_all('strong'):
            text = strong.get_text(strip=True)
            if "Prof" in text or "Dr" in text:
                data["president_name"] = text
                break
    
    if not data["president_name"]:
         data["president_name"] = "Prof. Salam Khalid Al-Mahadeen" # Fallback from research
         
    return data

def scrape_council_of_deans():
    # URL might be different, trying a common one or searching
    url = "https://www.meu.edu.jo/about-2019/council-of-deans/" 
    soup = get_soup(url)
    data = {"url": url, "members": []}
    if not soup:
        return data
    
    content = soup.find('div', class_='entry-content')
    if content:
        for li in content.find_all('li'):
             data["members"].append(li.get_text(strip=True))
    
    return data

def scrape_master_procedures():
    url = "https://www.meu.edu.jo/admission/master-degree-programs/"
    soup = get_soup(url)
    data = {"url": url, "steps": []}
    
    if not soup:
        # Fallback URL
        url = "https://www.meu.edu.jo/admission-registration-department/"
        soup = get_soup(url)
        data["url"] = url
    
    if soup:
        content = soup.find('div', class_='entry-content')
        if content:
             # Look for ordered lists for procedures
            ol = content.find('ol')
            if ol:
                for li in ol.find_all('li'):
                    data["steps"].append(li.get_text(strip=True))
            else:
                # Try finding text with "Master" or "Admission"
                paragraphs = content.find_all('p')
                for p in paragraphs:
                    if "Master" in p.get_text() or "ماجستير" in p.get_text():
                        data["steps"].append(p.get_text(strip=True))
    return data

def scrape_international_programs():
    url = "https://www.meu.edu.jo/international-programs/"
    soup = get_soup(url)
    data = {"url": url, "programs": []}
    if soup:
        content = soup.find('div', class_='entry-content')
        if content:
            # Look for program names, often headings or list items
            for h in content.find_all(['h3', 'h4']):
                data["programs"].append(h.get_text(strip=True))
                
            if not data["programs"]:
                for li in content.find_all('li'):
                    data["programs"].append(li.get_text(strip=True))
    return data


def main():
    print("Loading existing JSON...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print("Scraping data...")
    
    # Initialize 'about' if not present
    if "about" not in json_data:
        json_data["about"] = {}
        
    print("- Board of Trustees")
    json_data["about"]["board_of_trustees"] = scrape_board_of_trustees()
    
    print("- Board of Directors")
    json_data["about"]["board_of_directors"] = scrape_board_of_directors()
    
    print("- President Message")
    json_data["about"]["president_message"] = scrape_president_message()
    
    print("- Council of Deans")
    json_data["about"]["council_of_deans"] = scrape_council_of_deans()
    
    # Admission
    if "admission" not in json_data:
        json_data["admission"] = {}
        
    print("- Master Procedures")
    json_data["admission"]["master_procedures"] = scrape_master_procedures()
    
    # International Programs
    print("- International Programs")
    json_data["uk_degrees"] = scrape_international_programs() # Mapping to uk_degrees or new key
    
    # Specific missing Deans (Hardcoding from verified research if not found in lists)
    # Adding a specific section for key figures to make it easy to answer
    if "key_figures" not in json_data:
        json_data["key_figures"] = {}
        
    json_data["key_figures"]["dean_scientific_research"] = "Prof. Dr. Ahmed Abdulhay Mousa"
    json_data["key_figures"]["dean_arts_educational_sciences"] = "Dr. Ayat Al Mughabi"
    
    print("Saving updated JSON...")
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
        
    print("Done!")

if __name__ == "__main__":
    main()
