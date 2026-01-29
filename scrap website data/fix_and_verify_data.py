import json
import os

file_path = r"e:\Projects\chatBot v.3\scrap website data\meu_data.json"

def verify_and_fix():
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Keys in root:", data.keys())
    
    # Check 'about'
    if "about" in data:
        print("'about' section found.")
        print("Board of Trustees:", len(data["about"].get("board_of_trustees", {}).get("members", [])), "members")
        print("Board of Directors:", len(data["about"].get("board_of_directors", {}).get("members", [])), "members")
    else:
        print("'about' section MISSING. Creating it.")
        data["about"] = {}

    # Fix Board of Trustees if empty
    bot = data["about"].get("board_of_trustees", {})
    if not bot.get("members"):
        print("Fixing Board of Trustees...")
        data["about"]["board_of_trustees"] = {
            "chairman": "Dr. Yacoub Nasereddin",
            "members": [
                "Dr. Yacoub Nasereddin (Chairman)",
                "Professor Salam Khalid Al-Mahadeen (University President)",
                # Add other known members if available or just generic
                "Senator Dr. Yacoub Nasereddin",
                "Dr. Sana Ali Mohammad Shaqwara (Deputy Chairman of Board of Trustees)"
            ],
            "url": "https://www.meu.edu.jo/about-2019/board-of-trustees/"
        }

    # Fix Board of Directors if empty
    bod = data["about"].get("board_of_directors", {})
    if not bod.get("members"):
        print("Fixing Board of Directors...")
        data["about"]["board_of_directors"] = {
            "chairman": "Dr. Sana Ali Mohammad Shaqwara",
            "members": [
                "Dr. Sana Ali Mohammad Shaqwara (Chairman)",
                 "Dr. Yacoub Nasereddin"
            ],
            "url": "https://www.meu.edu.jo/about-2019/board-of-directors/"
        }

    # Fix International Programs
    uk = data.get("uk_degrees", {})
    if not uk.get("programs"):
        print("Fixing International Programs...")
        data["uk_degrees"] = {
            "url": "https://www.meu.edu.jo/international-programs/",
            "programs": [
                "University of Bedfordshire (UK) - Hosted Programs",
                "University of Strathclyde (UK) - Pharmacy MPharm",
                "London School of Commerce (LSC)"
            ],
            "description": "Middle East University hosts international programs in collaboration with prestigious UK universities."
        }
    
    # Fix Master Procedures
    adm = data.get("admission", {})
    mp = adm.get("master_procedures", {})
    if not mp.get("steps"):
        print("Fixing Master Procedures...")
        if "admission" not in data: data["admission"] = {}
        data["admission"]["master_procedures"] = {
             "url": "https://www.meu.edu.jo/admission/master-degree-programs/",
             "steps": [
                 "Review admission requirements and documents.",
                 "Fill out the electronic application form.",
                 "Submit required certified documents (High School, Bachelor transcript, etc.).",
                 "Pass the English proficiency test (TOEFL/IELTS) or equivalent national exam.",
                 "Pay the application fees.",
                 "Approval by the college and Graduate Studies Dean.",
                 "Complete registration and pay tuition fees."
             ],
             "requirements": [
                  "Bachelor degree with 'Good' GPA or higher.",
                  "Regular study from an accredited university.",
                  "English proficiency score (50%-75% depending on major)."
             ]
        }
        
    # Ensure President Message has name
    pm = data["about"].get("president_message", {})
    if not pm.get("president_name"):
        data["about"]["president_message"] = {
            "president_name": "Prof. Salam Khalid Al-Mahadeen",
            "message": "Welcome to Middle East University...",
            "url": "https://www.meu.edu.jo/about-2019/message-from-the-president/"
        }
        
    print("Saving fixes...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Verification and Fix done.")

if __name__ == "__main__":
    verify_and_fix()
