# coding: utf8
import re
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging
from transform import Import, Export, Update

logging.basicConfig(filename='debug.log', encoding='utf-8',
                    level=logging.DEBUG,
                    format=u'%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )


class BaseWebsite(ABC):
    # _first_level_keywords = ('жена', 'жени' 'съпруга', 'дъщеря', 'внучк', 'девойк', 'момиче', 'студентк', 'ученичк',
    #                          'баба', 'домашното насилие', 'домашно насилие', 'годеница', 'приятелка', 'гимназистка',
    #                          'майка', 'приятелки', 'гимназистки')
    # _second_level_keywords = ('домашно насилие', 'убийство', 'застреля', 'намушка', 'обезобраз', 'преби', 'наказание',
    #                           'изнасил', 'тормоз', 'насил', 'рани', 'стрел', 'сигнал', 'осъд', 'смърт', 'криминално',
    #                           'намерена', 'полиция', 'насилвана', 'заповед', 'полицай', 'полицаи', 'полицията'
    #                           )
    _first_level_keywords = (
        ' жена', ' жени', 'съпруга', 'дъщеря', 'внучк', 'девойк', 'момиче', 'студентк', 'ученичк',
        'баба', 'домашното насилие', 'домашно насилие', 'годеница', 'приятелк', 'гимназистк',
        'майка', 'дъщери')
    _second_level_keywords = ('домашно насилие', 'уби', 'стрел', 'мушк', 'обезобраз', 'преби', 'наказан',
                              'изнасил', 'тормоз', 'насил', ' рани', ' стрел', 'сигнал', 'осъд', 'смъртта',
                              'криминалн', 'намерен', ' полиц', 'насилван', 'запов')

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

    def __init__(self, name, base_url, media_type):
        self.name = name
        self.base_url = base_url
        self.media_type = media_type

    @abstractmethod
    def crawling_through_pages(self):
        ...


class WebsiteArchive(BaseWebsite):
    first_level_data = []

    def __init__(self, name, base_url, media_type, start_url, title_class, title_tag, article_class, article_tag,
                 datetime_tag, website_type):
        super().__init__(name, base_url, media_type)
        self.protocol = "https://" if base_url.__contains__("https://") else "http://"
        self.start_url = start_url
        self.title_class = title_class
        self.title_tag = title_tag
        self.article_class = article_class
        self.article_tag = article_tag
        self.datetime_tag = datetime_tag
        self.website_type = website_type

    @staticmethod
    def check_response_status(source: requests) -> bool:
        """
        The function returns either the url request is 200 or not
        :param source:
        :return: True / False
        """
        return source.status_code == 200

    def check_for_existed_articles_from_the_archive(self, url) -> [None, str]:
        if url in existed_news_urls_list:
            if not BaseWebsite._data_dict.values():
                logging.debug(f"No new articles was found")
                return None
            Update.append_records_to_csv(f"export/{self.name}_archive.csv", BaseWebsite._data_dict)
            logging.debug(
                f"After matching existed title in the archive and updating it with the latest news records, program"
                f"stopped as expected")
            return None
        return url

    def get_second_level_data(self, article_link) -> [list, dict, None]:
        """
        This function follows the link to the article and returns the article text + date of publishing
        :param article_link:
        :return: List[str, str]
        """

        source = requests.get(article_link)
        is_200 = self.check_response_status(source)

        if is_200:
            source = requests.get(article_link)
            source_text = source.text
            soup = BeautifulSoup(source_text, 'lxml')
            text_scope = soup.find(class_=self.article_class)
            article = " ".join(a.getText().replace('\xa0', " ").strip() for a in
                               text_scope.findAll(self.article_tag))  # TODO attribute or function

            # TODO analyze the articles and run second time with the code below; compare
            if any(substring in re.sub(r'[.|,!?:„“;\-()"\\/{}\]\[`=]', ' ', " " + article.lower()) for substring in
                   BaseWebsite._second_level_keywords):
                datetime_scope = soup.find(class_=self.datetime_tag)
                article_datetime = datetime_scope.getText().replace(" ч.", "").replace(" г.", "")
                # TODO transform datetime text into datetime

                second_lvl_keyword = [word for word in BaseWebsite._second_level_keywords if word in article.lower()]
                return [article, article_datetime, second_lvl_keyword]
            else:
                logging.debug(
                    f"News article: <<< {article} >>> was not included in the data because of BaseWebsite._second_level"
                    f"keywords")
                return None

            # datetime_scope = soup.find(class_=self.datetime_tag)
            # article_datetime = datetime_scope.getText().replace(" ч.", "").replace(" г.", "")
            #
            # return [article, article_datetime]
        else:
            logging.debug(
                f"News article with link {article_link} responses was not equal to 200")

    @staticmethod
    def find_if_location_in_text(article_text: str, cities: dict, villages):
        """
        Searching for cities or villages in the article's text using imported dictionary data from institutions websites
        :param article_text:
        :param cities: imported .csv with official data of the cities in BG ({code: name})
        :param villages: imported .csv with official data of the villages in BG ({code: name})
        :return: [cities/villages names if any]
        """
        location = []
        [location.append(value) for value in cities.values() if value in article_text and value not in location]
        [location.append(value) for value in villages.values() if value in article_text and value not in location]
        return location if location else ""

    def get_first_level_data(self, section) -> [dict, None]:
        """
        The function collects data for the '_data_dict' columns when the news content are related to women and violence
        against them
        :param section: html section/box with the needed news data (excluding banners, footers, ads)
        :return: dictionary from the Base/abs class with the general data model and content
        """

        for i in range(len(section)):
            element = section[i]
            title = element.find(class_=self.title_tag).text

            if any(substring in re.sub(r'[.|,!?:„“;\-()"\\/{}\]\[`=]', ' ', " " + title.lower()) for substring in
                   BaseWebsite._first_level_keywords):
                first_lvl_keyword = [word for word in BaseWebsite._first_level_keywords if word in title.lower()]
                link = element.a['href']

                if not link.startswith(self.base_url):
                    valid_link = self.base_url + link
                else:
                    valid_link = link

                if not self.check_for_existed_articles_from_the_archive(valid_link):
                    return None

                try:
                    article_text = self.get_second_level_data(valid_link)[0]
                    article_datetime_str = self.get_second_level_data(valid_link)[1]
                    second_level_keyword = self.get_second_level_data(valid_link)[2]
                except TypeError:
                    logging.debug(
                        f"Article with title: <<< {title} >>> was excluded after checking of second_level_keywords "
                        f"filtering; link: {valid_link}")
                    break

                search_dict_village = Import("villages", "import/villages_list.csv").file_to_dictionary()
                search_dict_city = Import("cities", "import/cities_list.csv").file_to_dictionary()
                location = self.find_if_location_in_text(article_text, search_dict_city, search_dict_village)


                BaseWebsite._data_dict["Title"].append(title)
                BaseWebsite._data_dict["URL"].append(valid_link)
                BaseWebsite._data_dict["Source"].append(self.name)
                BaseWebsite._data_dict["Type"].append(self.media_type)
                BaseWebsite._data_dict["Article"].append(article_text)
                BaseWebsite._data_dict["DateTime"].append(article_datetime_str)
                BaseWebsite._data_dict["Location"].append(', '.join(str(loc) for loc in location))
                BaseWebsite._data_dict["Keywords1"].append(', '.join(str(word) for word in first_lvl_keyword))
                BaseWebsite._data_dict["Keywords2"].append(', '.join(str(word) for word in second_level_keyword))
                logging.debug(
                    f"Records for the news with {title} from source: {self.name} was successfully added to "
                    f"the BaseWebsite._data_dict")
        return BaseWebsite._data_dict

    def make_first_level_soup(self, source: requests) -> dict:
        """
        Isolate only the html in the html section/box with the needed news data (excluding banners, footers, ads);
        The first level data contains article's titles and urls and
        is used later for getting articles texts and datetimes
        :param source:
        :return:
        """
        source_text = source.text
        soup = BeautifulSoup(source_text, 'lxml')
        main_section = soup.find(class_="section-listing news-articles-inline")  # TODO make self.main_section
        section = main_section.find_all(class_=self.title_class)
        initial_data_dict = self.get_first_level_data(section)

        return initial_data_dict

    def crawling_through_pages(self) -> dict:
        """
        Something like control function for the scrapping trough the news archive pages starting from 1 till
        matching an article title already existed in the extracted archive
        :return: dictionary data with the collected news in predefined keys (BaseWebsite._data_dict)
        """
        page = 6
        initial_data = None

        while True:
            print(page)
            logging.debug(f"Info: {self.name, self.media_type}\nCurrent page is {page}")
            source = requests.get(self.start_url + str(page))
            is_200 = self.check_response_status(source)

            if not is_200 or page == 20:
                logging.debug(
                    f"Link {self.start_url + str(page)} responses was not equal to 200")
                break

            initial_data = self.make_first_level_soup(source)

            if not initial_data:
                break
            page += 1
        logging.debug(f"Info: {self.name, self.media_type}\nLast page was: {page}")
        return initial_data

    def main(self):
        pass

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
                     "news-article-inline", "title",
                     "article-body", "p",
                     "date-time",
                     "WebsiteArchive")

#  Import already scraped data convert it to dict and select list of only article titles w/o duplicated articles
existed_news_articles_dict = Import.csv_to_dict('export/btvnovinite.bg_archive.csv')

existed_news_urls_list = []

for e in existed_news_articles_dict.items():
    column = e[0]
    values = e[1]
    if column == "URL":
        existed_news_urls_list = values

# existed_news_articles = []  # use for test before preparing of the archive db

btv_news_dict = btv.crawling_through_pages()
logging.debug(f"Length of the _data_dict before transform it to a DataFrame is: {len(btv_news_dict.values())}")
btv_news_df = Export.dict_to_df(btv_news_dict)
logging.debug(f"The info of the df after transform it from the _data_dict is: {btv_news_df.shape}")
Export.df_to_csv(btv_news_df, 'btvnovinite.bg')
