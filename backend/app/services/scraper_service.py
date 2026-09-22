"""Scraper service — extracts product data from competitor marketplace URLs."""

import logging
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Common user-agent to avoid basic bot detection
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_SUPPORTED_DOMAINS = {
    "amazon.in": "amazon",
    "amazon.com": "amazon",
    "www.amazon.in": "amazon",
    "www.amazon.com": "amazon",
    "flipkart.com": "flipkart",
    "www.flipkart.com": "flipkart",
    "dl.flipkart.com": "flipkart",
    "meesho.com": "meesho",
    "www.meesho.com": "meesho",
}


class ScraperError(Exception):
    """Raised when scraping fails."""

    def __init__(self, message: str, url: str | None = None):
        self.url = url
        super().__init__(message)


class ScraperService:
    """Scrapes product details from marketplace URLs using httpx + BeautifulSoup."""

    def __init__(self, timeout: float = 15.0):
        self._timeout = timeout

    def detect_marketplace(self, url: str) -> str | None:
        """Detect which marketplace a URL belongs to."""
        try:
            parsed = urlparse(url)
            return _SUPPORTED_DOMAINS.get(parsed.hostname or "", None)
        except Exception:
            return None

    async def scrape_product_url(self, url: str) -> dict:
        """
        Fetch a product page and extract visible product information.

        Returns:
            dict with keys: source, source_url, title, description, bullet_points,
            specifications, price, mrp, images, raw_text
        """
        marketplace = self.detect_marketplace(url)
        if not marketplace:
            raise ScraperError(
                f"Unsupported URL. Only Amazon, Flipkart, and Meesho links are supported.",
                url=url,
            )

        try:
            html = await self._fetch_page(url)
        except Exception as e:
            raise ScraperError(f"Failed to fetch page: {str(e)}", url=url)

        soup = BeautifulSoup(html, "html.parser")

        # Remove script, style, and nav elements
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        if marketplace == "amazon":
            return self._parse_amazon(soup, url)
        elif marketplace == "flipkart":
            return self._parse_flipkart(soup, url)
        elif marketplace == "meesho":
            return self._parse_meesho(soup, url)
        else:
            return self._parse_generic(soup, url, marketplace)

    async def _fetch_page(self, url: str) -> str:
        """Fetch HTML content from URL."""
        headers = {
            "User-Agent": _USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
        }
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=self._timeout,
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

    def _parse_amazon(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract product data from Amazon product page."""
        data = {
            "source": "amazon",
            "source_url": url,
            "title": "",
            "description": "",
            "bullet_points": [],
            "specifications": {},
            "price": None,
            "mrp": None,
            "images": [],
            "raw_text": "",
        }

        # Title
        title_el = soup.find(id="productTitle")
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        # Bullet points (feature list)
        feature_list = soup.find(id="feature-bullets")
        if feature_list:
            items = feature_list.find_all("li")
            data["bullet_points"] = [item.get_text(strip=True) for item in items if item.get_text(strip=True)]

        # Description
        desc_el = soup.find(id="productDescription")
        if desc_el:
            data["description"] = desc_el.get_text(strip=True)

        # Price
        price_el = soup.find("span", class_="a-price-whole")
        if price_el:
            price_text = price_el.get_text(strip=True).replace(",", "").replace(".", "")
            try:
                data["price"] = float(price_text)
            except ValueError:
                pass

        # MRP
        mrp_el = soup.find("span", class_="a-price", attrs={"data-a-strike": "true"})
        if mrp_el:
            mrp_whole = mrp_el.find("span", class_="a-price-whole")
            if mrp_whole:
                mrp_text = mrp_whole.get_text(strip=True).replace(",", "").replace(".", "")
                try:
                    data["mrp"] = float(mrp_text)
                except ValueError:
                    pass

        # Technical specifications
        spec_tables = soup.find_all("table", class_="a-keyvalue")
        for table in spec_tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all(["th", "td"])
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    val = cols[1].get_text(strip=True)
                    if key and val:
                        data["specifications"][key] = val

        # Images (from thumbnails)
        img_els = soup.find_all("img", attrs={"data-old-hires": True})
        for img in img_els[:8]:
            src = img.get("data-old-hires", "")
            if src:
                data["images"].append(src)

        # Raw text fallback
        main_content = soup.find(id="dp-container") or soup.find("main") or soup.body
        if main_content:
            data["raw_text"] = main_content.get_text(separator="\n", strip=True)[:10000]

        return data

    def _parse_flipkart(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract product data from Flipkart product page."""
        data = {
            "source": "flipkart",
            "source_url": url,
            "title": "",
            "description": "",
            "bullet_points": [],
            "specifications": {},
            "price": None,
            "mrp": None,
            "images": [],
            "raw_text": "",
        }

        # Flipkart uses dynamic class names, so we use heuristics

        # Title — usually the first h1 or a span with a specific pattern
        h1_el = soup.find("h1")
        if h1_el:
            # Sometimes h1 contains nested spans
            data["title"] = h1_el.get_text(strip=True)

        # Try to find title via common Flipkart patterns
        if not data["title"]:
            title_span = soup.find("span", class_=re.compile(r"VU-ZEz|G6XhRU|B_NuCI"))
            if title_span:
                data["title"] = title_span.get_text(strip=True)

        # Bullet points / highlights
        highlight_divs = soup.find_all("li", class_=re.compile(r"_21Ahn-|col-12-12"))
        if highlight_divs:
            data["bullet_points"] = [
                li.get_text(strip=True)
                for li in highlight_divs
                if li.get_text(strip=True) and len(li.get_text(strip=True)) > 5
            ]

        # Description
        desc_div = soup.find("div", class_=re.compile(r"_1mXcCf|yN\\+eNk"))
        if desc_div:
            data["description"] = desc_div.get_text(strip=True)

        # Price — Flipkart usually has ₹ followed by price in a div
        price_div = soup.find("div", class_=re.compile(r"_30jeq3|Nx9bqj|_16Jk6d"))
        if price_div:
            price_text = price_div.get_text(strip=True)
            price_match = re.search(r"[\d,]+", price_text.replace("₹", ""))
            if price_match:
                try:
                    data["price"] = float(price_match.group().replace(",", ""))
                except ValueError:
                    pass

        # Specifications table
        spec_tables = soup.find_all("table", class_=re.compile(r"_14cfVK|_1ZWgtN|GGNn3G"))
        for table in spec_tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    val = cols[1].get_text(strip=True)
                    if key and val:
                        data["specifications"][key] = val

        # Images
        img_els = soup.find_all("img", class_=re.compile(r"_396cs4|DByuf4|_2r_T1I"))
        for img in img_els[:8]:
            src = img.get("src", "")
            if src and "rukminim" in src:
                # Convert thumbnail to high-res
                src = re.sub(r"/\d+/\d+/", "/832/832/", src)
                data["images"].append(src)

        # Raw text
        main_content = soup.find("div", class_=re.compile(r"_1AtVbE|col-12-12")) or soup.body
        if main_content:
            data["raw_text"] = main_content.get_text(separator="\n", strip=True)[:10000]

        return data

    def _parse_meesho(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract product data from Meesho product page."""
        data = {
            "source": "meesho",
            "source_url": url,
            "title": "",
            "description": "",
            "bullet_points": [],
            "specifications": {},
            "price": None,
            "mrp": None,
            "images": [],
            "raw_text": "",
        }

        # Meesho title
        h1_el = soup.find("h1")
        if h1_el:
            data["title"] = h1_el.get_text(strip=True)

        # Price
        price_spans = soup.find_all("h4")
        for span in price_spans:
            text = span.get_text(strip=True)
            if "₹" in text:
                match = re.search(r"[\d,]+", text.replace("₹", ""))
                if match:
                    try:
                        data["price"] = float(match.group().replace(",", ""))
                        break
                    except ValueError:
                        pass

        # Description / details
        detail_divs = soup.find_all("div", class_=re.compile(r"ProductDescription|DetailCard"))
        for div in detail_divs:
            text = div.get_text(strip=True)
            if text and len(text) > 20:
                data["description"] += text + "\n"

        # Specifications (key-value pairs)
        spec_rows = soup.find_all("div", class_=re.compile(r"SpecRow|DetailRow"))
        for row in spec_rows:
            texts = [t.get_text(strip=True) for t in row.find_all(["span", "p"]) if t.get_text(strip=True)]
            if len(texts) >= 2:
                data["specifications"][texts[0]] = texts[1]

        # Images
        img_els = soup.find_all("img", class_=re.compile(r"ProductImage|Carousel"))
        for img in img_els[:8]:
            src = img.get("src", "")
            if src and src.startswith("http"):
                data["images"].append(src)

        # Raw text
        main = soup.find("main") or soup.body
        if main:
            data["raw_text"] = main.get_text(separator="\n", strip=True)[:10000]

        return data

    def _parse_generic(self, soup: BeautifulSoup, url: str, marketplace: str) -> dict:
        """Fallback generic parser."""
        data = {
            "source": marketplace,
            "source_url": url,
            "title": "",
            "description": "",
            "bullet_points": [],
            "specifications": {},
            "price": None,
            "mrp": None,
            "images": [],
            "raw_text": "",
        }

        h1 = soup.find("h1")
        if h1:
            data["title"] = h1.get_text(strip=True)

        main = soup.find("main") or soup.body
        if main:
            data["raw_text"] = main.get_text(separator="\n", strip=True)[:10000]

        return data
