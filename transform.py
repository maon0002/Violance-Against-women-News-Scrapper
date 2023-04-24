import csv
import logging
from csv import DictWriter
import pandas as pd
import os


class Import:
    __import_folder = "import/"

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

    @staticmethod
    def file_to_dictionary(path) -> dict:
        """
        Transform .csv file to df then to dictionary. It returns only the first two columns
        :return: dictionary - {Code: Location Name}
        """
        df = pd.read_csv(path, dtype={"CODE": "string"})
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
    __export_folder = "export/"

    @staticmethod
    def dict_to_df(dictionary: dict) -> pd.DataFrame:
        """
        Converts the _data_dict to a DataFrame
        :param dictionary:
        :return: a DataFrame obj
        """
        dataframe = pd.DataFrame(dictionary)[::-1]
        return dataframe

    @staticmethod
    def df_to_excel(dataframe: pd.DataFrame, name: str, datetime_format: str) -> None:
        """
        Converts the DateFrame with the data and creates a .xlsx file
        :param datetime_format:
        :param dataframe:
        :param name:
        :return: nothing
        """
        with pd.ExcelWriter(f"{Export.__export_folder}{name}/{name}.xlsx", engine='xlsxwriter',
                            datetime_format=datetime_format) as ew:
            dataframe.to_excel(ew, index=False)

    @staticmethod
    def df_to_csv(dataframe: pd.DataFrame, name: str, datetime_format: str) -> None:
        """
        Converts the DateFrame with the data to .csv
        :param datetime_format:
        :param dataframe: transformed from BaseWebsite._data_dict
        :param name: depends on instance name
        :return: nothing
        """
        sorted_dataframe = Update.sort_df_by_datetime(dataframe, datetime_format)
        sorted_dataframe.to_csv(f"{Export.__export_folder}{name}/{name}.csv", encoding='utf-8', index=False)

    @staticmethod
    def sr_to_csv(sr: pd.Series, media_name: str, file_name: str) -> None:
        """
        Converts the Series with the data to .csv
        :param media_name:
        :param file_name:
        :param sr: transformed from BaseWebsite._data_dict
        :return: nothing
        """
        sr.to_csv(f"{Export.__export_folder}{media_name}/{file_name}.csv", encoding='utf-8')


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
    def append_records_from_df_to_csv(dataframe: pd.DataFrame, path: str, datetime_format: str) -> None:
        Update.sort_df_by_datetime(dataframe, datetime_format)
        dataframe.to_csv(path, mode='a', index=False, header=False)

    @staticmethod
    def sort_df_by_datetime(dataframe: pd.DataFrame, datetime_format, ):
        dataframe['DateTime'] = pd.to_datetime(dataframe['DateTime'], format=datetime_format)
        # print(dataframe.dtypes)
        dataframe.sort_values(by='DateTime', ascending=False, inplace=True)
        return dataframe


class Create:
    __export_folder = "export/"

    @staticmethod
    def create_media_folder(name: str):
        directory = name
        parent_directory = "export/"
        path = os.path.join(parent_directory, directory)
        os.mkdir(path)
        logging.info("Directory '% s' created" % directory)

    @staticmethod
    def create_empty_archive_csv_file(media_name, columns):

        try:
            open(f"{Create.__export_folder}{media_name}/{media_name}_archive.csv")
            logging.info(f"Opening: '{Create.__export_folder}{media_name}/{media_name}_archive.csv' >>>")
        except FileNotFoundError:
            headers = columns
            filename = f"{Create.__export_folder}{media_name}/{media_name}_archive.csv"
            with open(filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(headers)
                csv_file.close()
            logging.info(f"Creating: '{Create.__export_folder}{media_name}/{media_name}_archive.csv' >>>")

            # with open(f"{Create.__export_folder}{media_name}/{media_name}_archive.csv", 'w') as creating_new_csv_file:
            #     pass
            # logging.info(f"Empty File 'export/{media_name}/{media_name}_archive.csv' Created Successfully")

        # # creating new pandas DataFrame
        # dataframe = pd.DataFrame(list())
        #
        # # writing empty DataFrame to the new csv file
        # dataframe.to_csv(f"{Create.__export_folder}{media_name}/{media_name}_archive.csv")
        # logging.info(f"Empty File 'export/{media_name}/{media_name}_archive.csv' Created Successfully")


