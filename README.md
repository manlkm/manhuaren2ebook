# manhuaren2ebook

[简体中文](README.zh-CN.md)


This is a Python script that downloads all chapters of a specified comic from manhuaren.com and converts each chapter into a separate EPUB e-book.

## Features

-   Automatically fetches all chapter links from a given comic's main page.
-   Simulates browser behavior to scrape manga images page by page for each chapter.
-   Packages the downloaded images into individual EPUB files, convenient for reading on e-readers.

## How to Use

### 1. Environment Setup

First, ensure you have Python 3 installed on your system.

**Create and activate a virtual environment (recommended):**

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

# Activate the virtual environment (Windows)
.\venv\Scripts\activate
```

### 2. Install Dependencies

After activating the virtual environment, use pip to install the required libraries:

```bash
pip install -r requirements.txt
```

### 3. Run the Script

Run the script by providing the URL of the comic's main page as a command-line argument.

**Syntax:**

```bash
python comic2ebook.py <URL_of_comic_main_page>
```

**Example:**

```bash
python comic2ebook.py https://www.manhuaren.com/manhua-some-comic-name/
```

## Disclaimer

This tool is for personal learning and research purposes only. The downloaded content is copyrighted by the respective publishers and authors. Please do not distribute the downloaded files. Please respect the copyright of the original content and support the official publishers.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The script will automatically perform the following operations:

1.  Create a folder named `comic_images` in the project root directory for temporarily storing downloaded images.
2.  Fetch all chapters and start downloading from the first one.
3.  Generate a corresponding `.epub` file in the project root directory after each chapter is downloaded.
4.  Exit automatically after all chapters have been processed.

## Notes

-   The script relies on `webdriver-manager` to automatically manage ChromeDriver, so an internet connection is required.
-   Download speed depends on your network conditions and the website server's response time.
-   The generated `.epub` files can be managed or converted to other formats (such as mobi) using tools like [Calibre](https://calibre-ebook.com/).
-   Please respect copyright. This tool is for learning and personal collection purposes only.
