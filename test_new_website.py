# coding: utf8
import os
import re
from typing import List
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging

from statistics import Stats
from transform import Import, Export, Update, Create

logging.basicConfig(filename='info.log', encoding='utf-8',
                    level=logging.INFO,
                    format=u'%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )


class WebsiteArchive:
    data_dict = {
        "Title": [],
        "URL": [],
        "Source": [],
        "Type": [],
        "DateTime": [],
        "Article": [],
        "Location": [],
        "Keywords1": [],
        "Keywords2": [], }

    def __init__(self, name, base_url, media_type, start_url, section_class, title_class, title_tag, article_class,
                 article_tag,
                 datetime_tag, website_type, datetime_format):
        self.name = name
        self.base_url = base_url
        self.media_type = media_type
        self.protocol = "https://" if base_url.__contains__("https://") else "http://"
        self.start_url = start_url
        self.section_class = section_class
        self.title_class = title_class
        self.title_tag = title_tag
        self.article_class = article_class
        self.article_tag = article_tag
        self.datetime_tag = datetime_tag
        self.website_type = website_type
        self._media_archive_dict = None
        self.found_duplicate = False
        self.interruption = False
        self.datetime_format = datetime_format

    def crawling_through_pages(self) -> dict:

        page = 1

        while True:
            logging.info(f"\tFor media {self.name} ({self.media_type}) searching in page {self.start_url}{page}\t"
                         f"The number of found articles is: {len(WebsiteArchive.data_dict['Title'])}")
            print(page, len(WebsiteArchive.data_dict["Title"]))
            logging.info(f"Info: {self.name, self.media_type}\nCurrent page is {page}")
            source = requests.get(self.start_url + str(page))

            if page == 5:
                break

            # source
            source_text = source.text
            soup = BeautifulSoup(source_text, 'lxml')

            main_section = soup.find(class_=self.section_class)  # TODO
            if self.title_class != "a":
                articles_section = main_section.find_all(class_=self.title_class)  # TODO
            else:
                articles_section = main_section.find_all(self.title_class)

            # articles_section = main_section.find_all(class_=self.title_class)

            for i in range(len(articles_section)):
                element = articles_section[i]
                print("The LEN of the section is: ", len(articles_section))

                # THE ARTICLE
                article_title = element.find(class_=self.title_tag).text  # TODO article_title = element.get(self.title_tag)
                # article_title = element.get(self.title_tag)
                article_title = article_title.replace("\n", "").strip()
                print("Title:", article_title)

                # THE URL
                if self.title_class != 'a':
                    link = element.a['href']
                else:
                    link = element.get('href')

                    # link = element.a['href']  # TODO
                if not link.startswith(self.base_url):
                    valid_link = self.base_url + link
                else:
                    valid_link = link
                article_url = valid_link
                print("URL:", article_url)

                # Using the article link, get the rest of the data
                article_source = requests.get(article_url)

                # THE ARTICLE TEXT
                a_source = requests.get(article_url)
                source_text = a_source.text
                article_soup = BeautifulSoup(source_text, 'lxml')

                article_text_scope = article_soup.find(class_=self.article_class)  # TODO

                article_text = " ".join(a.getText().replace('\xa0', " ").strip() for a in article_text_scope.findAll(self.article_tag))  # TODO
                print("Text:", article_text)

                # THE DATE
                datetime_scope = article_soup.find(class_=self.datetime_tag)

                article_datetime = datetime_scope.getText().replace(" ч.", "").replace(" г.", "").replace("\n",
                                                                                                          "").strip()
                print("Date:", article_datetime)

                # THE DICTIONARY
                WebsiteArchive.data_dict["Title"].append(article_title)
                WebsiteArchive.data_dict["URL"].append(article_url)
                WebsiteArchive.data_dict["Source"].append(self.name)
                WebsiteArchive.data_dict["Type"].append(self.media_type)
                WebsiteArchive.data_dict["Article"].append(article_text)
                WebsiteArchive.data_dict["DateTime"].append(article_datetime)
                # break
            page += 1

        data_dict = WebsiteArchive.data_dict

        return data_dict


def __repr__(self):
    return f"""
    Media name is: {self.name} >>>
    """


btv = WebsiteArchive("btvnovinite.bg",
                     "https://btvnovinite.bg",
                     "TV news",
                     "https://btvnovinite.bg/bulgaria/?page=",
                     "section-listing news-articles-inline",
                     "news-article-inline", "title",
                     "article-body", "p",
                     "date-time",
                     "WebsiteArchive",
                     '%H:%M %d.%m.%Y')

btv_news_dict = btv.crawling_through_pages()
print(btv_news_dict.values())

bnt = WebsiteArchive("bntnews.bg",
                     "https://bntnews.bg",
                     "TV news",
                     "https://bntnews.bg/bg/c/bulgaria?page=",
                     "news-wrap-view", # "left-wrap padd-r my-activity"     "news-wrap-view"
                     "a", "img-title",
                     "txt-news", "p",
                     "news-time",
                     "WebsiteArchive",
                     '%H:%M, %d.%m.%Y')  # 18:33, 02.05.2023

bnt_news_dict = bnt.crawling_through_pages()
print(bnt_news_dict.values())

nova = WebsiteArchive("nova.bg",
                      "https://nova.bg",
                      "TV news",
                      "https://nova.bg/news/category/2/%D0%B1%D1%8A%D0%BB%D0%B3%D0%B0%D1%80%D0%B8%D1%8F/",
                      "col-lg-12 col-md-12 col-sm-12 col-xs-12 category-list-wrapper",
                      "thumb-box", "title",
                      "col-lg-12 col-md-12 col-sm-12 col-xs-12 article-body io-article-body", "p",  #
                      "date-time",
                      "WebsiteArchive",
                      '%H:%M %d.%m.%Y')  # 04 май 2023  17:38

nova_news_dict = nova.crawling_through_pages()
print(nova_news_dict.values())
