import os
import time
import requests
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
from ebooklib import epub

# Create a directory for images
img_dir = "comic_images"
os.makedirs(img_dir, exist_ok=True)

def get_chapter_links(master_url):
    """
    Get all chapter links from the main comic page.

    :param master_url: The URL of the main comic page.
    :return: A list of tuples containing (chapter_title, link).
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    chapter_links = []
    try:
        print(f"Accessing main comic page: {master_url}")
        driver.get(master_url)
        wait = WebDriverWait(driver, 20)

        # 1. Handle overlays and click the "Expand all chapters" button
        try:
            # Remove or hide the fixed bottom bar that might be obstructing
            try:
                bottom_bar = driver.find_element(By.CSS_SELECTOR, "div.detail-fix-bottom")
                driver.execute_script("arguments[0].style.display='none';", bottom_bar)
                print("Hid the bottom overlay bar.")
            except Exception:
                print("Bottom overlay bar not found, continuing.")

            expand_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "展开全部章节")))
            driver.execute_script("arguments[0].click();", expand_button) # Click using JS
            print("Clicked 'Expand all chapters' button via JS.")
            time.sleep(2) # Wait for the chapter list to fully expand
        except Exception as e:
            print(f"Could not find or click 'Expand all chapters' button: {e}")

        # 2. Wait for and get all chapter links
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.chapteritem")))
        link_elements = driver.find_elements(By.CSS_SELECTOR, "a.chapteritem")
        for element in link_elements:
            title = element.text
            href = element.get_attribute('href')
            if title and href:
                chapter_links.append((title, href))
        
        # 3. Reverse the chapter list in the code (ascending order)
        chapter_links.reverse()
        print(f"Successfully found {len(chapter_links)} chapters, sorted in ascending order.")
    except Exception as e:
        print(f"Error finding chapter links: {e}")
    finally:
        driver.quit()
        
    return chapter_links


def scrape_and_save_images(start_url, img_dir, max_retries=3):
    """
    Use Selenium browser automation to scrape and save images from each page of the comic.
    Download images immediately after getting the URL to avoid URL expiration.

    :param start_url: The URL of the first page of the comic.
    :param img_dir: The directory to store the images.
    :return: (driver instance, comic title)
    """
    # Clear the image directory
    if os.path.exists(img_dir):
        for f in os.listdir(img_dir):
            os.remove(os.path.join(img_dir, f))
    else:
        os.makedirs(img_dir, exist_ok=True)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print("Initializing session, visiting start page for the first time...")
    driver.get(start_url)
    time.sleep(3)
    print("Visiting start page again to bypass blocking...")
    driver.get(start_url)
    time.sleep(3)

    # Get and clean the title
    title = driver.title.replace("_在线漫画阅读_漫画人", "").strip()
    print(f"Comic title: {title}")

    retries = 0
    current_url = start_url

    while retries < max_retries:
        try:
            page_num = 1
            wait = WebDriverWait(driver, 20) # Increase wait time

            # Process the first page
            print(f"Processing page {page_num}...")
            main_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cp_img img")))
            img_src = main_image.get_attribute("src")
            
            # Download the image immediately
            img_path = os.path.join(img_dir, f"page_{page_num:03d}.jpg")
            try:
                cookies = driver.get_cookies()
                session = requests.Session()
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                response = session.get(img_src, headers={'Referer': driver.current_url})
                response.raise_for_status()
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {img_path}")
            except Exception as e:
                print(f"Failed to download {img_src} : {e}")

            while True:
                page_num += 1
                current_url = driver.current_url
                last_img_src = img_src
                print(f"Processing page {page_num} ({current_url})...")

                # Execute nextPage() JavaScript function to turn the page
                try:
                    driver.execute_script("nextPage();")
                except Exception as e:
                    print(f"Failed to execute nextPage(), may have reached the end: {e}")
                    return driver # Normal exit

                # Wait for the image src attribute to update
                try:
                    wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, "#cp_img img").get_attribute("src") != last_img_src)
                except Exception:
                    print("Page did not update within the expected time, may have reached the end.")
                    return driver, title # Normal exit

                # Get the new image
                main_image = driver.find_element(By.CSS_SELECTOR, "#cp_img img")
                img_src = main_image.get_attribute("src")

                # Download the image immediately
                img_path = os.path.join(img_dir, f"page_{page_num:03d}.jpg")
                try:
                    cookies = driver.get_cookies()
                    session = requests.Session()
                    for cookie in cookies:
                        session.cookies.set(cookie['name'], cookie['value'])
                    response = session.get(img_src, headers={'Referer': driver.current_url})
                    response.raise_for_status()
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {img_path}")
                except Exception as e:
                    print(f"Failed to download {img_src} : {e}")

        except NoSuchWindowException:
            retries += 1
            print(f"Browser window closed, attempting to reconnect... (Attempt {retries}/{max_retries})")
            if driver:
                driver.quit()
            
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print(f"Re-visiting page: {current_url}")
            driver.get(current_url)
            time.sleep(5) # Wait for page to load
        except Exception as e:
            print(f"An unknown error occurred: {e}")
            break

    print("Maximum number of retries reached, terminating program.")
    return driver, title



def imgs_to_epub(img_dir, book_title, epub_name):
    """
    Convert images in the specified directory to an EPUB format e-book.

    :param img_dir: The path to the directory containing the images.
    :param book_title: The title of the e-book.
    :param epub_name: The output EPUB filename.
    """
    book = epub.EpubBook()
    book.set_title(book_title)
    book.set_language('zh')
    spine = ['nav']
    for img_file in sorted(os.listdir(img_dir)):
        if not (img_file.endswith(".jpg") or img_file.endswith(".png")):
            continue
        img_path = os.path.join(img_dir, img_file)
        with open(img_path, 'rb') as f:
            img_content = f.read()
        img_item = epub.EpubImage()
        img_item.file_name = img_file
        img_item.media_type = 'image/jpeg' if img_file.endswith(".jpg") else 'image/png'
        img_item.content = img_content
        book.add_item(img_item)
        img_chapter = epub.EpubHtml(title=img_file, file_name=f"{img_file}.xhtml", lang='zh')
        img_chapter.content = f'<img src="{img_file}" alt="{img_file}"/>'
        book.add_item(img_chapter)
        spine.append(img_chapter)
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(epub_name, book)
    print(f"EPUB e-book created: {epub_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download comics from manhuaren.com and convert to EPUB.')
    parser.add_argument('master_url', type=str, help='The main URL of the comic to get all chapters.')
    args = parser.parse_args()

    # Get all chapter links from the main page
    chapters = get_chapter_links(args.master_url)

    if not chapters:
        print("Could not retrieve any chapter links, terminating program.")
    else:
        print(f"Preparing to download {len(chapters)} chapters...")
        for i, (chapter_title, chapter_url) in enumerate(chapters):
            print(f"\n--- Start processing chapter {i+1}/{len(chapters)}: {chapter_title} ---")
            
            # Download images for a single chapter
            # The scrape_and_save_images function handles browser startup and shutdown
            driver, title = scrape_and_save_images(chapter_url, img_dir)
            
            if driver:
                driver.quit()
                print("Browser closed for the current chapter.")

            # Check if any images were downloaded, then create the EPUB
            if any(fname.endswith('.jpg') for fname in os.listdir(img_dir)):
                # Use the title obtained from the page for more accurate naming
                epub_filename = f"{title}.epub"
                imgs_to_epub(img_dir, title, epub_filename)
                print(f"To convert to mobi, use Calibre: ebook-convert \"{epub_filename}\" \"{title}.mobi\"")
            else:
                print(f"No images downloaded for chapter '{title}', skipping EPUB creation.")
            
            # Take a short break to avoid overwhelming the server
            time.sleep(5)

        print("\nAll chapters processed!")
