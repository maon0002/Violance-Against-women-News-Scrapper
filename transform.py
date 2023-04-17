import logging
from csv import DictWriter
import pandas as pd


class Import:

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def show_first_ten_rows(self) -> pd.DataFrame:
        """
        Uses a DataFrame to show first 10 rows from it
        :return:
        """
        df = pd.read_csv(self.path)
        return df.head(10)

    @staticmethod
    def import_to_df(path) -> pd.DataFrame:
        """
        Read a .csv file and convert it to a DataFrame
        :return:
        """
        df = pd.read_csv(path)
        return df

    def file_to_dictionary(self) -> dict:
        """
        Transform .csv file to df then to dictionary. It returns only the first two columns
        :return: dictionary - {Code: Location Name}
        """
        df = pd.read_csv(self.path, dtype={"CODE": "string"})
        dictionary = {}
        for i in range(len(df)):
            key = df.iloc[i][0]
            value = df.iloc[i][1]
            dictionary[key] = value
        return dictionary

    @staticmethod
    def csv_to_dict(path: str) -> dict:
        """
        Imports an .csv file and converts it to dictionary
        :param path:
        :return: a dictionary
        """
        dict_from_csv = pd.read_csv(filepath_or_buffer=path, index_col=False).to_dict(orient='list')
        return dict_from_csv


def __repr__(self):
    return f"Size of the {self.name} file is: {len(self.import_to_df())} rows and " \
           f"{len(self.import_to_df().columns)} columns"


class Export:

    @staticmethod
    def dict_to_df(dictionary: dict) -> pd.DataFrame:
        """
        Converts the _data_dict to a DataFrame
        :param dictionary:
        :return: a DataFrame obj
        """
        df = pd.DataFrame(dictionary)[::-1]
        return df

    @staticmethod
    def df_to_excel(df: pd.DataFrame, name: str) -> None:
        """
        Converts the DateFrame with the data and creates a .xlsx file
        :param df:
        :param name:
        :return: nothing
        """
        with pd.ExcelWriter(f"export/{name}.xlsx", engine='xlsxwriter', datetime_format='%H:%M %d.%m.%Y', ) as ew:
            df.to_excel(ew, index=False)

    @staticmethod
    def df_to_csv(df: pd.DataFrame, name: str) -> None:
        """
        Converts the DateFrame with the data to .csv
        :param df: transformed from BaseWebsite._data_dict
        :param name: depends on instance name
        :return: nothing
        """
        df.to_csv(f"export/{name}.csv", encoding='utf-8', index=False)  # date_format = '%d.%m.%Y'

    @staticmethod
    def sr_to_csv(sr: pd.Series, name: str) -> None:
        """
        Converts the Series with the data to .csv
        :param sr: transformed from BaseWebsite._data_dict
        :param name: depends on instance name
        :return: nothing
        """
        sr.to_csv(f"export/{name}.csv", encoding='utf-8')  # date_format = '%d.%m.%Y'


class Update:

    @staticmethod
    def append_records_to_csv(file_path: str, dictionary: dict) -> None:
        """
        After executing of the script if any non-existed news are found will be added at the bottom
        to the media archive .csv file
        :param file_path: based on the instance name
        :param dictionary: BaseWebsite._data_dict
        :return: nothing
        """
        try:
            col_names = [col for col in dictionary.keys()]
            with open(file_path, 'a', encoding="utf-8", newline='') as file:
                dictwriter_object = DictWriter(file, fieldnames=col_names)
                for i in range(len(dictionary["Title"])):
                    list_with_dicts = []
                    current_dict = {}
                    for j in range(len(dictionary.keys())):
                        key = col_names[j]
                        value = dictionary[key][i]
                        current_dict[key] = value
                    list_with_dicts.append(current_dict)
                    dictwriter_object.writerows(list_with_dicts)
                file.close()
        except AttributeError:
            logging.debug(f"***There are no new records/news to add!!!")

    @staticmethod
    def append_records_from_df_to_csv(dataframe: pd.DataFrame, path: str) -> None:
        dataframe.to_csv(path, mode='a', index=False, header=False)
