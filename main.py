#!/usr/bin/env python3
"""
Pixiv Illustration Crawler
A simple command-line tool to search and download illustrations from Pixiv
"""

import argparse
import sys
import os
from pathlib import Path

from config import Config
from crawler import PixivAPI, PixivDownloader
from utils import Logger


def setup_argparse() -> argparse.ArgumentParser:
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description='Pixiv Illustration Crawler - Search and download illustrations from Pixiv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search and download illustrations
  python main.py search "anime girl" --max-pages 5

  # Search with custom output directory
  python main.py search "landscape" --output ./my_downloads

  # Get monthly ranking illustrations
  python main.py ranking --mode monthly --date 20251128

  # Get daily ranking (current date)
  python main.py ranking --mode daily

  # Generate default config file
  python main.py config --generate
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search and download illustrations')
    search_parser.add_argument('keyword', help='Search keyword')
    search_parser.add_argument('--max-pages', type=int, default=10, help='Maximum pages to search (default: 10)')
    search_parser.add_argument('--output', default='./downloads', help='Output directory (default: ./downloads)')
    search_parser.add_argument('--order', default='date_d', help='Sort order: date_d, popular_d (default: date_d)')

    # Ranking command
    ranking_parser = subparsers.add_parser('ranking', help='Download from Pixiv ranking')
    ranking_parser.add_argument('--mode', default='monthly', help='Ranking mode: daily, weekly, monthly, etc. (default: monthly)')
    ranking_parser.add_argument('--date', default=None, help='Date in YYYYMMDD format (default: current date)')
    ranking_parser.add_argument('--output', default='./downloads', help='Output directory (default: ./downloads)')

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--generate', action='store_true', help='Generate default config file')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')

    return parser


def cmd_search(args, config: Config):
    """Execute search command"""
    logger = Logger()

    try:
        # Update output directory if specified
        if args.output != './downloads':
            config.set('download.output_dir', args.output)

        # Create API instance
        api = PixivAPI(config)

        logger.info(f"Searching for '{args.keyword}' with max {args.max_pages} pages...")
        illustrations = api.search(
            keyword=args.keyword,
            max_pages=args.max_pages,
            order=args.order
        )
        api.close()

        if not illustrations:
            logger.warning("No illustrations found")
            return

        logger.info(f"Found {len(illustrations)} illustrations")

        # Download illustrations
        downloader = PixivDownloader(config)
        logger.info("Starting download...")
        stats = downloader.download_illustrations(illustrations)
        downloader.close()

        # Print statistics
        print("\n" + "="*50)
        print("Download Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Success: {stats['success']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Output directory: {config.get('download.output_dir')}")
        print("="*50)

    except KeyboardInterrupt:
        logger.warning("Download interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during search and download: {e}")
        sys.exit(1)


def cmd_ranking(args, config: Config):
    """Execute ranking command"""
    logger = Logger()

    try:
        # Update output directory if specified
        if args.output != './downloads':
            config.set('download.output_dir', args.output)

        # Create API instance
        api = PixivAPI(config)

        logger.info(f"Fetching {args.mode} ranking with date {args.date or 'current'}...")
        illustrations = api.ranking(mode=args.mode, date=args.date)
        api.close()

        if not illustrations:
            logger.warning("No illustrations found in ranking")
            return

        logger.info(f"Found {len(illustrations)} illustrations in ranking")

        # Download illustrations
        downloader = PixivDownloader(config)
        logger.info("Starting download...")
        stats = downloader.download_illustrations(illustrations)
        downloader.close()

        # Print statistics
        print("\n" + "="*50)
        print("Download Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Success: {stats['success']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Output directory: {config.get('download.output_dir')}")
        print("="*50)

    except KeyboardInterrupt:
        logger.warning("Download interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during ranking download: {e}")
        sys.exit(1)


def cmd_config(args, config: Config):
    """Execute config command"""
    logger = Logger()

    if args.generate:
        logger.info("Generating default config file...")
        config.save_config()
        logger.info("Config file generated: config.yaml")
    elif args.show:
        print("\nCurrent Configuration:")
        print("-" * 50)
        import yaml
        print(yaml.dump(config.config, allow_unicode=True, default_flow_style=False))
    else:
        print("Use --help to see config options")


def main():
    """Main entry point"""
    parser = setup_argparse()
    args = parser.parse_args()

    # Initialize configuration
    config = Config('config.yaml')
    logger = Logger()

    if args.command == 'search':
        cmd_search(args, config)
    elif args.command == 'ranking':
        cmd_ranking(args, config)
    elif args.command == 'config':
        cmd_config(args, config)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
