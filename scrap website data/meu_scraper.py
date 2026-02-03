"""
MEU Comprehensive Web Scraper for Chatbot Knowledge Base
Scrapes data from:
- Ebooklet (https://ebooklet.meu.edu.jo) - uses Selenium for JavaScript-rendered content
- Main Website (https://www.meu.edu.jo) - uses requests for static content
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import os

# Try to import Selenium, provide instructions if not available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("WARNING: Selenium not installed. Install with: pip install selenium")
    print("Ebooklet scraping will be limited without Selenium.")


class MEUEbookletScraper:
    """Scraper for MEU Ebooklet website (JavaScript-rendered content)."""
    
    def __init__(self):
        self.base_url = "https://ebooklet.meu.edu.jo"
        self.driver = None
        self.data = {
            "bachelor_programs": [],
            "master_programs": [],
            "diploma_programs": [],
            "higher_diploma_programs": [],
            "faculties": [],
            "pricing": {}
        }
        
        # Bachelor program IDs from the URLs provided
        self.bachelor_ids = [
            "eng-lit", "arabic-lit", "translation", "edu-tech", "sports-mgmt",
            "law",
            "business-admin", "accounting", "digital-marketing", "business-intelligence",
            "fintech", "ecommerce", "hrm", "supply-chain", "business-psych",
            "computer-science", "ai", "software-eng", "cybersecurity",
            "journalism", "broadcasting",
            "renewable-energy", "smart-systems", "architecture", "graphic-design",
            "interior-design", "biomedical-eng",
            "pharmacy", "cosmetics",
            "nursing",
            "physiotherapy", "medical-lab", "nutrition", "genetics", "paramedic"
        ]
        
        # Master program IDs
        self.master_ids = [
            "law-private", "law-public", "mba", "master-accounting",
            "master-media", "master-pharmacy"
        ]
        
        # Diploma program IDs
        self.diploma_ids = [
            "dip-nursing", "dip-physiotherapy", "dip-midwifery", "dip-medical-lab",
            "dip-quantity-calculation", "dip-smart-systems", "dip-renewable-energy",
            "dip-digital-media", "dip-multimedia", "dip-game-development"
        ]
        
        # Higher diploma
        self.higher_diploma_ids = ["dip-higher-diploma-in-education"]
        
        # Faculty categories
        self.faculty_ids = [
            "arts-education", "law", "business", "it", "media",
            "engineering", "pharmacy", "nursing", "allied-medical"
        ]
    
    def init_browser(self):
        """Initialize Edge browser with Selenium."""
        if not SELENIUM_AVAILABLE:
            print("Selenium not available, skipping browser initialization")
            return False
        
        try:
            options = EdgeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Edge(options=options)
            print("Browser initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing browser: {e}")
            return False
    
    def close_browser(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def extract_js_data(self, page_source):
        """Extract JavaScript data from page source."""
        data = {}
        
        # Look for bachelorFaculties variable
        bachelor_match = re.search(r'const\s+bachelorFaculties\s*=\s*(\[[\s\S]*?\]);', page_source)
        if bachelor_match:
            try:
                # Clean the JavaScript and parse as JSON
                js_data = bachelor_match.group(1)
                # Remove JavaScript comments
                js_data = re.sub(r'//[^\n]*', '', js_data)
                data['bachelorFaculties'] = json.loads(js_data)
            except:
                pass
        
        # Look for mastersFaculties variable
        masters_match = re.search(r'const\s+mastersFaculties\s*=\s*(\[[\s\S]*?\]);', page_source)
        if masters_match:
            try:
                js_data = masters_match.group(1)
                js_data = re.sub(r'//[^\n]*', '', js_data)
                data['mastersFaculties'] = json.loads(js_data)
            except:
                pass
        
        # Look for pricingData
        pricing_match = re.search(r'const\s+pricingData\s*=\s*(\{[\s\S]*?\});', page_source)
        if pricing_match:
            try:
                js_data = pricing_match.group(1)
                js_data = re.sub(r'//[^\n]*', '', js_data)
                data['pricingData'] = json.loads(js_data)
            except:
                pass
        
        return data
    
    def scrape_program_page(self, program_type, program_id):
        """Scrape a specific program page."""
        if program_type == "bachelor":
            url = f"{self.base_url}/mainbach.html?id={program_id}"
        elif program_type == "master":
            url = f"{self.base_url}/mainmaster.html?id={program_id}"
        elif program_type == "diploma":
            url = f"{self.base_url}/main.html?id={program_id}"
        elif program_type == "higher_diploma":
            url = f"{self.base_url}/mainhigher.html?id={program_id}"
        else:
            return None
        
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for JavaScript to render
            
            # Extract program information from the rendered page
            program_data = {
                "id": program_id,
                "url": url,
                "type": program_type
            }
            
            # Get program name
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, "h1, .program-title, .major-name")
                program_data["name_ar"] = name_elem.text.strip()
            except:
                program_data["name_ar"] = program_id.replace("-", " ").title()
            
            # Get credit hours and duration
            try:
                info_text = self.driver.find_element(By.CSS_SELECTOR, ".program-info, .major-details, .info-section").text
                
                # Extract credit hours
                hours_match = re.search(r'(\d+)\s*(?:ساعة|credit|hours)', info_text, re.I)
                if hours_match:
                    program_data["credit_hours"] = int(hours_match.group(1))
                
                # Extract duration
                years_match = re.search(r'(\d+)\s*(?:سنوات|سنة|years?)', info_text, re.I)
                if years_match:
                    program_data["duration_years"] = int(years_match.group(1))
            except:
                pass
            
            # Get description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".description, .program-description, .general-info p")
                program_data["description"] = desc_elem.text.strip()
            except:
                pass
            
            # Get admission requirements (try JS data first, then UI)
            try:
                # 1. Try to find requirements in embedded JS data
                if "_js_data" in program_data and "bachelorFaculties" in program_data["_js_data"]:
                    faculties = program_data["_js_data"]["bachelorFaculties"]
                    for faculty in faculties:
                        for major in faculty.get("majors", []):
                            if major.get("id") == program_id:
                                if "requirements" in major:
                                    # Handle both object and array formats
                                    reqs = major["requirements"]
                                    if isinstance(reqs, dict):
                                        req_text = f"High School: {reqs.get('highschool', '')}\nBridging: {reqs.get('bridging', '')}"
                                        program_data["admission_requirements"] = req_text.strip()
                                    elif isinstance(reqs, list):
                                        program_data["admission_requirements"] = "\n".join(reqs)
                                    break
                
                # 2. If JS extraction failed, try UI extraction with better selectors
                if "admission_requirements" not in program_data or program_data["admission_requirements"] == "شروط القبول":
                    # Try to find the content box that appears after the "General Secondary" button
                    # Javascript usually toggles IDs like #txtHighSchool or classes
                    req_content = self.driver.execute_script("""
                        var content = '';
                        var highSchool = document.querySelector('#txtHighSchool, .requirements-content');
                        if (highSchool) content += 'High School: ' + highSchool.innerText + '\\n';
                        
                        var bridging = document.querySelector('#txtBridging');
                        if (bridging) content += 'Bridging: ' + bridging.innerText;
                        
                        if (!content) {
                            // Fallback: look for the section following the header
                            var header = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, div')).find(el => el.innerText.includes('شروط القبول'));
                            if (header) {
                                var next = header.nextElementSibling;
                                if (next) content = next.innerText;
                            }
                        }
                        return content;
                    """)
                    
                    if req_content and len(req_content.strip()) > 10:
                        program_data["admission_requirements"] = req_content.strip()
                    else:
                        # Fallback to previous method but try to get parent's text
                        req_section = self.driver.find_element(By.XPATH, "//*[contains(text(), 'شروط القبول')]/..")
                        full_text = req_section.text.strip()
                        if len(full_text) > len("شروط القبول") + 10:
                            program_data["admission_requirements"] = full_text
            except Exception as e:
                # print(f"Error extracting requirements: {e}")
                pass

            # Get Required Documents (الوثائق المطلوبة)
            try:
                # Logic: Find header containing "الوثائق المطلوبة" and get content
                docs_content = self.driver.execute_script("""
                    var content = '';
                    var headers = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, div, span, p'));
                    var targetHeader = headers.find(el => el.innerText.includes('الوثائق المطلوبة') && el.innerText.length < 50);
                    
                    if (targetHeader) {
                        // Try to find the next container or list
                        var next = targetHeader.nextElementSibling;
                        if (next) {
                            content = next.innerText;
                        } else {
                            // Sometimes it's in a parent's sibling
                            var parent = targetHeader.parentElement;
                            if (parent && parent.nextElementSibling) {
                                content = parent.nextElementSibling.innerText;
                            }
                        }
                    }
                    return content;
                """)
                
                if docs_content and len(docs_content.strip()) > 5:
                     program_data["required_documents"] = docs_content.strip()
            except Exception as e:
                pass
            
            # Get credit hour price (سعر الساعة المعتمدة)
            try:
                price_jod = self.driver.find_element(By.ID, "priceJOD")
                if price_jod:
                    program_data["credit_hour_price_jod"] = price_jod.text.strip()
            except:
                pass
            
            try:
                price_usd = self.driver.find_element(By.ID, "priceUSD")
                if price_usd:
                    program_data["credit_hour_price_usd"] = price_usd.text.strip()
            except:
                pass
            
            # Get pricing information (registration fees)
            try:
                price_elems = self.driver.find_elements(By.CSS_SELECTOR, ".price-item, .fee-row, li")
                fees = []
                for elem in price_elems:
                    text = elem.text.strip()
                    if "دينار" in text or "JOD" in text:
                        fees.append(text)
                if fees:
                    program_data["fees"] = fees
            except:
                pass
            
            # Try to get embedded JavaScript data
            page_source = self.driver.page_source
            js_data = self.extract_js_data(page_source)
            if js_data:
                program_data["_js_data"] = js_data
            
            return program_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {"id": program_id, "url": url, "error": str(e)}
    
    def scrape_faculty_selection_page(self, faculty_id):
        """Scrape faculty selection page to get list of programs."""
        url = f"{self.base_url}/BachSubLevelSelection.html?id={faculty_id}"
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            faculty_data = {
                "id": faculty_id,
                "url": url,
                "programs": []
            }
            
            # Get faculty name
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1, .faculty-title")
                faculty_data["name_ar"] = title.text.strip()
            except:
                pass
            
            # Get list of programs/majors
            try:
                program_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='mainbach'], .program-card, .major-card")
                for link in program_links:
                    href = link.get_attribute("href")
                    if href and "id=" in href:
                        prog_id = href.split("id=")[-1]
                        faculty_data["programs"].append({
                            "id": prog_id,
                            "name": link.text.strip()
                        })
            except:
                pass
            
            # Try to get embedded JavaScript data (often contains all faculties data)
            page_source = self.driver.page_source
            js_data = self.extract_js_data(page_source)
            if js_data:
                faculty_data["_js_data"] = js_data
            
            return faculty_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {"id": faculty_id, "url": url, "error": str(e)}
    
    def scrape_all(self):
        """Scrape all ebooklet data."""
        if not self.init_browser():
            print("Could not initialize browser, skipping ebooklet scraping")
            return self.data
        
        try:
            print("\n" + "="*50)
            print("SCRAPING EBOOKLET DATA")
            print("="*50)
            
            # First, try to get all data from one page (embedded JS)
            print("\n[1/5] Extracting embedded JavaScript data...")
            self.driver.get(f"{self.base_url}/mainbach.html?id=computer-science")
            time.sleep(3)
            page_source = self.driver.page_source
            js_data = self.extract_js_data(page_source)
            
            if js_data.get('bachelorFaculties'):
                print("  ✓ Found bachelorFaculties data")
                self.data["faculties"] = js_data['bachelorFaculties']
            
            if js_data.get('pricingData'):
                print("  ✓ Found pricingData")
                self.data["pricing"] = js_data['pricingData']
            
            # Scrape faculty selection pages to get structure
            print("\n[2/5] Scraping faculty selection pages...")
            for faculty_id in self.faculty_ids:
                print(f"  - Scraping faculty: {faculty_id}")
                faculty_data = self.scrape_faculty_selection_page(faculty_id)
                if faculty_data and not faculty_data.get("error"):
                    # Merge any new JS data
                    if faculty_data.get("_js_data", {}).get("bachelorFaculties"):
                        self.data["faculties"] = faculty_data["_js_data"]["bachelorFaculties"]
                time.sleep(0.5)
            
            # Scrape individual bachelor programs
            print(f"\n[3/5] Scraping {len(self.bachelor_ids)} bachelor programs...")
            for i, prog_id in enumerate(self.bachelor_ids):
                print(f"  - [{i+1}/{len(self.bachelor_ids)}] Scraping: {prog_id}")
                prog_data = self.scrape_program_page("bachelor", prog_id)
                if prog_data:
                    self.data["bachelor_programs"].append(prog_data)
                time.sleep(0.5)
            
            # Scrape master programs
            print(f"\n[4/5] Scraping {len(self.master_ids)} master programs...")
            # First try to get masters data from a masters page
            self.driver.get(f"{self.base_url}/mainmaster.html?id=mba")
            time.sleep(3)
            page_source = self.driver.page_source
            masters_js = self.extract_js_data(page_source)
            if masters_js.get('mastersFaculties'):
                print("  ✓ Found mastersFaculties data")
                self.data["master_faculties"] = masters_js['mastersFaculties']
            
            for i, prog_id in enumerate(self.master_ids):
                print(f"  - [{i+1}/{len(self.master_ids)}] Scraping: {prog_id}")
                prog_data = self.scrape_program_page("master", prog_id)
                if prog_data:
                    self.data["master_programs"].append(prog_data)
                time.sleep(0.5)
            
            # Scrape diploma programs
            print(f"\n[5/5] Scraping {len(self.diploma_ids)} diploma programs...")
            for i, prog_id in enumerate(self.diploma_ids):
                print(f"  - [{i+1}/{len(self.diploma_ids)}] Scraping: {prog_id}")
                prog_data = self.scrape_program_page("diploma", prog_id)
                if prog_data:
                    self.data["diploma_programs"].append(prog_data)
                time.sleep(0.5)
            
            # Scrape higher diploma
            print("\n  Scraping higher diploma programs...")
            for prog_id in self.higher_diploma_ids:
                prog_data = self.scrape_program_page("higher_diploma", prog_id)
                if prog_data:
                    self.data["higher_diploma_programs"].append(prog_data)
            
            print("\n✓ Ebooklet scraping complete!")
            
        finally:
            self.close_browser()
        
        return self.data


class MEUMainWebsiteScraper:
    """Scraper for MEU Main Website (static content)."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,ar;q=0.3',
        })
        self.base_url = "https://www.meu.edu.jo"
        self.data = {
            "university": {},
            "about": {},
            "admission": {},
            "facilities": [],
            "deanships": [],
            "units": [],
            "contact": {},
            "faq": [],
            "links": {}
        }
    
    def fetch_page(self, url, delay=0.5):
        """Fetch a page with error handling."""
        try:
            time.sleep(delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return None
    
    def extract_text_content(self, soup, selector=None):
        """Extract main text content from a page."""
        if not soup:
            return ""
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        if selector:
            content = soup.select_one(selector)
            if content:
                return content.get_text(separator="\n", strip=True)
        
        # Try common content selectors
        for sel in [".entry-content", ".page-content", "article", "main", ".content"]:
            content = soup.select_one(sel)
            if content:
                return content.get_text(separator="\n", strip=True)
        
        return soup.get_text(separator="\n", strip=True)
    
    def extract_links(self, soup, base_url):
        """Extract all links from a page."""
        links = []
        if not soup:
            return links
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = urljoin(base_url, href)
            if href.startswith('http'):
                links.append({
                    "text": a.get_text(strip=True),
                    "url": href
                })
        return links
    
    def scrape_about_pages(self):
        """Scrape about section pages."""
        print("\n[About Section]")
        
        about_urls = {
            "meu_in_words": f"{self.base_url}/about-2019/meu-in-words/",
            "president_message": f"{self.base_url}/about-2019/message-from-the-president/",
            "chairman_message": f"{self.base_url}/about-2019/chairman-of-the-board-of-trustees/",
            "board_of_trustees": f"{self.base_url}/about-2019/board-of-trustees/",
            "council_of_deans": f"{self.base_url}/about-2019/council-of-deans/",
            "board_of_directors": f"{self.base_url}/about-2019/board-of-directors/",
        }
        
        for key, url in about_urls.items():
            print(f"  - Scraping: {key}")
            soup = self.fetch_page(url)
            if soup:
                self.data["about"][key] = {
                    "url": url,
                    "content": self.extract_text_content(soup),
                    "title": soup.title.string if soup.title else key
                }
    
    def scrape_admission_pages(self):
        """Scrape admission section pages."""
        print("\n[Admission Section]")
        
        admission_urls = {
            "overview": f"{self.base_url}/admission/",
            "about_department": f"{self.base_url}/admission/about-the-admission-and-registration-department/",
            "bachelor_procedures": f"{self.base_url}/admission/bachelor-programmes/admission-and-registration-procedures-for-undergraduate-studies/",
            "master_procedures": f"{self.base_url}/admission/masters-programmes/admission-and-registration-procedures-for-graduate-studies/",
        }
        
        for key, url in admission_urls.items():
            print(f"  - Scraping: {key}")
            soup = self.fetch_page(url)
            if soup:
                self.data["admission"][key] = {
                    "url": url,
                    "content": self.extract_text_content(soup),
                    "links": self.extract_links(soup, url)
                }
    
    def scrape_facilities_pages(self):
        """Scrape facilities section pages."""
        print("\n[Facilities Section]")
        
        # Main facilities page
        facilities_url = f"{self.base_url}/facilities/"
        soup = self.fetch_page(facilities_url)
        
        if soup:
            # Get list of facility sub-pages
            facility_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'facilities/' in href and href != facilities_url:
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    facility_links.append({
                        "name": a.get_text(strip=True),
                        "url": href
                    })
            
            # Scrape each facility page
            seen_urls = set()
            for link in facility_links:
                if link['url'] not in seen_urls and link['name']:
                    seen_urls.add(link['url'])
                    print(f"  - Scraping: {link['name'][:30]}...")
                    sub_soup = self.fetch_page(link['url'])
                    if sub_soup:
                        self.data["facilities"].append({
                            "name": link['name'],
                            "url": link['url'],
                            "content": self.extract_text_content(sub_soup)
                        })
    
    def scrape_deanships_pages(self):
        """Scrape deanships section pages."""
        print("\n[Deanships Section]")
        
        deanships_url = f"{self.base_url}/deanships/"
        soup = self.fetch_page(deanships_url)
        
        if soup:
            self.data["deanships"].append({
                "name": "Deanships Overview",
                "url": deanships_url,
                "content": self.extract_text_content(soup),
                "links": self.extract_links(soup, deanships_url)
            })
    
    def scrape_units_pages(self):
        """Scrape units section pages."""
        print("\n[Units Section]")
        
        units_url = f"{self.base_url}/units/"
        soup = self.fetch_page(units_url)
        
        if soup:
            self.data["units"].append({
                "name": "Units Overview",
                "url": units_url,
                "content": self.extract_text_content(soup),
                "links": self.extract_links(soup, units_url)
            })
    
    def scrape_home_page(self):
        """Scrape home page for general info."""
        print("\n[Home Page]")
        
        soup = self.fetch_page(self.base_url)
        if soup:
            self.data["university"] = {
                "name": "Middle East University",
                "name_ar": "جامعة الشرق الأوسط",
                "url": self.base_url,
                "founded": 2005,
                "location": "Amman, Jordan",
                "description": self.extract_text_content(soup)[:2000],  # First 2000 chars
            }
            
            # Extract contact info from footer
            footer = soup.find('footer')
            if footer:
                footer_text = footer.get_text()
                # Extract phone numbers
                phones = re.findall(r'\+?962[\s\-]?\d[\s\-]?\d{7,8}', footer_text)
                if phones:
                    self.data["contact"]["phones"] = list(set(phones))
                
                # Extract email
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', footer_text)
                if emails:
                    self.data["contact"]["emails"] = list(set(emails))
    
    def scrape_uk_degrees(self):
        """Scrape UK degrees portal."""
        print("\n[UK Degrees Portal]")
        
        url = "https://ukdegrees.meu.edu.jo/"
        try:
            response = self.session.get(url, timeout=30)
            if response.ok:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.data["uk_degrees"] = {
                    "url": url,
                    "title": soup.title.string if soup.title else "UK Degrees",
                    "content": self.extract_text_content(soup)
                }
                print("  ✓ UK Degrees scraped")
        except Exception as e:
            print(f"  Error: {e}")
    
    def scrape_all(self):
        """Scrape all main website data."""
        print("\n" + "="*50)
        print("SCRAPING MEU MAIN WEBSITE")
        print("="*50)
        
        self.scrape_home_page()
        self.scrape_about_pages()
        self.scrape_admission_pages()
        self.scrape_facilities_pages()
        self.scrape_deanships_pages()
        self.scrape_units_pages()
        self.scrape_uk_degrees()
        
        # Add useful links
        self.data["links"] = {
            "portals": {
                "student_portal": "https://www.meu.edu.jo/student-portal/",
                "staff_portal": "https://mymeu.meu.edu.jo/",
                "edugate": "https://reg.meu.edu.jo/",
                "elearning": "http://elearning.meu.edu.jo/"
            },
            "information": {
                "meu_map": "https://www.meu.edu.jo/meu-map/",
                "academic_calendar": "https://www.meu.edu.jo/admission/academic-calendar/",
                "booklet": "https://www.meu.edu.jo/admission/meu-booklet/",
                "student_handbook": "https://www.meu.edu.jo/admission/students-guide/"
            },
            "other": {
                "faq": "https://www.meu.edu.jo/faq/",
                "contact": "https://www.meu.edu.jo/contact-us/",
                "job_application": "https://www.meu.edu.jo/job-application-2/"
            }
        }
        
        print("\n✓ Main website scraping complete!")
        return self.data


class MEUComprehensiveScraper:
    """Main scraper that combines ebooklet and main website scrapers."""
    
    def __init__(self):
        self.ebooklet_scraper = MEUEbookletScraper()
        self.website_scraper = MEUMainWebsiteScraper()
        self.combined_data = {}
    
    def scrape_all(self):
        """Scrape all data from both sources."""
        print("\n" + "="*60)
        print("MEU COMPREHENSIVE WEB SCRAPER")
        print("="*60)
        print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Scrape ebooklet
        ebooklet_data = self.ebooklet_scraper.scrape_all()
        
        # Scrape main website
        website_data = self.website_scraper.scrape_all()
        
        # Combine data
        self.combined_data = {
            "metadata": {
                "scraped_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "sources": [
                    "https://ebooklet.meu.edu.jo",
                    "https://www.meu.edu.jo"
                ]
            },
            "university": website_data.get("university", {}),
            "ebooklet": ebooklet_data,
            "about": website_data.get("about", {}),
            "admission": website_data.get("admission", {}),
            "facilities": website_data.get("facilities", []),
            "deanships": website_data.get("deanships", []),
            "units": website_data.get("units", []),
            "uk_degrees": website_data.get("uk_degrees", {}),
            "contact": website_data.get("contact", {}),
            "links": website_data.get("links", {})
        }
        
        return self.combined_data
    
    def save_to_json(self, filename="meu_data.json"):
        """Save scraped data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.combined_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n" + "="*60)
        print("DATA SAVED")
        print("="*60)
        print(f"File: {filename}")
        print(f"Size: {os.path.getsize(filename) / 1024:.1f} KB")
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print summary of scraped data."""
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        
        eb = self.combined_data.get("ebooklet", {})
        print(f"Bachelor Programs: {len(eb.get('bachelor_programs', []))}")
        print(f"Master Programs: {len(eb.get('master_programs', []))}")
        print(f"Diploma Programs: {len(eb.get('diploma_programs', []))}")
        print(f"Higher Diploma Programs: {len(eb.get('higher_diploma_programs', []))}")
        print(f"About Pages: {len(self.combined_data.get('about', {}))}")
        print(f"Admission Pages: {len(self.combined_data.get('admission', {}))}")
        print(f"Facilities: {len(self.combined_data.get('facilities', []))}")
        print(f"Deanships: {len(self.combined_data.get('deanships', []))}")
        print(f"Units: {len(self.combined_data.get('units', []))}")


def main():
    """Main function to run the scraper."""
    scraper = MEUComprehensiveScraper()
    scraper.scrape_all()
    scraper.save_to_json()
    print("\n✓ All done!")


if __name__ == "__main__":
    main()
