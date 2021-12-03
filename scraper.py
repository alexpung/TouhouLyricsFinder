import requests
from bs4 import BeautifulSoup
from exception import ContentNotFoundError
import logging
from thefuzz import fuzz


class SongNameSimilarity(object):
    def __init__(self, song_name, token_set_ratio):
        self.song_name = song_name
        self.token_set_ratio = token_set_ratio


class Scraper(object):
    @staticmethod
    def request_soup(url: str):
        r = requests.get(url)
        if r.text and 200 <= r.status_code <= 299:
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        else:
            raise ContentNotFoundError(url, r.status_code)


class ScrapThwiki(Scraper):
    lrc_url = "https://cd.thwiki.cc/lyrics/"
    album_url = "https://thwiki.cc/"
    site_name = "thwiki"
    similarity_threshold = 80

    def scrap_lrc(self, song_name: str) -> str:
        """
        directly check if the lrc file exist with the song name
        :param song_name: name of the song
        :return: lyrics string if exist
        """
        url = self.lrc_url + song_name + ".lrc"
        try:
            lyrics = self.request_soup(url).string
        except ContentNotFoundError:
            logging.warning(f"Song {song_name} not found in lrc file in {self.site_name}")
            lyrics = None
        return lyrics

    def scrap_song_name(self, album_name: str, song_name: str) -> list[SongNameSimilarity]:
        """ searching song_name in album list to find similar name that is slightly mismatched
            e.g. missing punctuations, misspelling etc.
        :param album_name: album to search for
        :param song_name: name of the song
        :return: a list of song name in album with the fuzz token set ratio (more similar the name the higher the ratio)
        """
        url = self.album_url + album_name
        logging.info(f"Trying to search name with album name {album_name}")
        try:
            soup = self.request_soup(url)
        except ContentNotFoundError:
            logging.warning(f"Album {album_name} not found in {self.site_name}")
            return []
        similar_list = []
        # filter through html elements to get desired list of song names
        for track in soup.find_all("td", {"class": "title"}):
            search = track.find('a')
            if search is not None:
                new_name = search.get("title")
                # The [3:] at the end strip the 歌词: string that is unneeded
                if new_name is not None:
                    new_name = new_name[3:]
                    similar_list.append(SongNameSimilarity(new_name, fuzz.token_set_ratio(song_name, new_name)))
        return similar_list

    def scrap(self, album_name: str, song_name: str):
        lyrics = self.scrap_lrc(song_name)
        if lyrics is None:
            song_list = self.scrap_song_name(album_name, song_name)
            logging.debug(f"Matching song list is {sorted(song_list, key=lambda x: x[1], reverse=True)}")
            for candidate in sorted(song_list, key=lambda x: x[1], reverse=True):
                if candidate.token_set_ratio > self.similarity_threshold:
                    logging.info(f"Similar Name found, trying to search {self.site_name} "
                                 f"with {candidate.song_name} instead")
                    lyrics = self.scrap_lrc(candidate.song_name)
                    if lyrics is not None:
                        break
        # guard against lyrics not exist return
        if lyrics is None:
            logging.warning(f"No lyrics found at {self.site_name} for {song_name}")
            return None
        else:
            return lyrics

