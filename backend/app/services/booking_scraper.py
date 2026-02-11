import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from io import BytesIO, StringIO
import time
import openpyxl
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def is_booking_link(text):
    if pd.isna(text) or text is None:
        return False
    text_str = str(text).strip()
    return 'booking.com/hotel/' in text_str


def extract_hyperlinks_from_excel(file_bytes):
    try:
        wb = openpyxl.load_workbook(BytesIO(file_bytes))
        ws = wb.active
        links_info = []

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
    
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp(prefix='selenium_booking_')
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--lang=vi-VN')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f'--user-data-dir={temp_dir}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0')
    
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
        try:
            service = Service()
        except:
            service = Service()
        
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.get(forced_url)

        time.sleep(5)
        
        try:
            page_source = driver.page_source
            with open('/tmp/booking_booking_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
        except:
            pass

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

        try:
            room_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.js-rt-block-row')
            
            for row in room_rows:
                try:
                    room_data = {
                        'room_type': None,
                        'price': None,
                        'price_original': None,
                        'num_guests': None,
                        'bed_options': [],
                        'room_size': None,
                        'facilities': []
                    }

                    try:
                        room_name = row.find_element(By.CSS_SELECTOR, '.hprt-roomtype-icon-link')
                        room_data['room_type'] = room_name.text.strip()
                    except:
                        try:
                            room_name = row.find_element(By.CSS_SELECTOR, '.hprt-roomtype-link')
                            room_data['room_type'] = room_name.text.strip()
                        except:
                            try:
                                room_cell = row.find_element(By.CSS_SELECTOR, 'th.hprt-table-cell-roomtype, .hprt-roomtype-name')
                                text = room_cell.text.strip()
                                if text:
                                    room_data['room_type'] = text
                                else:
                                    continue
                            except:
                                continue
                    
                    try:
                        num_guests_elem = row.find_element(By.CSS_SELECTOR, '.bui-u-sr-only')
                        guests_text = num_guests_elem.text.strip()
                        guests_match = re.search(r'(\d+)', guests_text)
                        if guests_match:
                            room_data['num_guests'] = guests_match.group(1)
                    except:
                        try:
                            occupancy = row.find_elements(By.CSS_SELECTOR, '.bui-icon.bui-icon--adults')
                            if occupancy:
                                room_data['num_guests'] = str(len(occupancy))
                        except:
                            pass
                    
                    try:
                        bed_config_elems = row.find_elements(By.CSS_SELECTOR, '.hprt-roomtype-bed')
                        for bed_elem in bed_config_elems:
                            bed_text = bed_elem.text.strip()
                            if bed_text:
                                lines = bed_text.split('\n')
                                for line in lines:
                                    line = line.strip()
                                    if line and 'Chọn giường' not in line and 'tùy tình trạng' not in line:
                                        room_data['bed_options'].append(line)
                    except:
                        pass
                    
                    try:
                        size_elem = row.find_element(By.CSS_SELECTOR, '.hprt-roomtype-icon-info .bui-u-sr-only')
                        size_text = size_elem.text.strip()
                        size_match = re.search(r'(\d+)\s*m', size_text)
                        if size_match:
                            room_data['room_size'] = size_match.group(1) + ' m²'
                    except:
                        try:
                            size_elem = row.find_element(By.XPATH, './/*[contains(text(), "m²") or contains(text(), "m2") or contains(text(), "feet²") or contains(text(), "ft²")]')
                            size_text = size_elem.text.strip()

                            size_match_m = re.search(r'(\d+)\s*m', size_text)
                            size_match_ft = re.search(r'(\d+)\s*(feet²|ft²)', size_text)

                            if size_match_m:
                                room_data['room_size'] = size_match_m.group(1) + ' m²'
                            elif size_match_ft:
                                room_data['room_size'] = size_match_ft.group(1) + ' ft²'
                        except:
                            pass
                    
                    try:
                        choice_elems = row.find_elements(By.CSS_SELECTOR, '.hprt-table-cell-conditions li')
                        for choice in choice_elems:
                            choice_text = choice.text.strip()
                            choice_text = re.sub(r'^[•\-–—]\s*', '', choice_text)
                            choice_text = choice_text.strip()
                            if choice_text:
                                room_data['facilities'].append(choice_text)

                        if not room_data['facilities']:
                            choice_elems = row.find_elements(By.CSS_SELECTOR, '.hprt-conditions li')
                            for choice in choice_elems:
                                choice_text = choice.text.strip()
                                choice_text = re.sub(r'^[•\-–—]\s*', '', choice_text)
                                choice_text = choice_text.strip()
                                if choice_text:
                                    room_data['facilities'].append(choice_text)
                    except:
                        pass

                    try:
                        price_elem = row.find_element(By.CSS_SELECTOR, '.bui-price-display__value')
                        price_text = price_elem.text.strip().replace('\n', ' ').replace('\xa0', ' ')

                        price_match = re.search(r'VND\s*([\d\.,]+)', price_text, re.I)
                        if not price_match:
                            price_match = re.search(r'([\d\.,]+)\s*VND', price_text, re.I)

                        if not price_match:
                            price_match = re.search(r'([\d\.,]+)', price_text)

                        if price_match:
                            value = price_match.group(1).replace(',', '.')
                            room_data['price'] = f"{value} {currency_code}".strip()
                    except:
                        pass

                    if not room_data['price']:
                        try:
                            per_night_elem = row.find_element(By.CSS_SELECTOR, '.js-average-per-night-price')
                            raw_val = per_night_elem.get_attribute('data-price-per-night-raw') or per_night_elem.text
                            if raw_val:
                                raw_val = str(raw_val).strip()
                                number_match = re.search(r'([\d\.,]+)', raw_val)
                                if number_match:
                                    value = number_match.group(1).replace(',', '.')
                                    room_data['price'] = f"{value} {currency_code}".strip()
                        except:
                            pass

                    try:
                        original_price = row.find_element(By.CSS_SELECTOR, '.bui-price-display__original')
                        orig_text = original_price.text.strip().replace('\n', ' ').replace('\xa0', ' ')

                        orig_match = re.search(r'VND\s*([\d\.,]+)', orig_text, re.I)
                        if not orig_match:
                            orig_match = re.search(r'([\d\.,]+)\s*VND', orig_text, re.I)

                        if not orig_match:
                            orig_match = re.search(r'([\d\.,]+)', orig_text)

                        if orig_match:
                            value = orig_match.group(1).replace(',', '.')
                            room_data['price_original'] = f"{value} {currency_code}".strip()
                    except:
                        pass

                    if not room_data['price_original']:
                        try:
                            orig_elem = row.find_element(By.CSS_SELECTOR, '.js-strikethrough-price')
                            raw_orig = orig_elem.get_attribute('data-strikethrough-value') or orig_elem.text
                            if raw_orig:
                                raw_orig = str(raw_orig).strip()
                                number_match = re.search(r'([\d\.,]+)', raw_orig)
                                if number_match:
                                    value = number_match.group(1).replace(',', '.')
                                    room_data['price_original'] = f"{value} {currency_code}".strip()
                        except:
                            pass

                    if room_data['room_type'] and room_data['price']:
                        result['rooms'].append(room_data)

                except Exception as e:
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
