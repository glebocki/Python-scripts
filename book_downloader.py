#!/usr/bin/env python3

"""
https://goalkicker.com/ Book Downloader

Idea: Coworker send me a link to a web-page with many tech books. To download
one I had to open each sub-page separately and click 'Download' button.

Solution: Automate this with a simple web-crawler and learn some Python along
the way.

Algorithm: Crawler goes to main page aggregates links to sub-pages then visits
every one and click a Download button there. There is a checker to not download
books multiple times. Also deletes tmp download files.
"""

from __future__ import print_function

import time
import os
import glob
import wget
import requests
from parsel import Selector

class BookDownloader(object):
    """
    Crawling and downloading books from links.
    Goes to main page then opena a link to books page then clicks download button
    """
    WEB_SITE_ADDRESS = 'https://goalkicker.com/'

    def __init__(self, dst_dir_url):
        self.dst_dir_url = dst_dir_url

    def start(self):
        """Start Downloading Books
        Before download if local dir does not exists creates it
        and if there were any *.tmp files removes them
        """
        self.__before_download()
        self.__download_books()

    def __before_download(self):
        if not os.path.exists(self.dst_dir_url):
            os.makedirs(self.dst_dir_url)
        else:
            self.delete_tmp_downloads()

    def __download_books(self):
        href_links = self.__get_all_books_links()
        self.__crawl_sub_pages(href_links)

    def __get_all_books_links(self):
        """
        Gets all links from main page to subpages with books
        """
        response = requests.get(self.WEB_SITE_ADDRESS)
        selector = Selector(response.text)
        href_links = selector.xpath('//a/@href').getall()
        return href_links

    def __crawl_sub_pages(self, href_links):
        for link in href_links:
            # FIXME: Low level operation: abstract it
            sub_page_link = BookDownloader.WEB_SITE_ADDRESS + link
            self.__crawl_to_sub_page(sub_page_link)

    def __crawl_to_sub_page(self, sub_link):
        try:
            self.__crawl_sub_page(sub_link)
        except Exception as exp:
            print('Error navigating to link: {0} : {1}'.format(sub_link, exp))

    def __crawl_sub_page(self, sub_link):
        response = requests.get(sub_link)
        if response.status_code == 200:
            file_name = self.__get_download_file_name(response)
            # FIXME: Low level operations: abstract them
            src_url = sub_link + file_name
            destination_url = self.dst_dir_url + file_name
            self.__check_and_download(src_url, destination_url)

    def __get_download_file_name(self, response):
        selector = Selector(response.text)
        file_name = selector.xpath('//*[@id="footer"]/button/@onclick').get()
        file_name = file_name.replace('location.href=', "").replace("\'", "")
        return file_name

    def __check_and_download(self, src_url, destination_url):
        print("Downloading {0} to {1}".format(src_url, destination_url))
        if self.__is_downloaded(destination_url):
            print("File already downloaded!")
            return
        self.__download(src_url, destination_url)

    def __is_downloaded(self, destination_url):
        return os.path.isfile(destination_url)

    def __download(self, src_url, destination_url):
        wget.download(src_url, destination_url)

    def delete_tmp_downloads(self):
        """Deletes */tmp files from local destination folder
        """
        tmp_file_list = glob.glob(self.dst_dir_url + '*.tmp')
        for path in tmp_file_list:
            self.__delete_tmp_download(path)

    def __delete_tmp_download(self, path):
        try:
            os.remove(path)
        except OSError as os_error:
            print("Error while deleting file: {0} : {1}".format(path, os_error))

def main():
    """Main entry point
    """
    downloader = BookDownloader('CodeBooks/')
    start = time.time()
    downloader.start()
    end = time.time()
    print("Time taken in seconds : ", (end - start))

main()
