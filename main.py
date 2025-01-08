#!/usr/bin/env python
from bot import DownloadBot
from downloader import VideoDownloader, JellyfinClient
from config import Config

def main():
    config = Config()
    downloader = VideoDownloader(config)
    jellyfin = JellyfinClient(config)
    bot = DownloadBot(config, downloader, jellyfin)
    bot.run()

if __name__ == "__main__":
    main()