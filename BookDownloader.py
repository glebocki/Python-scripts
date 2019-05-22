import glob
import wget
import requests
import time
import os
from parsel import Selector

LOCAL_DESTINATION_PATH = 'C:\\Users\\glebo\\OneDrive\\Dokumenty\\CodeBooks\\'


class BookDownloader:
    """
    Crawling and downloading books from links.
    Goes to main page then opena a link to books page then clicks download button
    """
    WEB_SITE_ADDRESS = 'https://goalkicker.com/'

    def __init__(self, dest_dir_url):
        self.dest_dir_url = dest_dir_url

    def start(self):
        self.delete_tmp_downloads()
        href_links = BookDownloader.get_all_book_links()
        self.__crawl_sub_pages(href_links)

    def __crawl_sub_pages(self, href_links):
        for link in href_links:
            # TODO: Low level operation: abstract it
            sub_page_link = BookDownloader.WEB_SITE_ADDRESS + link
            self.__crawl_to_sub_page(sub_page_link)

    @staticmethod
    def get_all_book_links():
        """
        Gets all links from main page to subpages with books
        """
        response = requests.get(BookDownloader.WEB_SITE_ADDRESS)
        selector = Selector(response.text)
        href_links = selector.xpath('//a/@href').getall()
        return href_links

    def __crawl_to_sub_page(self, sub_link):
        try:
            self.crawl_sub_page(sub_link)
        except Exception as exp:
            print('Error navigating to link : ', sub_link, ': ', exp)

    def __crawl_sub_page(self, sub_link):
        response = requests.get(sub_link)
        if 200 == response.status_code:
            file_name = BookDownloader.get_download_file_name(response)
            # TODO: Low level operations: abstract them
            src_url = sub_link + file_name
            destination_url = self.dest_dir_url + file_name
            self.__check_and_download(src_url, destination_url)

    def __check_and_download(self, src_url, destination_url):
        print("Downloading " + src_url + " to: " + destination_url)
        if self.is_downloaded(destination_url):
            print("File already downloaded!")
            return
        self.download(src_url, destination_url)

    @staticmethod
    def is_downloaded(destination_url) -> bool:
        return os.path.isfile(destination_url)

    @staticmethod
    def download(src_url, destination_url):
        wget.download(src_url, destination_url)

    @staticmethod
    def get_download_file_name(response):
        selector = Selector(response.text)
        file_name = selector.xpath('//*[@id="footer"]/button/@onclick').get()
        file_name = file_name.replace('location.href=', "").replace("\'", "")
        return file_name

    def delete_tmp_downloads(self):
        tmp_file_list = glob.glob(self.dest_dir_url + '*.tmp')
        for path in tmp_file_list:
            BookDownloader.delete_tmp_download(path)

    @staticmethod
    def delete_tmp_download(path):
        try:
            os.remove(path)
        except OSError as e:
            print("Error while deleting file : ", path + " : " + e)


start = time.time()

downloader = BookDownloader(LOCAL_DESTINATION_PATH)
downloader.start()

end = time.time()
print("Time taken in seconds : ", (end - start))
