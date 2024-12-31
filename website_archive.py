# coding: utf8
import os
import re
from typing import List
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging

from statistics import Stats
from transform import Import, Export, Update, Create, RemoveFile

from datetime import datetime

# Generate a unique log file name with the current datetime
log_filename = datetime.now().strftime("info_%d-%m-%Y_%H-%M-%S.log")

# Configure logging
logging.basicConfig(
    filename=log_filename,
    encoding='utf-8',
    level=logging.INFO,
    format=u'%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filemode="w",
)

# logging.basicConfig(filename='info.log',
#                     encoding='utf-8',
#                     level=logging.INFO,
#                     format=u'%(asctime)s %(levelname)-8s %(message)s',
#                     datefmt='%d-%m-%Y %H:%M:%S',
#                     filemode="w",
#                     )


class BaseWebsite(ABC):
    """A base abstract class that represent media websites

        Attributes
        ----------
        name = media name (most recognisable part of the home page: for example "btvnovinite.bg")
        base_url = media website home page (for example "https://btvnovinite.bg")
        media_type = type of the media (for example "TV news", "Website", "Tabloid" etc.)

        Methods
        -------
        check_response_status(source: requests) -> bool:
            The function returns either the url request is 200 or not

        check_if_keyword_in_string(text: str, keywords: tuple) -> [List[str], None]:
            Uses the two tuples: _first_level_keywords, _second_level_keywords for filtering only the article titles and
            then the article texts which are in the scope of the project

        get_locations(article_text):
            The function try to match if there is a location/s in Bulgaria in the article text
            using an imported list of locations

        search_in_archive_csv_by_column_by_value(self, column, value):
            @abstractmethod

        section_soup(self, source):
            @abstractmethod

        article_soup(self, url: str):
            @abstractmethod

        get_article_title(self, element):
            @abstractmethod

        get_article_link(self, element):
            @abstractmethod

        get_article_text(self, scope):
            @abstractmethod

        get_article_datetime_str(self, article_url):
            @abstractmethod

        add_data(self, source):
            @abstractmethod

        crawling_through_pages(self):
            @abstractmethod
    """

    _first_level_keywords = (
        ' жена', ' жени', 'съпруга', ' дъщер', 'внучк', 'момиче', 'студентк', 'ученичк',
        'баба', 'домашното насилие', 'домашно насилие', 'годеница', 'приятелк', 'гимназистк',
        'майка')

    _second_level_keywords = ('домашно насилие', 'уби', 'застрел', 'мушк', 'обезобраз', 'преби',
                              'изнасил', 'тормоз', 'насил', ' прострел', 'смърт', 'жертва', 'нарязя')

    _first_level_keywords_excl = (
        'мъж и жена', 'катастроф', 'автобус', ' кола', 'трамва', 'блъсна', 'автомоб', 'зебра', 'влак', 'камион',
        'маршрутк',
        'тролей', 'волан', 'шофьор', 'самолет', 'микробус', 'тир', 'мотор', 'шофир', 'пешеход', 'спирка', 'такси',
        'куче', 'нахап', 'глутниц', 'ужил',
        'пожар', 'наводн', 'мълния', 'удави', ' море', 'срут', 'почитаме', "мъжа и жената", 'мигранти',
        ' падан', ' падна ', 'скочи', 'операц', 'здравн', 'здрави', 'здраве', 'здрава', 'психичн', 'пари',
        'телефон', ' ало ', 'потоп', 'издирва ', 'родител', 'нарко', 'алкохол', 'грип', 'COVID', 'бебе', 'донор',
        'инцидент', 'онко', ' рак ', 'добро', 'деца', 'роден', 'роди', 'сърце', 'приет', 'изчезнали', 'дете',
    )

    _second_level_keywords_excl = (
        'инцидент', 'шофьорка', 'катастрофа'
    )

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
    }

    _bg_months = {
        "януари": "01",
        "февруари": "02",
        "март": "03",
        "април": "04",
        "май": "05",
        "юни": "06",
        "юли": "07",
        "август": "08",
        "септември": "09",
        "октомври": "10",
        "ноември": "11",
        "декември": "12",
    }

    _search_dict_village = Import.file_to_dictionary("import/villages_list.csv")
    _search_dict_city = Import.file_to_dictionary("import/cities_list.csv")

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

    @staticmethod
    def check_if_keyword_in_string(text: str, keywords: tuple) -> [List[str], None]:
        """
        Uses the two tuples: _first_level_keywords, _second_level_keywords,
        _first_level_keywords_excl, _second_level_keywords_excl
        for filtering only the article titles and
        then the article texts which are in the scope of the project
        :param text: article_title or article_text
        :param keywords: the two tuples: _first_level_keywords, _second_level_keywords from the BaseWebsite class
        :return: either matched keywords or None
        """
        if any(substring in re.sub(r'[.|–,!?:„“;\-()"\\/{}\]\[`=]', ' ', " " + text.lower())
               for substring in keywords):
            return [word for word in keywords if word in text.lower()]
        else:
            return None

    @staticmethod
    def get_locations(article_text) -> [List[str] or str]:
        """
        The function try to match if there is a location/s in Bulgaria in the article text
        using an imported list of locations
        :param article_text: text with the article itself
        :return: list with matched locations or an empty string
        """
        location = []
        [location.append(value) for value in BaseWebsite._search_dict_city.values() if
         value in article_text and value not in location]
        [location.append(value) for value in BaseWebsite._search_dict_village.values() if
         value in article_text and value not in location]
        return location if location else ""

    @staticmethod
    def get_media_names():
        """

        :return:
        """
        tmp = globals().copy()
        # print(tmp)
        media_names_list: list = []
        media_names_dict: dict = {}
        for k, v in tmp.items():
            if isinstance(v, BaseWebsite):
                # print(k, v)
                media_names_list.append(v)
                media_names_dict[k] = v
        return [media_names_list, media_names_dict]

    def __str__(self):
        return f"{self.name}"

    @abstractmethod
    def search_in_archive_csv_by_column_by_value(self, column, value):
        ...

    @abstractmethod
    def section_soup(self, source):
        ...

    @abstractmethod
    def article_soup(self, url: str):
        ...

    @abstractmethod
    def get_article_title(self, element):
        ...

    @abstractmethod
    def get_article_link(self, element):
        ...

    @abstractmethod
    def get_article_text(self, scope):
        ...

    @abstractmethod
    def get_article_datetime_str(self, article_url):
        ...

    @abstractmethod
    def add_data(self, source):
        ...

    @abstractmethod
    def crawling_through_pages(self):
        ...


class WebsiteArchive(BaseWebsite):
    """A base abstract class that represent media websites

        Attributes
        ----------
        name = media name (most recognisable part of the home page: for example "btvnovinite.bg")
        base_url = media website home page (for example "https://btvnovinite.bg")
        media_type = type of the media (for example "TV news", "Website", "Tabloid" etc.)
        protocol: either "https://" or "http://"
        start_url: the archive url w/o the page int at the end (example: "https://btvnovinite.bg/bulgaria/?page=")
        section_class: the inspected html class for the container of the articles and their links
        title_class: the inspected html class for the title text
        title_tag: the inspected html tag for the title text
        article_class: the inspected html class for the article text
        article_tag: the inspected html tag for the article text
        datetime_tag: the inspected html tag for the date
        website_type:  the type of the website
        _media_archive_dict:  = None
        found_duplicate: the bool for indicating if record exist that can abort the script if True (default: False)
        interruption: the bool for indicating if something stops the crawling
                      that can abort the script if True (default: False)
        datetime_format:  = format of the datetime (for example:'%H:%M %d.%m.%Y')

        Methods
        -------

        search_in_archive_csv_by_column_by_value(self, column, value) -> [None, str]:
            Check if a particular value already existed
            in a particular column to exclude duplicated records
            in the media archive file and to abort the script

        section_soup(self, source) -> [None, str]:
            After inspecting and defining the html box/section
            with the news articles and urls
            (self.section_class and self.title_class given during the initialization)
            the function creates a bs4soup
            narrowing the search for needed article elements

        article_soup(self, url: str) -> [None, list]:
            Creates a soup with the needed scope for extracting article_text, datetime, locations etc...

        get_article_title(self, element) -> [None, list]:
            If some of the BaseWebsite._first_level_keywords
            matching word/words from the article title.
            The article and the article url will be further analyzed
            for the purpose of adding them in the _data_dict with
            the rest of the data

        get_article_link(self, element) -> str:
            Finds the article url and validates if the 'href'
            element is a standard formatted link (have 'https://' e.g)

        get_article_text(self, scope) -> [str, None]:
            Collects the article text parts via self.article_tag

        get_article_datetime_str(self, article_url) -> str:
            Extracts the date and time when the article
            was publish/updated and remove some local formatting

        add_data(self, source) -> dict:
            The main function of the script that connects the rest of the data collection functions

        check_if_media_folder_exists(self):
            If folder for a new BaseWebsite child instance doesn't exist,
            the method calls another function to create it

        check_if_media_archive_file_exists(self, columns: List[str]):
            If an archive .csv file for a new BaseWebsite child instance doesn't exist,
            the method calls another function to create it (empty one)

        crawling_through_pages(self) -> dict:
            Something like control function for the scrapping
            trough the news archive pages starting from 1 until
            matching an article title already existed in the extracted archive
            or until unexpected error or exceeding the archive pages

    """

    def __init__(self, name, base_url, media_type, start_url, section_class, title_class, title_tag, article_class,
                 article_tag,
                 datetime_class, datetime_tag,
                 website_type, datetime_format):
        super().__init__(name, base_url, media_type)
        self.protocol = "https://" if base_url.__contains__("https://") else "http://"
        self.start_url = start_url
        self.section_class = section_class
        self.title_class = title_class
        self.title_tag = title_tag
        self.article_class = article_class
        self.article_tag = article_tag
        self.datetime_class = datetime_class
        self.datetime_tag = datetime_tag
        self.website_type = website_type
        self._media_archive_dict = None
        self.found_duplicate = False
        self.interruption = False
        self.datetime_format = datetime_format

    def search_in_archive_csv_by_column_by_value(self, column, value) -> [None, str]:
        """
        Check if a particular value already existed
        in a particular column to exclude duplicated records
        in the media archive file and to abort the script

        :param column: one of the _data_dict keys
        :param value: related to _data_dict columns/keys
        :return: value if found else None
        """
        self._media_archive_dict = Import.csv_to_dict(f'export/{self.name}/{self.name}_archive.csv')
        if value in self._media_archive_dict[column]:
            return value
        return None

    def section_soup(self, source) -> [None, str]:
        """
        After inspecting and defining the html box/section
        with the news articles and urls
        (self.section_class and self.title_class given during the initialization)
        the function creates a bs4soup
        narrowing the search for needed article elements

        :param source: a request obj with the 'start_page' url as a parameter
        :return: section scope
        """
        source_text = source.text
        soup = BeautifulSoup(source_text, 'lxml')
        try:
            main_section = soup.find(class_=self.section_class)  # TODO make self.main_section
            if self.title_class != "a":
                section = main_section.find_all(class_=self.title_class)  # TODO
            else:
                section = main_section.find_all(self.title_class)
            # section = main_section.find_all(class_=self.title_class)
        except AttributeError:
            logging.info(f"***Can't find the html section/box by self.section_class or self.title_class")
            return None
        return section

    def datetime_soup(self, url: str) -> [None, list]:
        """
        Creates a soup with the needed scope for extracting article_text, datetime, locations etc...

        :param url: the article url
        :return: both the soup for the datetime extraction later and the text scope
        """
        source = requests.get(url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'})
        source_text = source.text
        soup = BeautifulSoup(source_text, 'lxml')
        try:
            datetime_scope = soup.find(class_=self.datetime_class)
        except AttributeError:
            logging.info(f"***Can't find text_scope searching in {url} soup")
            return None
        return datetime_scope

    def article_soup(self, url: str) -> [None, list]:
        """
        Creates a soup with the needed scope for extracting article_text, datetime, locations etc...

        :param url: the article url
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
        return text_scope

    def get_article_title(self, element) -> [None, list]:
        """
        If some of the BaseWebsite._first_level_keywords
        matching word/words from the article title.
        The article and the article url will be further
        analyzed for the purpose of adding them in the _data_dict with
        the rest of the data

        :param element: element of the html section
        :return: the title of the article and the matched words if any; else: None
        """
        try:
            article_title = element.find(class_=self.title_tag).text
            article_title = article_title.replace("\n", "").strip()
        except AttributeError:
            logging.info(f"***Can't find article title")
            return None
        first_lvl_keyword = self.check_if_keyword_in_string(article_title, BaseWebsite._first_level_keywords)
        excluded_first_lvl_keyword = self.check_if_keyword_in_string(article_title,
                                                                     BaseWebsite._first_level_keywords_excl)
        if first_lvl_keyword:
            if not excluded_first_lvl_keyword:
                return article_title, first_lvl_keyword
            else:
                logging.info(f"---Article with title: {article_title} was not added because"
                             f" contains words from article title exclusion list: {excluded_first_lvl_keyword}")
        return None

    def get_article_link(self, element) -> str:
        """
        Finds the article url and validates if the 'href'
        element is a standard formatted link (have 'https://' e.g)

        :param element: element of the html section
        :return: validated/formatted url as string
        """
        if self.title_class != 'a':
            link = element.a['href']
        else:
            link = element.get('href')

        if not link.startswith(self.base_url):
            valid_link = self.base_url + link
        else:
            valid_link = link

        return valid_link

    def get_article_text(self, scope) -> [str, None]:
        """
        Collects the article text parts via self.article_tag

        :param scope: the needed html that contains the article pieces
        :return: the article text
        """
        try:
            # get and join the <p> article text and replace new line tags and spaces with single space
            article_text = " ".join(a.getText()
                                    .replace('\xa0', " ")
                                    .replace('\n', " ")
                                    .replace('\r', " ")
                                    .strip()
                                    for a in scope.findAll(self.article_tag))
        except AttributeError:
            logging.info(f"***Can't find article text")
            return None
        return article_text

    def get_article_datetime_str(self, article_url) -> str:
        """
        Extracts the date and time when the article
        was publish/updated and remove some local formatting

        :param article_url:
        :return: empty string or the date/time in string format
        """
        try:
            datetime_soup = self.datetime_soup(article_url)
            datetime_scope = datetime_soup.find(class_=self.datetime_tag)
        except AttributeError:
            logging.info(f"***Issue with extracting datetime for url: {article_url}")
            return ""
        article_datetime = datetime_scope.getText()

        # check if bg month in the datetime
        if len([ch for ch in article_datetime.lower() if re.search('[а-яА-Я]', ch)]) > 2:

            for x in article_datetime.split(" "):
                if x.lower() in BaseWebsite._bg_months.keys():
                    replacement = BaseWebsite._bg_months[x.lower()]
                    article_datetime = article_datetime.replace(x, replacement)
                    # print(article_datetime, "<< with month")
                    # article_datetime = article_datetime.replace(" ", ":", 2)
                    article_datetime = article_datetime.replace("  ", "-")
                    article_datetime = article_datetime.replace(" ", ":")
                    article_datetime = article_datetime.replace("-", " ")
                    # print(article_datetime, "<< without month")

        lst = [re.sub(r'[^\d]', " ", x).strip() for x in article_datetime.split(" ")]
        new_dt = [x for x in lst if x]
        # print(new_dt)
        final_article_datetime = []
        for element in new_dt:
            if len(element) == 5:
                time = element.replace(" ", ":")
                final_article_datetime.append(time)
            else:
                date = element.replace(" ", "-")
                final_article_datetime.append(date)
        if len(final_article_datetime[0]) < len(final_article_datetime[1]):
            final_article_datetime[0], final_article_datetime[1] = final_article_datetime[1], final_article_datetime[0]

        # print(", ".join(x for x in final_article_datetime))
        return ", ".join(x for x in final_article_datetime)

    def add_data(self, source) -> dict:
        """
        The main function of the script that connects the rest of the data collection functions

        :param source: a request obj with the 'start_page' url as a parameter
        :return: the main dictionary with the data for every filtered article
        """
        try:
            articles_section = self.section_soup(source)
            if not articles_section:
                self.interruption = True

            for i in range(len(articles_section)):
                element = articles_section[i]
                if not self.get_article_title(element):
                    continue
                article_title, article_matched_first_scope_keywords = self.get_article_title(element)
                article_url = self.get_article_link(element)
                if not all([article_title, article_url]):
                    logging.info(f"*** Problem with extracting article_title or/and article_url")
                    continue

                # Check if the article + URL already existed
                if self.search_in_archive_csv_by_column_by_value("URL", article_url) and \
                        self.search_in_archive_csv_by_column_by_value("Title", article_title):
                    logging.info(f"***Article with title: <<< {article_title} >>> already existed "
                                 f"within the media archive as URL and Title. ")
                    self.found_duplicate = True
                    break

                # Using the article link, get the rest of the data
                article_source = requests.get(article_url)
                is_200 = self.check_response_status(article_source)
                if all([article_source, is_200]):
                    article_text_scope = self.article_soup(article_url)
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
                    # adding datetime of publishing the article
                    article_datetime_str = self.get_article_datetime_str(article_url)

                    # adding locations if some of the locations from the imported file
                    # is/are matching with strings in the article's text
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

    def check_if_media_folder_exists(self) -> None:
        """
        If folder for a new BaseWebsite child instance doesn't exist,
        the method calls another function to create it

        :return: None
        """
        dir_name = "export/"
        list_of_file = os.listdir(dir_name)
        dir_list = []
        for file in list_of_file:
            if self.name == file:
                dir_list.append(file)
                break
        if not dir_list:
            Create.create_media_folder(self.name)

    def check_if_media_archive_file_exists(self, columns: List[str]):
        """
        If an archive .csv file for a new BaseWebsite child instance doesn't exist,
        the method calls another function to create it (empty one)

        :param columns:
        :return:
        """
        Create.create_empty_archive_csv_file(self.name, columns)

    def crawling_through_pages(self) -> str:
        """
        Something like control function for the scrapping
        trough the news archive pages starting from 1 until
        matching an article title already existed in the extracted archive
        or until unexpected error or exceeding the archive pages

        :return: None
        """
        # check if media folders and media archive file exists and creates it if not
        self.check_if_media_folder_exists()
        self.check_if_media_archive_file_exists([col for col in BaseWebsite._data_dict.keys()])
        page = 1

        while True:
            logging.info(f"\tFor media {self.name} ({self.media_type}) searching in page {self.start_url}{page}\t"
                         f"The number of found articles is: "
                         f"{len(BaseWebsite._data_dict['Title']) if BaseWebsite._data_dict['Title'] else 0}")
            print(self.name, page, len(BaseWebsite._data_dict["Title"]))
            logging.info(f"Info: {self.name, self.media_type}\nCurrent page is {page}")
            source = requests.get(self.start_url + str(page))
            is_200 = self.check_response_status(source)

            # break if not the correct response, a duplicate record was found or an interruption occurs
            if not is_200 or self.found_duplicate or self.interruption:
                if not is_200:
                    logging.info(f"***Link {self.start_url + str(page)} responses was not equal to 200 ")
                    break
                break

            self.add_data(source)
            page += 1

        data_dict = BaseWebsite._data_dict

        # export collected data_dict to DataFrame
        df_from_dict = Export.dict_to_df(data_dict)
        logging.info(f"The info of the df after transform it from the _data_dict is: {df_from_dict.shape} (rows/cols)")

        # export the DataFrame to new .csv file
        Export.df_to_csv(df_from_dict, self.name, self.datetime_format)
        logging.info(f"Info: {self.name, self.media_type}\nLast page was: {page}")

        # Update the .csv file with the newly collected data
        Update.append_records_from_df_to_csv(df_from_dict, f"export/{self.name}/{self.name}_archive.csv",
                                             self.datetime_format)

        logging.info(f"The 'export/{self.name}/{self.name}_archive.csv' was updated with "
                     f"{len(data_dict['Title'])} articles")

        # export pandas Series file with the unique words and their occurrences
        Stats.count_word_occurrences(f"export/{self.name}/{self.name}_archive.csv",
                                     ["Article", "Title"],
                                     self.name,
                                     True)
        # setting the data dictionary bach to initial state
        # for not letting the different exports to have mixed media data
        BaseWebsite._data_dict = {
            "Title": [],
            "URL": [],
            "Source": [],
            "Type": [],
            "DateTime": [],
            "Article": [],
            "Location": [],
            "Keywords1": [],
            "Keywords2": [],
        }
        logging.info(f"@The article collection for {self.name} is done!")
        return f"@The article collection for {self.name} is done!"

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
                     "date-time-wrap", "date-time",
                     "WebsiteArchive",
                     "%d-%m-%Y, %H:%M",
                     )

nova = WebsiteArchive("nova.bg",
                      "https://nova.bg",
                      "TV news",
                      "https://nova.bg/news/category/2/%D0%B1%D1%8A%D0%BB%D0%B3%D0%B0%D1%80%D0%B8%D1%8F/",
                      "col-lg-12 col-md-12 col-sm-12 col-xs-12 category-list-wrapper",
                      "thumb-box", "title",
                      "col-lg-12 col-md-12 col-sm-12 col-xs-12 article-body io-article-body", "p",  #
                      "col-lg-8 col-md-8 col-sm-12 col-xs-12 artcle-desc-info", "date-time",
                      "WebsiteArchive",
                      "%d-%m-%Y, %H:%M",
                      )

bnt = WebsiteArchive("bntnews.bg",
                     "https://bntnews.bg",
                     "TV news",
                     "https://bntnews.bg/bg/c/bulgaria?page=",
                     "news-wrap-view",
                     "a", "img-title",
                     "big-slider video-wrap -r", "p",
                     "r-part relative", "news-time",
                     "WebsiteArchive",
                     "%d-%m-%Y, %H:%M",
                     )

if __name__ == "__main__":

    # get a list with all media names for combining them later
    all_media_instances_list = BaseWebsite.get_media_names()[0]
    all_media_instances_dict = BaseWebsite.get_media_names()[1]

    btv_news_dict = btv.crawling_through_pages()
    bnt_news_dict = bnt.crawling_through_pages()
    nova_news_dict = nova.crawling_through_pages()

    # combine all archives
    Export.combine_archives(list(all_media_instances_dict.values()))

    # export pandas Series file with the unique words and their occurrences
    Stats.count_word_occurrences(f"export/combined_archive/combined_archive.csv",
                                 ["Article", "Title"],
                                 "combined_archive",
                                 True)
