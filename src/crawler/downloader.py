import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm
import time
from src.utils.logger import Logger
from src.config.config import Config


class PixivDownloader:
    """Download illustrations from Pixiv"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = Logger()
        self.session = requests.Session()
        self._setup_session()
        self.output_dir = Path(config.get('download.output_dir', './downloads'))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _setup_session(self):
        """Setup requests session with headers and proxies"""
        headers = {
            'User-Agent': self.config.get('headers.user_agent', ''),
            'Referer': 'https://www.pixiv.net',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
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

    def download_illustrations(self, illustrations: List[Dict]) -> Dict[str, int]:
        """
        Download illustrations

        Args:
            illustrations: List of illustration dictionaries

        Returns:
            Dictionary containing download statistics
        """
        stats = {
            'total': len(illustrations),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        for illust in tqdm(illustrations, desc="Downloading illustrations"):
            try:
                result = self.download_single_illustration(illust)
                if result == 'success':
                    stats['success'] += 1
                elif result == 'skipped':
                    stats['skipped'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                self.logger.error(f"Error downloading illustration {illust.get('id')}: {e}")
                stats['failed'] += 1

        return stats

    def download_single_illustration(self, illust: Dict) -> str:
        """
        Download a single illustration

        Args:
            illust: Illustration dictionary

        Returns:
            'success', 'failed', or 'skipped'
        """
        illust_id = illust.get('id')
        title = illust.get('title', 'unknown').replace('/', '_').replace('\\', '_').replace(':', '_')
        page_count = illust.get('page_count', 1)
        urls = illust.get('original_urls', [])

        if not urls:
            self.logger.warning(f"No image URLs found for illustration {illust_id}")
            return 'failed'

        # Download directly to output_dir without creating subdirectories
        success_count = 0

        for idx, url in enumerate(urls[:page_count]):
            try:
                # Use title as filename (with page number for multi-page illustrations)
                if page_count > 1:
                    filename = f"{title}_p{idx}.jpg"
                else:
                    filename = f"{title}.jpg"

                file_path = self.output_dir / filename

                # Skip if file already exists
                if file_path.exists():
                    self.logger.info(f"File already exists: {filename}")
                    success_count += 1
                    continue

                # Download image
                response = self.session.get(
                    url,
                    timeout=self.config.get('download.timeout', 30),
                    stream=True
                )
                response.raise_for_status()

                # Write file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                self.logger.info(f"Downloaded: {filename}")
                success_count += 1
                time.sleep(self.config.get('download.delay', 1.0))

            except Exception as e:
                self.logger.warning(f"Failed to download image {idx + 1} of illustration {illust_id}: {e}")

        if success_count == 0:
            return 'failed'
        elif success_count < page_count:
            return 'failed'
        else:
            self.logger.info(f"Successfully downloaded illustration {illust_id}: {title}")
            return 'success'

    def close(self):
        """Close the session"""
        self.session.close()
