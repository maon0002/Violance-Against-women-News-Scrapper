from website_archive import WebsiteArchive


class ScrapperScript:
    VALID_WEBSITE_TYPES = {'WebsiteArchive': WebsiteArchive}

    def __init__(self):
        self.articles = {}
        self.websites = []
        self.dataframes = []

    def add_website(self, name, base_url, media_type, start_url, title_class, title_tag, article_class, article_tag,
                    datetime_tag, website_type):
        if name in [w.name for w in self.websites]:
            raise Exception(f"{name} already added")
        if website_type not in ScrapperScript.VALID_WEBSITE_TYPES:
            raise Exception(f"{website_type} is not a valid type!")

        self.websites.append(
            ScrapperScript.VALID_WEBSITE_TYPES[website_type](name, base_url, media_type, start_url, title_class,
                                                             title_tag, article_class, article_tag,
                                                             datetime_tag, website_type))
        return f"Website '{name}' with url: {base_url} was added successfully"


btv_scrapper = ScrapperScript()
print(ScrapperScript.VALID_WEBSITE_TYPES)
print(btv_scrapper.add_website("btvnovinite.bg",
                               "https://btvnovinite.bg",
                               "TV news",
                               "https://btvnovinite.bg/bulgaria/?page=",
                               "news-article-inline", "title",
                               "article-body", "p",
                               "date-time",
                               "WebsiteArchive"))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("HI")  # TODO replace
