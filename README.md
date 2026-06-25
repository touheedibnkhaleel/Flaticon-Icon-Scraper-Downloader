# Flaticon Icon Scraper & Downloader

A full data pipeline built in Python that scrapes, stores, 
and downloads 10,000+ icons from Flaticon concurrently.

---

## Project Structure

flaticon/
├── main.py          # Scraper — collects icon data
├── downloader.py    # Downloader — downloads images concurrently  
├── db.py            # Database — manages all SQLite operations
├── images/          # Downloaded images stored here
└── scraper.db       # SQLite database

---

## Features

### Scraping
- Uses Playwright to navigate Flaticon pages
- Extracts icon titles and image URLs
- Detects and skips duplicate images using MD5 hashing
- Handles pagination automatically via next button

### Database
- SQLite database with two tables
- ICONS — stores title, image URL, local path, downloaded status, failed status
- PROGRESS — tracks current scraping page for resume support

### Resume Tracking
- Saves progress after every completed page
- On restart automatically resumes from last completed page
- Clears progress when scraping finishes completely
- Never re scrapes already completed pages

### Concurrent Downloading
- Downloads multiple images simultaneously using ThreadPoolExecutor
- Each thread creates its own SQLite connection — thread safe
- Configurable worker count (default 5)
- Rate limiting with delays between requests

### Retry Logic
- Retries failed downloads up to 3 times
- Waits 2 seconds between retries
- Permanently marks images as failed after 3 unsuccessful attempts
- Failed images are skipped on future runs

### Progress Reporting
- Shows completed/total count after every download
- Tracks elapsed time and calculates ETA
- Reports failed count separately
- Thread safe counter using Lock

---

## Setup

### Requirements
- Python 3.8+
- Playwright
- Requests

### Installation

# Clone the repository
git clone https://github.com/yourusername/flaticon-scraper

# Navigate to project folder
cd flaticon-scraper

# Install dependencies
pip install playwright requests

# Install Playwright browsers
playwright install chromium

---

## Usage

### Step 1 — Scrape icon data
python3 main.py

### Step 2 — Download images
python3 downloader.py

Run them independently — scraper collects data, 
downloader processes it.

---

## How It Works

### Pipeline Flow
Flaticon Website
      ↓
  main.py (Playwright scraper)
      ↓
  scraper.db (SQLite database)
      ↓
  downloader.py (Concurrent downloader)
      ↓
  images/ folder

### Resume Logic
After each page completes → save page number to PROGRESS table
On restart → read PROGRESS table → skip to saved page
On completion → clear PROGRESS table

### Threading Architecture
Main thread → reads database → passes work to ThreadPoolExecutor
Worker threads → each creates own SQLite connection
Lock → protects shared counters from race conditions

---

## Key Challenges Solved

### SQLite Thread Safety
SQLite connections cannot be shared across threads.
Solution: each worker thread creates its own local connection.

### Resume Tracking
Scraper losing progress on crash was unacceptable.
Solution: tiny PROGRESS table saves state after every page.

### Concurrent Downloads
Sequential downloading of 10,000 images was too slow.
Solution: ThreadPoolExecutor with 5 workers reduced time by 70%.

---

## What I Learned
- Building a real multi-script pipeline from scratch
- SQLite thread safety and connection management
- Concurrent programming with ThreadPoolExecutor
- Resume tracking and fault tolerant system design
- Retry logic and graceful failure handling

---

## Author
Touheed
Building real projects to learn faster than any course
