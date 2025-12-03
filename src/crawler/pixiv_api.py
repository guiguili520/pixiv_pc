import requests
import re
import time
import json
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
from src.utils.logger import Logger
from src.config.config import Config
from bs4 import BeautifulSoup


class PixivAPI:
    """Pixiv API wrapper for searching and fetching illustrations"""

    BASE_URL = "https://www.pixiv.net"
    AJAX_URL = "https://www.pixiv.net/ajax"
    RANKING_URL = "https://www.pixiv.net/ranking.php"

    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Setup requests session with headers and proxies"""
        headers = {
            'User-Agent': self.config.get('headers.user_agent', ''),
            'Referer': self.BASE_URL,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session.headers.update(headers)

        # Setup proxy if enabled
        if self.config.get('proxy.enabled', False):
            http_proxy = self.config.get('proxy.http')
            https_proxy = self.config.get('proxy.https')
            if http_proxy or https_proxy:
                proxies = {}
                if http_proxy:
                    proxies['http'] = http_proxy
                if https_proxy:
                    proxies['https'] = https_proxy
                self.session.proxies.update(proxies)

    def search(self, keyword: str, max_pages: int = 10, order: str = 'date_d') -> List[Dict]:
        """
        Search illustrations by keyword

        Args:
            keyword: Search keyword
            max_pages: Maximum number of pages to fetch
            order: Order type (date_d: newest, popular_d: most popular, etc.)

        Returns:
            List of illustration data
        """
        illustrations = []
        retry_count = 0
        max_retries = self.config.get('download.retry_times', 3)

        for page in range(1, max_pages + 1):
            try:
                self.logger.info(f"Fetching search results - keyword: {keyword}, page: {page}")

                # Construct search URL
                url = f"{self.BASE_URL}/search/illustrations"
                params = {
                    's_mode': 's_tag_full',
                    'word': keyword,
                    'order': order,
                    'p': page,
                    'type': 'all'
                }

                response = self.session.get(url, params=params, timeout=self.config.get('download.timeout', 30))
                response.raise_for_status()

                # Extract illustration IDs from the response HTML
                illust_ids = self._extract_illust_ids(response.text)

                if not illust_ids:
                    self.logger.warning(f"No illustrations found on page {page}")
                    break

                # Fetch details for each illustration
                for illust_id in illust_ids:
                    try:
                        illust_data = self.get_illustration_details(illust_id)
                        if illust_data:
                            illustrations.append(illust_data)
                            time.sleep(self.config.get('download.delay', 1.0))
                    except Exception as e:
                        self.logger.warning(f"Failed to get details for illust_id {illust_id}: {e}")

                # Add delay between pages
                time.sleep(self.config.get('download.delay', 1.0) * 2)
                retry_count = 0  # Reset retry count on success

            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count < max_retries:
                    self.logger.warning(f"Request failed (retry {retry_count}/{max_retries}): {e}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch page {page} after {max_retries} retries: {e}")
                    break
            except Exception as e:
                self.logger.error(f"Unexpected error while fetching page {page}: {e}")
                break

        return illustrations

    def get_illustration_details(self, illust_id: int) -> Optional[Dict]:
        """
        Get detailed information about an illustration

        Args:
            illust_id: Pixiv illustration ID

        Returns:
            Dictionary containing illustration details
        """
        try:
            url = f"{self.AJAX_URL}/illusts/{illust_id}"
            response = self.session.get(url, timeout=self.config.get('download.timeout', 30))
            response.raise_for_status()

            data = response.json()

            if data.get('error'):
                self.logger.warning(f"API error for illust_id {illust_id}: {data.get('message')}")
                return None

            illust_data = data.get('body', {})

            # Extract important fields
            return {
                'id': illust_id,
                'title': illust_data.get('title', 'Unknown'),
                'artist': illust_data.get('userName', 'Unknown'),
                'artist_id': illust_data.get('userId', ''),
                'image_url': illust_data.get('urls', {}).get('original', ''),
                'page_count': illust_data.get('pageCount', 1),
                'like_count': illust_data.get('likeCount', 0),
                'comment_count': illust_data.get('commentCount', 0),
                'view_count': illust_data.get('viewCount', 0),
                'upload_date': illust_data.get('uploadDate', ''),
                'tags': [tag.get('tag', '') for tag in illust_data.get('tags', {}).get('tags', [])],
                'original_urls': self._get_all_image_urls(illust_id, illust_data.get('pageCount', 1))
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch details for illust_id {illust_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing illustration details: {e}")
            return None

    def _get_all_image_urls(self, illust_id: int, page_count: int) -> List[str]:
        """Get all image URLs for multi-page illustrations"""
        urls = []

        try:
            url = f"{self.AJAX_URL}/illusts/{illust_id}/pages"
            response = self.session.get(url, timeout=self.config.get('download.timeout', 30))
            response.raise_for_status()

            data = response.json()
            pages = data.get('body', [])

            for page in pages:
                img_urls = page.get('urls', {})
                original_url = img_urls.get('original', '')
                if original_url:
                    urls.append(original_url)

            return urls

        except Exception as e:
            self.logger.warning(f"Failed to fetch all image URLs for illust_id {illust_id}: {e}")
            return []

    def ranking(self, mode: str = 'monthly', date: Optional[str] = None) -> List[Dict]:
        """
        Get illustrations from Pixiv ranking by parsing HTML img URLs directly

        Args:
            mode: Ranking mode (daily, weekly, monthly, etc.)
            date: Date in format YYYYMMDD (e.g., '20251128' for Nov 28, 2025)
                  If None, uses current date

        Returns:
            List of illustration data with img URLs from ranking page
        """
        illustrations = []
        retry_count = 0
        max_retries = self.config.get('download.retry_times', 3)

        if not date:
            date = datetime.now().strftime('%Y%m%d')

        try:
            self.logger.info(f"Fetching ranking page - mode: {mode}, date: {date}")

            # Construct ranking URL
            params = {
                'mode': mode,
                'content': 'illust',
                'date': date
            }

            response = self.session.get(
                self.RANKING_URL,
                params=params,
                timeout=self.config.get('download.timeout', 30)
            )
            response.raise_for_status()

            # Extract illustration data directly from ranking page JSON
            illustrations = self._extract_ranking_illustrations(response.text)

            if not illustrations:
                self.logger.warning(f"No illustrations found in ranking")
                return []

            self.logger.info(f"Found {len(illustrations)} illustrations in ranking")
            retry_count = 0

        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count < max_retries:
                self.logger.warning(f"Request failed (retry {retry_count}/{max_retries}): {e}")
                time.sleep(2 ** retry_count)
            else:
                self.logger.error(f"Failed to fetch ranking after {max_retries} retries: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching ranking: {e}")

        return illustrations

    def _extract_illust_ids(self, html: str) -> List[int]:
        """Extract illustration IDs from search results HTML"""
        try:
            # Look for data-id attributes in image elements
            pattern = r'data-id="(\d+)"'
            ids = re.findall(pattern, html)
            return list(set(map(int, ids)))[:100]  # Limit to 100 unique IDs
        except Exception as e:
            self.logger.error(f"Error extracting illustration IDs: {e}")
            return []

    def _extract_ranking_illustrations(self, html: str) -> List[Dict]:
        """Extract illustration data from ranking page JSON"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Find JSON script tag
            script = soup.find('script', type='application/json')
            if not script:
                self.logger.warning("No JSON script tag found")
                return []

            # Parse JSON data
            json_data = json.loads(script.string)

            # Extract illustration data from JSON
            # Path: props > pageProps > assign > contents
            contents = (
                json_data.get('props', {})
                .get('pageProps', {})
                .get('assign', {})
                .get('contents', [])
            )

            self.logger.info(f"Found {len(contents)} illustrations in ranking JSON data")

            illustrations = []

            # Extract illustration data from contents
            for content in contents:
                try:
                    # Check if required fields exist
                    if 'url' not in content or 'pximg' not in content['url']:
                        continue

                    illust_data = {
                        'id': content.get('illust_id', 0),
                        'title': content.get('title', 'unknown'),
                        'artist': content.get('user_name', 'unknown'),
                        'artist_id': str(content.get('user_id', '')),
                        'image_url': content.get('url', ''),
                        'page_count': int(content.get('illust_page_count', 1)),
                        'like_count': content.get('rating_count', 0),
                        'comment_count': 0,
                        'view_count': content.get('view_count', 0),
                        'upload_date': content.get('date', ''),
                        'tags': content.get('tags', []),
                        'original_urls': [content.get('url', '')]
                    }
                    illustrations.append(illust_data)
                except Exception as e:
                    self.logger.warning(f"Failed to process ranking content: {e}")
                    continue

            self.logger.info(f"Extracted {len(illustrations)} illustrations from ranking page")
            return illustrations

        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON data: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error extracting ranking illustrations: {e}")
            return []

    def close(self):
        """Close the session"""
        self.session.close()
