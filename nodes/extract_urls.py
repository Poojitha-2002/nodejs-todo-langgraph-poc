# import os
# from urllib.parse import urljoin, urlparse
# from lxml import html
# import requests

# def extract_internal_hrefs(source_code, base_url, current_path):
#     """
#     Extracts internal links from anchor tags and normalizes them.
#     """
#     try:
#         tree = html.fromstring(source_code, base_url=urljoin(base_url, current_path))
#         link_elements = tree.xpath('//a[@href]')
#     except Exception:
#         return []

#     internal_links = set()
#     for el in link_elements:
#         raw_href = el.get('href', '').strip()
#         if not raw_href:
#             continue
#         absolute_url = urljoin(base_url, raw_href)
#         parsed = urlparse(absolute_url)
#         base_netloc = urlparse(base_url).netloc

#         # Same domain, path starts with /, and is not the current path
#         if parsed.netloc == base_netloc and parsed.path.startswith('/') and parsed.path != current_path:
#             internal_links.add(parsed.path)

#     return list(internal_links)


# def get_page_source(full_url):
#     """
#     Returns the HTML source of a page, or None if inaccessible.
#     """
#     try:
#         response = requests.get(full_url, timeout=5)
#         response.raise_for_status()
#         return response.text
#     except requests.RequestException:
#         return None


# def crawl_app_links(base_url):
#     """
#     Crawls a web app starting from the base URL and returns unique internal paths.
#     Skips inaccessible or crashing pages to prevent breaking the app.
#     """
#     visited = set()
#     all_links = set(['/'])  # Start from root path
#     queue = ['/']

#     while queue:
#         current_path = queue.pop(0)
#         if current_path in visited:
#             continue

#         full_url = urljoin(base_url, current_path)
#         source_code = get_page_source(full_url)

#         if source_code is None:
#             visited.add(current_path)
#             continue

#         links = extract_internal_hrefs(source_code, base_url, current_path)
#         for link in links:
#             if link not in visited and link not in queue:
#                 queue.append(link)
#                 all_links.add(link)

#         visited.add(current_path)

#     return sorted(all_links)



# from playwright.sync_api import sync_playwright
# from urllib.parse import urljoin, urlparse
# import os

# def crawl_app_links(start_url, email=None, password=None, login_url=None, max_depth=2):
#     visited = set()
#     to_visit = [(start_url, 0)]
#     base_netloc = urlparse(start_url).netloc

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         context = browser.new_context()
#         page = context.new_page()

#         # Optional login step
#         if login_url and email and password:
#             try:
#                 page.goto(login_url, timeout=10000)
#                 page.fill('input[type="email"]', email)
#                 page.fill('input[type="password"]', password)
#                 page.click('input[type="submit"]')
#                 page.wait_for_load_state("networkidle", timeout=10000)
#             except Exception as e:
#                 print(f"⚠️ Login failed: {e}")
#                 browser.close()
#                 return []

#         while to_visit:
#             current_url, depth = to_visit.pop(0)
#             if current_url in visited or depth > max_depth:
#                 continue

#             try:
#                 page.goto(current_url, timeout=10000)
#                 visited.add(current_url)
#                 print(f"✅ Visited: {current_url}")
#                 anchors = page.query_selector_all("a[href]")
#                 for a in anchors:
#                     href = a.get_attribute("href")
#                     if not href:
#                         continue
#                     full_url = urljoin(current_url, href)
#                     parsed = urlparse(full_url)
#                     if parsed.netloc == base_netloc and full_url not in visited:
#                         to_visit.append((full_url, depth + 1))
#             except Exception as e:
#                 print(f"❌ Skipping {current_url} due to error: {e}")
#                 continue

#         browser.close()

#     return sorted(visited)

from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def extract_internal_links_from_page(page, base_url, current_path):
    """
    Uses Playwright to extract internal anchor tag hrefs from the current page.
    """
    internal_links = set()
    elements = page.query_selector_all('a[href]')

    for el in elements:
        raw_href = el.get_attribute('href')
        if not raw_href:
            continue

        absolute_url = urljoin(base_url, raw_href)
        parsed = urlparse(absolute_url)
        base_netloc = urlparse(base_url).netloc

        if parsed.netloc == base_netloc and parsed.path.startswith('/') and parsed.path != current_path:
            internal_links.add(parsed.path)

    return list(internal_links)


def crawl_app_links(base_url):
    """
    Crawls internal links using Playwright, skipping inaccessible pages.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        visited = set()
        all_links = set(['/'])  # Start from root
        queue = ['/']

        while queue:
            current_path = queue.pop(0)
            if current_path in visited:
                continue

            full_url = urljoin(base_url, current_path)
            try:
                page.goto(full_url, timeout=5000, wait_until="load")
            except PlaywrightTimeoutError:
                print(f"❌ Timeout while loading {full_url}, skipping.")
                visited.add(current_path)
                continue
            except Exception as e:
                print(f"❌ Error visiting {full_url}: {e}")
                visited.add(current_path)
                continue

            try:
                links = extract_internal_links_from_page(page, base_url, current_path)
            except Exception as e:
                print(f"⚠️ Failed to extract links from {full_url}: {e}")
                visited.add(current_path)
                continue

            for link in links:
                if link not in visited and link not in queue:
                    queue.append(link)
                    all_links.add(link)

            visited.add(current_path)

        browser.close()
        return sorted(all_links)


app_link = 'http://localhost:4000'

links = crawl_app_links(app_link)

for link in links:
    print(link)