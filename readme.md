
# Web Scraping: Selenium and Raw Fetching

## Selenium Implementation

The current implementation using Selenium is slow and unreliable. The website being scraped uses a lot of jQuery and AJAX calls, which complicates the scraping process. Selenium waits for the entire page and all AJAX requests to finish loading, but sometimes the load never completes properly, causing issues.

- Selenium implementation is slow and sometimes breaks.
- **Cause**: The website uses a lot of jQuery and AJAX, and Selenium waits for everything to load, but the process often doesn't finish properly.
- **Problem**: When the page fails to load fully, Selenium either hangs, bricks, or fails to scrape anything.

## Raw Fetching (API-like)

The **raw fetching** method is more similar to API data fetching. Instead of loading the website, we directly interact with the server by sending requests to the **`.php` URLs** used by the site's backend, which are revealed through the website's jQuery and AJAX implementations. This allows us to get the exact data we want without rendering the webpage.

 **masterDataFetcher.py** is the final form of the code while the other file in the rawFetching dirictory are localy contained states how the project grew. That just gives you schedules.bd that is the hole program for the simerter in liteSQL looks like that:
 ```sql
      CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT,
        spec TEXT,
        group_name TEXT,
        title TEXT,
        start TEXT,
        end TEXT,
        room TEXT,
        teacher TEXT,
        type TEXT,
        group_s TEXT,
        des TEXT
    )
  ```

- Way faster than Selenium since it bypasses the need to load the entire page.
- Works 99% of the time.
- Scrapes all the data in 4-5 seconds by directly fetching data through the site's backend `.php` URLs.

However, there are still situations where manual adjustments are required:

- **Manual intervention**: Sometimes, the request parameters sent to the server need manual adjustment to get the correct response.
```py
    start_date = "2024-10-21T00:00:00+03:00" 
    end_date = "2024-10-26T00:00:00+03:00" 
```
---
