import glob
from mutagen.mp4 import MP4
import logging
from time import sleep
import tkinter as tk
from tkinter import filedialog
from scraper import ScrapThwiki

tag_name = {
    "name": "\xa9nam",
    "album": "\xa9alb",
    "lyrics": '\xa9lyr'
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    if file_path == "":
        logging.info("Folder search cancelled")
        exit(0)
    scrapers = [ScrapThwiki()]
    for file in glob.iglob(file_path + '/**/*.m4a', recursive=True):
        logging.info(f"Processing file {file}")
        audio = MP4(file)
        # check if lyrics already exist
        if tag_name["lyrics"] in audio:
            logging.info(f"{file} already have lyrics, skipping it.")
            continue
        try:
            song_name = audio[tag_name["name"]][0]
            album_name = audio[tag_name["album"]][0]
        except IndexError:
            logging.error(f"{file} have no name/album in MP4 tag")
            continue
        sleep(1)
        for scraper in scrapers:
            scraper_lyrics = scraper.scrap(album_name, song_name)
            if scraper_lyrics is not None:
                audio[tag_name["lyrics"]] = scraper_lyrics
                logging.info(f"lyrics found for {file}, saving it.")
                audio.save()
                break


