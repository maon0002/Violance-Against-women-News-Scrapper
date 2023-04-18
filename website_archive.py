# coding: utf8
import re
from typing import List
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging

from statistics import Stats
from transform import Import, Export, Update

logging.basicConfig(filename='debug.log', encoding='utf-8',
                    level=logging.INFO,
                    format=u'%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )


class BaseWebsite(ABC):
    _first_level_keywords = (
        ' жена', ' жени', 'съпруга', 'дъщеря', 'внучк', 'девойк', 'момиче', 'студентк', 'ученичк',
        'баба', 'домашното насилие', 'домашно насилие', 'годеница', 'приятелк', 'гимназистк',
        'майка', 'дъщери')
    _second_level_keywords = ('домашно насилие', 'уби', 'стрел', 'мушк', 'обезобраз', 'преби', 'наказан',
                              'изнасил', 'тормоз', 'насил', ' рани', ' стрел', 'сигнал', 'осъд', 'смърт',
                              'криминалн', 'намерен', ' полиц', 'насилван', 'запов', ' наран', ' почина')

    _data_dict = {
        "Title": [],
        "URL": [],
        "Source": [],
        "Type": [],
        "DateTime": [],
        "Article": [],
        "Location": [],
        "Keywords1": [],
        "Keywords2": [],
        # TODO to add first and second level keywords which were found in the article
        #  (two places where are the 'any' func)
    }
    _search_dict_village = Import("villages", "import/villages_list.csv").file_to_dictionary()
    _search_dict_city = Import("cities", "import/cities_list.csv").file_to_dictionary()

    def __init__(self, name, base_url, media_type):
        self.name = name
        self.base_url = base_url
        self.media_type = media_type

    @staticmethod
    def check_response_status(source: requests) -> bool:
        """
        The function returns either the url request is 200 or not
        :param source:
        :return: True / False
        """
        return source.status_code == 200

    @abstractmethod
    def crawling_through_pages(self):
        ...


class WebsiteArchive(BaseWebsite):

    def __init__(self, name, base_url, media_type, start_url, section_class, title_class, title_tag, article_class,
                 article_tag,
                 datetime_tag, website_type):
        super().__init__(name, base_url, media_type)
        self.protocol = "https://" if base_url.__contains__("https://") else "http://"
        self.start_url = start_url
        self.section_class = section_class
        self.title_class = title_class
        self.title_tag = title_tag
        self.article_class = article_class
        self.article_tag = article_tag
        self.datetime_tag = datetime_tag
        self.website_type = website_type
        self._media_archive_dict = Import.csv_to_dict(f'export/{self.name}_archive.csv')
        self.found_duplicate = False
        self.interruption = False

    # @staticmethod
    # def check_response_status(source: requests) -> bool:
    #     """
    #     The function returns either the url request is 200 or not
    #     :param source:
    #     :return: True / False
    #     """
    #     return source.status_code == 200

    def search_in_archive_csv_by_column_by_value(self, column, value):
        """
        Check if a particular value already existed in a particular column to exclude duplicated records
        in the media archive file and to abort the script
        :param column: one of the _data_dict keys
        :param value: related to _data_dict columns/keys
        :return: value if found else None
        """
        if value in self._media_archive_dict[column]:
            return value
        return None

    @staticmethod
    def check_if_keyword_in_string(text: str, keywords: tuple) -> [List[str], None]:
        """
        Uses the two tuples: _first_level_keywords, _second_level_keywords for filtering only the article titles and
        then the article texts which are in the scope of the project
        :param text: article_title or article_text
        :param keywords: the two tuples: _first_level_keywords, _second_level_keywords from the BaseWebsite class
        :return: either matched keywords or None
        """
        if any(substring in re.sub(
                r'[.|–,!?:„“;\-()"\\/{}\]\[`=]', ' ',
                " " + text.lower())
               for substring in keywords):
            return [word for word in keywords if word in text.lower()]
        else:
            return None

    def section_soup(self, source):
        """
        After inspecting and defining the html box/section with the news articles and urls
        (self.section_class and self.title_class given during the initialization) the function creates a bs4soup
        narrowing the search for needed article elements
        :param source:
        :return: section scope
        """
        source_text = source.text
        soup = BeautifulSoup(source_text, 'lxml')
        try:
            main_section = soup.find(class_=self.section_class)  # TODO make self.main_section
            section = main_section.find_all(class_=self.title_class)
        except AttributeError:
            logging.info(f"***Can't find the html section/box by self.section_class or self.title_class")
            return None
        return section

    def article_soup(self, url: str):
        """
        Creates a soup with the needed scope for extracting article_text, datetime, locations etc...
        :param url: the article
        :return: both the soup for the datetime extraction later and the text scope
        """
        source = requests.get(url)
        source_text = source.text
        soup = BeautifulSoup(source_text, 'lxml')
        try:
            text_scope = soup.find(class_=self.article_class)
        except AttributeError:
            logging.info(f"***Can't find text_scope searching in {url} soup")
            return None
        return [text_scope, soup]

    def get_article_title(self, element):
        """
        If some of the BaseWebsite._first_level_keywords matching word/words from the article title.
        The article and the article url will be further analyzed for the purpose of adding them in the _data_dict with
        the rest of the data

        :param element:
        :return: the title of the article and the matched words if any; else: None
        """
        try:
            article_title = element.find(class_=self.title_tag).text
        except AttributeError:
            logging.info(f"***Can't find article title")
            return None
        first_lvl_keyword = self.check_if_keyword_in_string(article_title, BaseWebsite._first_level_keywords)
        if first_lvl_keyword:
            return article_title, first_lvl_keyword
        return None

    def get_article_link(self, element):
        """
        Finds the article url and validates if the 'href' element is a standard formatted link (have 'https://' e.g)
        :param element:
        :return: validated/formatted link
        """
        link = element.a['href']
        if not link.startswith(self.base_url):
            valid_link = self.base_url + link
        else:
            valid_link = link

        return valid_link

    def get_article_text(self, scope):
        """
        Collects the article text parts via self.article_tag
        :param scope:
        :return: the article text
        """
        try:
            article_text = " ".join(a.getText().replace('\xa0', " ").strip() for a in scope.findAll(self.article_tag))
        except AttributeError:
            logging.info(f"***Can't find article text")
            return None
        return article_text

    def get_article_datetime_str(self, article_url):
        """
        Extracts the date and time when the article was publish/updated and remove some local formatting
        :param article_url:
        :return:
        """
        try:
            article_soup = self.article_soup(article_url)[1]
            datetime_scope = article_soup.find(class_=self.datetime_tag)
        except AttributeError:
            logging.info(f"***Issue with extracting datetime for url: {article_url}")
            return ""
        article_datetime = datetime_scope.getText().replace(" ч.", "").replace(" г.", "")
        return article_datetime

    @staticmethod
    def get_locations(article_text):
        """

        :param article_text:
        :return:
        """
        location = []
        [location.append(value) for value in BaseWebsite._search_dict_city.values() if
         value in article_text and value not in location]
        [location.append(value) for value in BaseWebsite._search_dict_village.values() if
         value in article_text and value not in location]
        return location if location else ""

    def add_data(self, source):
        """
        The main function of the script that controls the other
        :param source:
        :return:
        """
        try:
            articles_section = self.section_soup(source)

            for i in range(len(articles_section)):
                element = articles_section[i]
                if not self.get_article_title(element):
                    continue
                article_title, article_matched_first_scope_keywords = self.get_article_title(element)
                article_url = self.get_article_link(element)
                if not all([article_title, article_url]):
                    logging.info(f"*** Problem with extracting article_title or/and article_url")
                    continue

                # Check if the article URL already existed in the media archive .csv / if yes, break and stop the script
                # TODO : Problem - case with updated old articles will stop the script and
                #  will not scrape next articles!!
                #  (may be is better to use datetime as a criteria?)
                # Check if the article URL already existed
                # if self.search_in_archive_csv_by_column_by_value("URL", article_url) and \
                #         self.search_in_archive_csv_by_column_by_value("Title", article_title):
                #     logging.info(f"Article with title: <<< {article_title} >>> already existed "
                #                   f"within the media archive as URL and Title. ")
                #     self.found_duplicate = True
                #     break

                # Using the article link, get the rest of the data
                article_source = requests.get(article_url)
                is_200 = self.check_response_status(article_source)
                if all([article_source, is_200]):
                    article_text_scope = self.article_soup(article_url)[0]
                    article_text = self.get_article_text(article_text_scope)
                    if not all([article_text_scope, article_text]):
                        logging.info(f"***Either article_text_scope or article_text was not present for some reason!"
                                     f"Article url: {article_url} "
                                     f"Article title: {article_title} ")
                        continue
                    # Check if any word from the second_level_keywords is in the article text,
                    # if not - continue with next article
                    article_matched_second_scope_keywords = \
                        self.check_if_keyword_in_string(article_text, BaseWebsite._second_level_keywords)
                    if not article_matched_second_scope_keywords:
                        logging.info(
                            f"---News article: <<< {article_title} >>> was not included in the data because none of "
                            f"BaseWebsite._second_level "
                            f"keywords were found in the article text "
                            f"Article url: {article_url}")
                        continue
                    article_datetime_str = self.get_article_datetime_str(article_url)
                    locations_in_article = self.get_locations(article_text)

                    BaseWebsite._data_dict["Title"].append(article_title)
                    BaseWebsite._data_dict["URL"].append(article_url)
                    BaseWebsite._data_dict["Source"].append(self.name)
                    BaseWebsite._data_dict["Type"].append(self.media_type)
                    BaseWebsite._data_dict["Article"].append(article_text)
                    BaseWebsite._data_dict["DateTime"].append(article_datetime_str)
                    BaseWebsite._data_dict["Location"].append(', '.join(str(loc) for loc in locations_in_article))
                    BaseWebsite._data_dict["Keywords1"].append(', '.join(str(word) for word in
                                                                         article_matched_first_scope_keywords))
                    BaseWebsite._data_dict["Keywords2"].append(', '.join(str(word) for word in
                                                                         article_matched_second_scope_keywords))
                    logging.info(
                        f"+++ Records for the news with {article_title} with url {article_url} and text {article_text} "
                        f"from source: {self.name} was successfully added to the BaseWebsite._data_dict")

                return BaseWebsite._data_dict
        except Exception:
            logging.info(f"***!get_data function interruption for some reason")
            self.interruption = True
            return BaseWebsite._data_dict

    def crawling_through_pages(self) -> dict:
        """
        Something like control function for the scrapping trough the news archive pages starting from 1 till
        matching an article title already existed in the extracted archive
        :return: dictionary data with the collected news in predefined keys (BaseWebsite._data_dict)
        """
        page = 1

        while True:
            logging.info(f"\tFor media {self.name} ({self.media_type}) searching in page {self.start_url}{page}\t"
                         f"The number of found articles is: {len(BaseWebsite._data_dict['Title'])}")
            print(page, len(BaseWebsite._data_dict["Title"]))
            logging.info(f"Info: {self.name, self.media_type}\nCurrent page is {page}")
            source = requests.get(self.start_url + str(page))
            is_200 = self.check_response_status(source)

            # if not is_200 or self.found_duplicate or page == 4: #TODO activate after building media archive
            if not is_200 or self.interruption or page == 3:
                logging.info(
                    f"***Link {self.start_url + str(page)} responses was not equal to 200 "
                    f"or the scraper reach duplicated item")
                break

            self.add_data(source)
            page += 1

        data_dict = BaseWebsite._data_dict
        # export collected data_dict to DataFrame
        df_from_dict = Export.dict_to_df(data_dict)
        logging.info(f"The info of the df after transform it from the _data_dict is: {df_from_dict.shape} (rows/cols)")

        # export the DataFrame to new .csv file
        Export.df_to_csv(df_from_dict, self.name)
        logging.info(f"Info: {self.name, self.media_type}\nLast page was: {page}")

        # # Update the .csv file with the newly collected data
        # Update.append_records_to_csv(f"export/{self.name}_archive.csv", data_dict)

        # Update the .csv file with the newly collected data
        Update.append_records_from_df_to_csv(df_from_dict, f"export/{self.name}_archive.csv")

        # export pandas Series file with the unique words and their occurrences # TODO make it to update not replace
        Export.sr_to_csv(Stats.count_word_occurrences(f"export/{self.name}_archive.csv", "Article", True),
                         f"{self.name}_stats")

        return data_dict

    def __repr__(self):
        return f"""
    Media name is: {self.name} >>>
    Media main link is: {self.base_url} >>>
    Media type is: {self.media_type} >>>
    The archive page base url w/o the page number is: {self.start_url} >>>
    The title class after webpage inspection is: '{self.title_class}' with tag for the title: '{self.title_tag}' >>>
    with Article class: '{self.article_class}' and tag: '{self.article_tag}' >>>
    With datetime tag from the articles pages: '{self.datetime_tag}'
    """


btv = WebsiteArchive("btvnovinite.bg",
                     "https://btvnovinite.bg",
                     "TV news",
                     "https://btvnovinite.bg/bulgaria/?page=",
                     "section-listing news-articles-inline",
                     "news-article-inline", "title",
                     "article-body", "p",
                     "date-time",
                     "WebsiteArchive")

btv_news_dict = btv.crawling_through_pages()
