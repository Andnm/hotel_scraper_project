import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from io import BytesIO, StringIO
import time
import openpyxl
import json
import tempfile
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import random

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)

try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

def get_driver(is_headless=True):
    # Check if running in Docker/Linux with Chrome installed
    is_docker = os.path.exists('/.dockerenv') or os.path.exists('/usr/bin/google-chrome')
    
    if is_docker:
        # Use Chrome in Docker
        options = ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=vi-VN')
        options.add_argument(f'user-agent={get_random_user_agent()}')
        
        service = ChromeService() # Assumes chromedriver is in PATH (installed by package usually or we need to manage it)
        # In python-slim + chrome install, we might need chromedriver. 
        # The Dockerfile I wrote installs google-chrome-stable but NOT chromedriver explicitly.
        # I should update Dockerfile to install chromedriver or use webdriver-manager.
        
        # Better: use webdriver_manager in code to be safe
        from webdriver_manager.chrome import ChromeDriverManager
        service = ChromeService(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # Fake Geo for Chrome
        try:
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": 21.028511,
                "longitude": 105.854164,
                "accuracy": 100
            })
            driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {
                "timezoneId": "Asia/Ho_Chi_Minh"
            })
        except:
            pass
            
        return driver
    else:
        # Use Edge locally (Windows)
        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            if not is_headless:
                temp_dir = tempfile.mkdtemp(prefix='selenium_booking_')
            
            options = EdgeOptions()
            options.use_chromium = True
            if is_headless:
                options.add_argument('--headless=new')
                
            options.add_argument('--disable-gpu')
            options.add_argument('--lang=vi-VN')
            options.add_argument(f'user-agent={get_random_user_agent()}')
            
            # Fake Geo for Edge
            # ... (Logic applies later)
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            return driver
        except Exception as e:
            raise Exception(f"Failed to initialize Edge driver: {e}")

def is_booking_link(text):
    if pd.isna(text) or text is None:
        return False
    text_str = str(text).strip()
    return 'booking.com/hotel/' in text_str


def get_markets_from_excel(file_bytes):
    """Lấy danh sách các markets (sheet names) từ Excel file"""
    try:
        wb = openpyxl.load_workbook(BytesIO(file_bytes))
        return wb.sheetnames
    except Exception as e:
        print(f"Lỗi khi đọc sheet names từ Excel: {str(e)}")
        return []


def extract_hyperlinks_from_excel(file_bytes, market=None):
    """
    Trích xuất links từ Excel file.
    Nếu market=None: lấy tất cả sheets với thông tin market
    Nếu market được chỉ định: chỉ lấy từ sheet đó
    """
    try:
        wb = openpyxl.load_workbook(BytesIO(file_bytes))
        links_info = []
        
        # Xác định các sheets cần xử lý
        if market:
            # Nếu chỉ định market, chỉ xử lý sheet đó
            sheets_to_process = [(market, wb[market])] if market in wb.sheetnames else []
        else:
            # Nếu không chỉ định, xử lý tất cả sheets
            sheets_to_process = [(sheet_name, wb[sheet_name]) for sheet_name in wb.sheetnames]
        
        for sheet_name, ws in sheets_to_process:
            for col_idx in [1, 2, 3]:
                for row_idx in range(1, ws.max_row + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)

                    if cell.hyperlink and cell.hyperlink.target:
                        link = cell.hyperlink.target
                        is_valid = is_booking_link(link)
                        links_info.append({
                            'row': row_idx,
                            'col': chr(64 + col_idx),
                            'link': link.strip(),
                            'cell_value': str(cell.value) if cell.value else '',
                            'is_valid': is_valid,
                            'market': sheet_name,
                            'note': '' if is_valid else '⚠️Link không hợp lệ'
                        })

                    elif cell.value:
                        cell_text = str(cell.value).strip()
                        if 'http' in cell_text.lower() or 'www.' in cell_text.lower():
                            is_valid = is_booking_link(cell_text)
                            links_info.append({
                                'row': row_idx,
                                'col': chr(64 + col_idx),
                                'link': cell_text,
                                'cell_value': cell_text,
                                'is_valid': is_valid,
                                'market': sheet_name,
                                'note': '' if is_valid else '⚠️Link không hợp lệ'
                            })
        
        return links_info
    except Exception as e:
        print(f"Lỗi khi đọc hyperlink từ Excel: {str(e)}")
        return []


def find_booking_links(df):
    links_info = []
    
    for col_idx in [0, 1, 2]:
        if col_idx < len(df.columns):
            col_name = df.columns[col_idx]
            for row_idx, value in enumerate(df[col_name]):
                if pd.isna(value) or value is None:
                    continue
                    
                value_str = str(value).strip()

                if value_str.startswith('=HYPERLINK('):
                    match = re.search(r'=HYPERLINK\("([^"]+)"', value_str)
                    if match:
                        url = match.group(1)
                        is_valid = is_booking_link(url)
                        text_match = re.search(r',\s*"([^"]+)"\)', value_str)
                        display_text = text_match.group(1) if text_match else url
                        links_info.append({
                            'row': row_idx + 1,
                            'col': chr(65 + col_idx),
                            'link': url.strip(),
                            'cell_value': display_text,
                            'is_valid': is_valid,
                            'note': '' if is_valid else '⚠️Link không hợp lệ'
                        })

                elif 'http' in value_str.lower() or 'www.' in value_str.lower():
                    is_valid = is_booking_link(value_str)
                    links_info.append({
                        'row': row_idx + 1,
                        'col': chr(65 + col_idx),
                        'link': value_str,
                        'cell_value': value_str,
                        'is_valid': is_valid,
                        'note': '' if is_valid else '⚠️Link không hợp lệ'
                    })
    
    return links_info


def force_vnd_currency(url):

    try:
        parsed = urlparse(str(url))
        query = parse_qs(parsed.query)
        query['selected_currency'] = ['VND']
        query['lang'] = ['vi']
        new_query = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
    except Exception:
        return url


def load_google_sheet(url):
    try:
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            return None, None, "URL Google Sheets không hợp lệ"
        
        spreadsheet_id = match.group(1)

        gid_match = re.search(r'[#&]gid=([0-9]+)', url)
        gid = gid_match.group(1) if gid_match else '0'

        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
        csv_response = requests.get(csv_url, timeout=10)
        csv_response.raise_for_status()
        df = pd.read_csv(StringIO(csv_response.text), header=None)

        links_info = []

        try:
            html_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=html&gid={gid}"
            html_response = requests.get(html_url, timeout=10)
            
            if html_response.status_code == 200:
                soup = BeautifulSoup(html_response.content, 'lxml')

                for row_idx, tr in enumerate(soup.find_all('tr'), 1):
                    cells = tr.find_all('td')
                    for col_idx in range(min(3, len(cells))):
                        cell = cells[col_idx]

                        link_tag = cell.find('a', href=True)
                        if link_tag:
                            href = link_tag.get('href')
                            is_valid = is_booking_link(href)
                            links_info.append({
                                'row': row_idx,
                                'col': chr(65 + col_idx),
                                'link': href.strip(),
                                'cell_value': link_tag.get_text(strip=True),
                                'is_valid': is_valid,
                                'note': '' if is_valid else '⚠️Link không hợp lệ'
                            })
                        else:
                            cell_text = cell.get_text(strip=True)
                            if 'http' in cell_text.lower() or 'www.' in cell_text.lower():
                                is_valid = is_booking_link(cell_text)
                                links_info.append({
                                    'row': row_idx,
                                    'col': chr(65 + col_idx),
                                    'link': cell_text,
                                    'cell_value': cell_text,
                                    'is_valid': is_valid,
                                    'note': '' if is_valid else '⚠️Link không hợp lệ'
                                })
            else:
                pubhtml_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/pubhtml?gid={gid}"
                html_response = requests.get(pubhtml_url, timeout=10)
                
                if html_response.status_code == 200:
                    soup = BeautifulSoup(html_response.content, 'lxml')
                    
                    for row_idx, tr in enumerate(soup.find_all('tr'), 1):
                        cells = tr.find_all('td')
                        for col_idx in range(min(3, len(cells))):
                            cell = cells[col_idx]
                            
                            link_tag = cell.find('a', href=True)
                            if link_tag:
                                href = link_tag.get('href')
                                is_valid = is_booking_link(href)
                                links_info.append({
                                    'row': row_idx,
                                    'col': chr(65 + col_idx),
                                    'link': href.strip(),
                                    'cell_value': link_tag.get_text(strip=True),
                                    'is_valid': is_valid,
                                    'note': '' if is_valid else '⚠️Link không hợp lệ'
                                })
                            else:
                                cell_text = cell.get_text(strip=True)
                                if 'http' in cell_text.lower() or 'www.' in cell_text.lower():
                                    is_valid = is_booking_link(cell_text)
                                    links_info.append({
                                        'row': row_idx,
                                        'col': chr(65 + col_idx),
                                        'link': cell_text,
                                        'cell_value': cell_text,
                                        'is_valid': is_valid,
                                        'note': '' if is_valid else '⚠️Link không hợp lệ'
                                    })
        except Exception as e:
            print(f"HTML extraction error: {e}")

        if not links_info:
            for col_idx in [0, 1, 2]:
                if col_idx < len(df.columns):
                    col_name = df.columns[col_idx]
                    for row_idx, value in enumerate(df[col_name]):
                        if pd.notna(value):
                            value_str = str(value).strip()
                            if 'http' in value_str.lower() or 'www.' in value_str.lower():
                                is_valid = is_booking_link(value_str)
                                links_info.append({
                                    'row': row_idx + 1,
                                    'col': chr(65 + col_idx),
                                    'link': value_str,
                                    'cell_value': value_str,
                                    'is_valid': is_valid,
                                    'note': '' if is_valid else '⚠️Link không hợp lệ'
                                })
        
        return df, links_info, None
    except Exception as e:
        return None, None, f"Lỗi khi tải Google Sheets: {str(e)}"


def check_date_outdated(url):
    try:
        checkin_match = re.search(r'checkin=(\d{4}-\d{2}-\d{2})', url)
        checkout_match = re.search(r'checkout=(\d{4}-\d{2}-\d{2})', url)
        
        if checkin_match and checkout_match:
            checkin_date = datetime.strptime(checkin_match.group(1), '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout_match.group(1), '%Y-%m-%d')
            today = datetime.now().date()
            
            if checkin_date.date() < today or checkout_date.date() < today:
                return True, f"Ngày checkin ({checkin_match.group(1)}) hoặc checkout ({checkout_match.group(1)}) đã qua"
        
        return False, None
    except Exception as e:
        return False, None


def scrape_booking_data(url):
    if not SELENIUM_AVAILABLE:
        return None, "Selenium chưa được cài đặt. Vui lòng chạy: pip install selenium webdriver-manager"
    
    driver = None
    forced_url = force_vnd_currency(url)

    currency_code = 'VND'
    try:
        parsed = urlparse(forced_url)
        qs = parse_qs(parsed.query)
        if qs.get('selected_currency') and qs['selected_currency'][0].strip():
            currency_code = qs['selected_currency'][0].strip()
    except Exception:
        pass

    try:
        # Sử dụng hàm get_driver để hỗ trợ cả Docker (Chrome) và Local (Edge)
        driver = get_driver(is_headless=True) # Mặc định headless cho server

        
        driver.set_page_load_timeout(45)

        # Retry logic for page load (Phase 1: Immediate Retry)
        # Cơ chế thử lại ngay lập tức khi tải trang thất bại (Phase 1)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # print(f"Loading URL (Attempt {attempt+1}/{max_retries}): {forced_url}")
                driver.get(forced_url)
                
                # Check for successful load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.pp-header__title, h1, [data-testid="price-and-discounted-price"]'))
                )
                break # Success, exit retry loop
            except Exception as e:
                # print(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5) # Wait before retry
                # If last attempt fails, loop will finish and code proceeds below
                # potentially leading to empty result or further error which is caught by caller

        time.sleep(5)
        
        # Lưu HTML để debug
        try:
            page_source = driver.page_source
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Tạo thư mục debug_html trong backend
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            debug_dir = os.path.join(current_dir, 'debug_html')
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, f'booking_debug_{timestamp}.html')
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"Saved HTML to: {debug_path}")
        except Exception as e:
            print(f"⚠️ Could not save HTML: {e}")

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.pp-header__title, h1, [data-testid="price-and-discounted-price"]'))
            )
        except:
            pass
        
        time.sleep(3)
        
        result = {
            'hotel_name': None,
            'hotel_link': forced_url,
            'scrape_date': None,
            'popular_facilities': [],
            'rooms': [],
            'rating': None,
            'review_count': None
        }
        
        try:
            checkin_match = re.search(r'checkin=(\d{4}-\d{2}-\d{2})', url)
            checkout_match = re.search(r'checkout=(\d{4}-\d{2}-\d{2})', url)
            
            if checkin_match and checkout_match:
                checkin = checkin_match.group(1)
                checkout = checkout_match.group(1)
                result['scrape_date'] = f"{checkin} - {checkout}"
        except:
            pass
        
        if not result['scrape_date']:
            try:
                date_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="searchbox-dates-container"]')
                date_text = date_elem.text.strip()
                result['scrape_date'] = date_text
            except:
                try:
                    date_elem = driver.find_element(By.XPATH, '//*[contains(text(), "T7") or contains(text(), "CN")]')
                    date_text = date_elem.text.strip()
                    result['scrape_date'] = date_text
                except:
                    result['scrape_date'] = datetime.now().strftime('%Y-%m-%d')

        try:
            scripts = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.get_attribute('innerHTML'))
                    if isinstance(data, dict):
                        if 'name' in data and not result['hotel_name']:
                            result['hotel_name'] = data['name']
                        
                        if 'aggregateRating' in data:
                            rating_data = data['aggregateRating']
                            if 'ratingValue' in rating_data:
                                result['rating'] = str(rating_data['ratingValue'])
                            if 'reviewCount' in rating_data:
                                result['review_count'] = str(rating_data['reviewCount'])
                except Exception as e:
                    continue
        except Exception as e:
            pass

        if not result['hotel_name']:
            selectors = ['h2.pp-header__title', 'h1[data-testid="title"]', 'h1']
            for selector in selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and len(text) >= 3:
                        result['hotel_name'] = text
                        break
                except:
                    continue

        # Lấy Các tiện nghi được ưa chuộng nhất
        try:
            facility_wrapper = driver.find_element(By.CSS_SELECTOR, '[data-testid="property-most-popular-facilities-wrapper"]')
            facility_items = facility_wrapper.find_elements(By.CSS_SELECTOR, 'li span.f6b6d2a959')
            for item in facility_items:
                facility_text = item.text.strip()
                if facility_text:
                    result['popular_facilities'].append(facility_text)
        except Exception as e:
            pass

        try:
            room_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.js-rt-block-row')
            
            row_index = 0
            while row_index < len(room_rows):
                row = room_rows[row_index]
                
                try:
                    # Kiểm tra xem row có room type header không (có th.hprt-table-cell-roomtype)
                    room_type_cell = row.find_elements(By.CSS_SELECTOR, 'th.hprt-table-cell-roomtype')
                    
                    if room_type_cell:
                        # Row này có room type header, lấy thông tin chung
                        room_type_header = room_type_cell[0]
                        
                        # Lấy rowspan để biết có bao nhiêu pricing options
                        rowspan = 1
                        try:
                            rowspan_attr = room_type_header.get_attribute('rowspan')
                            if rowspan_attr:
                                rowspan = int(rowspan_attr)
                        except:
                            rowspan = 1
                        
                        # Lấy thông tin chung của room (room name, guests, bed, size)
                        room_common_data = {
                            'room_type': None,
                            'num_guests': None,
                            'bed_options': [],
                            'room_size': None,
                            'discount_percent': None
                        }
                        
                        # Lấy room name
                        try:
                            room_name_elem = room_type_header.find_element(By.CSS_SELECTOR, '.hprt-roomtype-link, .hprt-roomtype-icon-link')
                            room_common_data['room_type'] = room_name_elem.text.strip()
                        except:
                            pass
                        
                        # Lấy số lượng khách - ưu tiên tìm trong room_type_header trước
                        try:
                            num_guests_found = False
                            
                            # 1. Thử tìm text "Được giới thiệu cho X người" hoặc "Max people: X"
                            try:
                                # Tìm các thẻ h3, div, span có thể chứa thông tin này
                                candidates = room_type_header.find_elements(By.CSS_SELECTOR, '.e2e-gr-title, .hprt-occupancy-occupancy-info, .maxPersons-container, .c-occupancy-icons')
                                for cand in candidates:
                                    text = cand.get_attribute('textContent').strip()
                                    # Match "Được giới thiệu cho 2 người"
                                    match = re.search(r'(?:Được giới thiệu cho|Max people:|Số người tối đa:)\s*(\d+)', text, re.IGNORECASE)
                                    if match:
                                        room_common_data['num_guests'] = match.group(1)
                                        num_guests_found = True
                                        break
                            except:
                                pass

                            if not num_guests_found:
                                # 2. Count occupancy icons - selector: .c-occupancy-icons__adults i.bicon-occupancy
                                # Tìm trong cả row vì có thể icon nằm ở cell khác
                                occupancy_icons = row.find_elements(By.CSS_SELECTOR, '.c-occupancy-icons__adults i.bicon-occupancy')
                                if not occupancy_icons:
                                     occupancy_icons = row.find_elements(By.CSS_SELECTOR, '.c-occupancy-icons__adults .bicon.bicon-occupancy')
                                
                                if occupancy_icons:
                                    room_common_data['num_guests'] = str(len(occupancy_icons))
                                    num_guests_found = True

                            if not num_guests_found:
                                # 3. Fallback: parse from hidden text "Số người tối đa: X"
                                guests_elem = row.find_element(By.CSS_SELECTOR, '.bui-u-sr-only')
                                guests_text = guests_elem.text.strip()
                                num_match = re.search(r'Số người tối đa:\s*(\d+)', guests_text, re.IGNORECASE)
                                if not num_match:
                                    num_match = re.search(r'(\d+)\s*người', guests_text, re.IGNORECASE)
                                if num_match:
                                    room_common_data['num_guests'] = num_match.group(1)
                                    num_guests_found = True
                            
                            if not num_guests_found:
                                # 4. Another fallback specific to some layouts
                                occupancy = row.find_elements(By.CSS_SELECTOR, '.bui-icon.bui-icon--adults')
                                if occupancy:
                                    room_common_data['num_guests'] = str(len(occupancy))
                        except:
                            pass
                        
                        # Lấy thông tin giường
                        try:
                            bed_config_elems = room_type_header.find_elements(By.CSS_SELECTOR, '.hprt-roomtype-bed')
                            for bed_elem in bed_config_elems:
                                bed_text = bed_elem.text.strip()
                                if bed_text:
                                    lines = bed_text.split('\n')
                                    for line in lines:
                                        line = line.strip()
                                        if line and 'Chọn giường' not in line and 'tùy tình trạng' not in line:
                                            room_common_data['bed_options'].append(line)
                        except:
                            pass
                        
                        # Lấy diện tích phòng
                        try:
                            size_elem = room_type_header.find_element(By.CSS_SELECTOR, '.hprt-roomtype-icon-info .bui-u-sr-only')
                            size_text = size_elem.text.strip()
                            size_match = re.search(r'(\d+)\s*m', size_text)
                            if size_match:
                                room_common_data['room_size'] = size_match.group(1) + ' m²'
                        except:
                            try:
                                size_elem = room_type_header.find_element(By.XPATH, './/*[contains(text(), "m²") or contains(text(), "m2") or contains(text(), "feet²") or contains(text(), "ft²")]')
                                size_text = size_elem.text.strip()
                                size_match_m = re.search(r'(\d+)\s*m', size_text)
                                size_match_ft = re.search(r'(\d+)\s*(feet²|ft²)', size_text)
                                if size_match_m:
                                    room_common_data['room_size'] = size_match_m.group(1) + ' m²'
                                elif size_match_ft:
                                    room_common_data['room_size'] = size_match_ft.group(1) + ' ft²'
                            except:
                                pass
                        
                        # Bây giờ lấy thông tin pricing cho từng option (rowspan lần)
                        for option_idx in range(rowspan):
                            pricing_row = room_rows[row_index + option_idx]
                            
                            room_data = {
                                'room_type': room_common_data['room_type'],
                                'num_guests': room_common_data['num_guests'],
                                'bed_options': room_common_data['bed_options'].copy(),
                                'room_size': room_common_data['room_size'],
                                'facilities': [],
                                'price': None,
                                'price_original': None,
                                'discount_percent': None
                            }
                            
                            try:
                                # Lấy facilities từ pricing row
                                choice_elems = pricing_row.find_elements(By.CSS_SELECTOR, '.hprt-table-cell-conditions li')
                                for choice in choice_elems:
                                    choice_text = choice.text.strip()
                                    choice_text = re.sub(r'^[•\-–—]\s*', '', choice_text)
                                    choice_text = choice_text.strip()
                                    if choice_text:
                                        room_data['facilities'].append(choice_text)

                                if not room_data['facilities']:
                                    choice_elems = pricing_row.find_elements(By.CSS_SELECTOR, '.hprt-conditions li')
                                    for choice in choice_elems:
                                        choice_text = choice.text.strip()
                                        choice_text = re.sub(r'^[•\-–—]\s*', '', choice_text)
                                        choice_text = choice_text.strip()
                                        if choice_text:
                                            room_data['facilities'].append(choice_text)                    
                            except:
                                pass

                            # Lấy discount percentage (Tiết kiệm 51%)
                            try:
                                price_cell = pricing_row.find_element(By.CSS_SELECTOR, '.hprt-table-cell-price, [data-testid="price-and-discounted-price"]')
                                discount_text = price_cell.text
                                discount_match = re.search(r'Ti[ếe]t ki[ệe]m\s+\d+%', discount_text, re.IGNORECASE)
                                if discount_match:
                                    room_data['discount_percent'] = discount_match.group(0)
                            except:
                                pass

                            # Lấy giá
                            price_selectors = [
                                '.bui-price-display__value',
                                '[data-testid="price-and-discounted-price"] .prco-valign-middle-helper',
                                '.prco-inline-block-maker-helper',
                                '.bui_font_strong',
                                '.prco-text-color-bold',
                                'span[aria-hidden="true"]'
                            ]
                            
                            for selector in price_selectors:
                                try:
                                    price_elem = pricing_row.find_element(By.CSS_SELECTOR, selector)
                                    price_text = price_elem.text.strip().replace('\n', ' ').replace('\xa0', ' ')
                                    if price_text and len(price_text) > 0:
                                        price_match = re.search(r'VND\s*([\d\.,]+)', price_text, re.I)
                                        if not price_match:
                                            price_match = re.search(r'([\d\.,]+)\s*VND', price_text, re.I)
                                        if not price_match:
                                            price_match = re.search(r'([\d\.,]+)', price_text)
                                        if price_match:
                                            value = price_match.group(1).replace(',', '.')
                                            room_data['price'] = f"{value} {currency_code}".strip()
                                            break
                                except:
                                    continue

                            if not room_data['price']:
                                try:
                                    per_night_elem = pricing_row.find_element(By.CSS_SELECTOR, '.js-average-per-night-price')
                                    raw_val = per_night_elem.get_attribute('data-price-per-night-raw') or per_night_elem.text
                                    if raw_val:
                                        raw_val = str(raw_val).strip()
                                        number_match = re.search(r'([\d\.,]+)', raw_val)
                                        if number_match:
                                            value = number_match.group(1).replace(',', '.')
                                            room_data['price'] = f"{value} {currency_code}".strip()
                                except:
                                    pass

                            # Lấy giá gốc
                            original_price_selectors = [
                                '.bui-price-display__original',
                                '.bui-price-display__strikethrough',
                                '[data-testid="price-and-discounted-price"] .bui-price-display__strikethrough',
                                '.prco-text-stack s'
                            ]
                            
                            for selector in original_price_selectors:
                                try:
                                    original_price = pricing_row.find_element(By.CSS_SELECTOR, selector)
                                    orig_text = original_price.text.strip().replace('\n', ' ').replace('\xa0', ' ')
                                    if orig_text and len(orig_text) > 0:
                                        orig_match = re.search(r'VND\s*([\d\.,]+)', orig_text, re.I)
                                        if not orig_match:
                                            orig_match = re.search(r'([\d\.,]+)\s*VND', orig_text, re.I)
                                        if not orig_match:
                                            orig_match = re.search(r'([\d\.,]+)', orig_text)
                                        if orig_match:
                                            value = orig_match.group(1).replace(',', '.')
                                            room_data['price_original'] = f"{value} {currency_code}".strip()
                                            break
                                except:
                                    continue

                            if not room_data['price_original']:
                                try:
                                    orig_elem = pricing_row.find_element(By.CSS_SELECTOR, '.js-strikethrough-price')
                                    raw_orig = orig_elem.get_attribute('data-strikethrough-value') or orig_elem.text
                                    if raw_orig:
                                        raw_orig = str(raw_orig).strip()
                                        number_match = re.search(r'([\d\.,]+)', raw_orig)
                                        if number_match:
                                            value = number_match.group(1).replace(',', '.')
                                            room_data['price_original'] = f"{value} {currency_code}".strip()
                                except:
                                    pass

                            # Thêm room data vào result
                            if room_data['room_type'] and room_data['price']:
                                result['rooms'].append(room_data)
                        
                        # Tăng row_index để skip các pricing rows đã xử lý
                        row_index += rowspan
                    else:
                        # Row này không có room type header -> bỏ qua (đã được xử lý trong rowspan loop trước đó)
                        row_index += 1
                        
                except Exception as e:
                    row_index += 1
                    continue
        except Exception as e:
            pass
        
        return result, None
        
    except Exception as e:
        return None, f"Lỗi: {str(e)}"
        
    finally:
        if driver:
            driver.quit()
        try:
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
