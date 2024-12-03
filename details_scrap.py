import os
import psycopg2
import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_images_from_link(url, image_save_path, base_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        images = []
        
        # Pobierz zdjęcia z meta tagów
        meta_images = soup.find_all('meta', property='og:image')
        for meta_img in meta_images:
            src = meta_img.get('content')
            if src:
                images.append(src)
                print(f"Znaleziono obraz: {src}")

        if not images:
            print(f"Brak obrazów w meta tagach dla URL: {url}")

        photo_paths = []
        for idx, img_url in enumerate(images):
            img_response = requests.get(img_url, headers=headers)
            if img_response.status_code == 200:
                content_type = img_response.headers.get('content-type')
                if 'image' in content_type:
                    ext = content_type.split('/')[-1]
                    img_name = f"{base_name}_{idx:08d}.{ext}"
                    img_path = os.path.join(image_save_path, img_name)
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    photo_paths.append(img_path)
                    print(f"Pobrano i zapisano obraz: {img_path}")
                else:
                    print(f"Niepoprawny typ treści dla obrazu: {content_type}")
            else:
                print(f"Nie udało się pobrać obrazu: {img_url}")
        return ', '.join(photo_paths)
    except Exception as e:
        print(f"Błąd przy pobieraniu obrazów z URL {url}: {e}")
        return None

def fetch_data_from_link(url, image_save_path):
    try:
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        def get_text(selector):
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else None

        def download_photos():
            elements = soup.select('.image-gallery-image')
            print(f"Found {len(elements)} images in {url}")
            photo_paths = []
            for img in elements:
                if 'src' in img.attrs:
                    img_url = img['src']
                    img_response = session.get(img_url, headers=headers, timeout=10)
                    if img_response.status_code == 200:
                        img_name = os.path.basename(img_url.split(';')[0])
                        img_path = os.path.join(image_save_path, img_name)
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                        photo_paths.append(img_path)
            return ', '.join(photo_paths)

        data = {
            'title': get_text('[data-cy="adPageAdTitle"]'),
            'price': get_text('[data-cy="adPageHeaderPrice"]'),
            'address': get_text('a[aria-label="Adres"]'),
            'price_per_m2': get_text('[aria-label="Cena za metr kwadratowy"]'),
            
            'area': get_text('div[data-testid="table-value-area"]'),
            'rooms': get_text('div[data-testid="table-value-rooms_num"] a'),
            'floor': get_text('div[data-testid="table-value-floor"]'),
            'virtual_tour': get_text('[data-cy="adPageVirtualTour"]'),
            'remote_service': get_text('[data-cy="adPageRemoteService"]'),
            'ownership_form': get_text('div[data-testid="table-value-building_ownership"]'),
            'finishing_status': get_text('[aria-label="Stan wykończenia"] button'),
            'balcony_garden_terrace': get_text('[aria-label="Balkon / ogród / taras"] button'),
            'parking_space': get_text('[aria-label="Miejsce parkingowe"] button'),
            'heating': get_text('div[data-testid="table-value-heating"]'),
            
            
            'market': get_text('div[data-testid="table-value-market"]'),
            'advertiser_type': get_text('div[data-testid="table-value-advertiser_type"]'),
            'available_from': get_text('div[data-testid="table-value-free_from"]'),
            'year_built': get_text('div[data-testid="table-value-build_year"]'),
            'building_type': get_text('div[data-testid="table-value-building_type"]'),
            'windows': get_text('div[data-testid="table-value-windows_type"]'),
            'elevator': get_text('div[data-testid="table-value-lift"]'),
            'media': get_text('div[data-testid="table-value-media_types"]'),
            'security': get_text('div[data-testid="table-value-security_types"]'),
            'equipment': get_text('div[data-testid="table-value-equipment_types"]'),
            'additional_info': get_text('div[data-testid="table-value-extras_types"]'),
            'building_material': get_text('div[data-testid="table-value-building_material"]'),
            'listing_date': get_text('[data-cy="adPageAdDescription"] p:nth-of-type(7)'),
            'advertiser_name': get_text('[data-cy="adPageAdDescription"] p:nth-of-type(6) strong'),
            'advertiser_phone': get_text('[data-cy="adPageAdDescription"] p:nth-of-type(8) strong'),
            'url': url,
            'description': get_text('[data-cy="adPageAdDescription"]'),
            'photos': download_photos()  # pobieranie zdjęć
        }

        # Validate and format listing_date
        try:
            data['listing_date'] = datetime.strptime(data['listing_date'], '%Y-%m-%d').date() if data['listing_date'] else None
        except (ValueError, TypeError):
            data['listing_date'] = None

        # Truncate strings to fit column length limits
        def truncate(value, max_length):
            return value[:max_length] if value and len(value) > max_length else value

        column_max_lengths = {
            'title': 255,
            'price': 50,
            'address': 255,
            'price_per_m2': 50,
            'area': 50,
            'rooms': 50,
            'floor': 50,
            'virtual_tour': 255,
            'remote_service': 255,
            'ownership_form': 50,
            'finishing_status': 50,
            'balcony_garden_terrace': 50,
            'parking_space': 50,
            'heating': 50,
            'market': 50,
            'advertiser_type': 50,
            'available_from': 50,
            'year_built': 50,
            'building_type': 50,
            'windows': 50,
            'elevator': 50,
            'media': 50,
            'security': 50,
            'equipment': 50,
            'additional_info': 255,
            'building_material': 50,
            'advertiser_name': 255,
            'advertiser_phone': 50,
            'url': 255,
            'description': 5000,
            'photos': 5000,
        }

        for key in column_max_lengths:
            data[key] = truncate(data[key], column_max_lengths[key])

        return data

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def process_listing(link_id, url, image_save_path, cursor, conn):
    print(f"Processing ID: {link_id}")
    data = fetch_data_from_link(url, image_save_path)
    if data:
        # Sprawdzenie, które dane należy zaktualizować
        columns_to_update = []
        values_to_update = []

        if data['title']:
            columns_to_update.append("title = %s")
            values_to_update.append(data['title'])
        if data['photos']:
            columns_to_update.append("photos = %s")
            values_to_update.append(data['photos'])

        # Dodanie pozostałych pól tylko jeśli są nowe lub zaktualizowane
        for key in ['price', 'address', 'price_per_m2', 'area', 'rooms', 'floor', 'virtual_tour', 'remote_service', 'ownership_form', 'finishing_status', 'balcony_garden_terrace', 'parking_space', 'heating', 'market', 'advertiser_type', 'available_from', 'year_built', 'building_type', 'windows', 'elevator', 'media', 'security', 'equipment', 'additional_info', 'building_material', 'listing_date', 'advertiser_name', 'advertiser_phone', 'url', 'description']:
            if data[key]:
                columns_to_update.append(f"{key} = %s")
                values_to_update.append(data[key])

        values_to_update.append(link_id)

        if columns_to_update:
            update_query = f"UPDATE listings SET {', '.join(columns_to_update)} WHERE id = %s"
            cursor.execute(update_query, tuple(values_to_update))
            conn.commit()
            print(f"Zaktualizowano rekord ID {link_id}")
        else:
            print(f"Brak danych do zaktualizowania dla ID {link_id}")
    else:
        print(f"Brak danych do zapisania dla ID {link_id}")

# Połączenie z bazą danych
conn = psycopg2.connect(
    dbname="ot_database",
    user="postgres",
    password="1@leK2345",
    host="localhost"
)
cursor = conn.cursor()

# Pobieranie linków do ogłoszeń, gdzie kolumna title lub photos jest pusta
cursor.execute("SELECT id, url FROM listings WHERE title IS NULL OR title = '' OR photos IS NULL OR photos = '' ORDER BY id ASC")
links = cursor.fetchall()

# Ustawienie ścieżki do zapisywania obrazów
image_save_path = 'images'
os.makedirs(image_save_path, exist_ok=True)

# Użycie ThreadPoolExecutor do równoległego przetwarzania
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_listing, link_id, url, image_save_path, cursor, conn) for link_id, url in links]
    for future in as_completed(futures):
        future.result()

cursor.close()
conn.close()
