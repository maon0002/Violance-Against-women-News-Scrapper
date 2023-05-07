import re
from typing import Dict

from transform import Import, Export
from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist
import pandas as pd


class Stats:

    @staticmethod
    def count_word_occurrences(path: str, columns: list, name: str, output_choice: bool = True) -> \
            [pd.Series, Dict[str, int]]:
        """
        Imports a .csv file to a DateFrame, cleans and join all text values from a chosen column and counts the
        occurrences of every word with length more than 2 chars

        :param path: the archive file path from which the function will get the data
        :param columns: Title or Article (to count the words in a specific column)
        :param name: output file name
        :param output_choice: True by default for dataframes (False if data is in dictionary format)
        :return: sorted in desc order dictionary/series with the word as a key
        and the number of the occurrences as a value:
                    {'жената': 24, 'това': 23, 'калоян': 21, 'жена': 21, 'като': 20, 'полицията': 19,...}
        """
        df = Import.import_to_df(path)
        for i in range(len(columns)):
            column = columns[i]
            text_list = [row.lower() for row in df[column]]
            text_join = " ".join(text for text in text_list)
            text = re.sub(r'[\d]', "", text_join)

            tokenizer = RegexpTokenizer(r'[\w]{3,}')
            words = tokenizer.tokenize(text)

            if output_choice:
                occurrences_sr = pd.Series(FreqDist(words), dtype='object')
                sorted_occurrences_sr = occurrences_sr.sort_values(ascending=False)
                Export.sr_to_csv(sorted_occurrences_sr, name, f"{name}_{column}_words_stats")
            else:
                occurrences_dict = pd.Series(FreqDist(words), dtype='object').to_dict()
                sorted_occurrences_dict = dict(sorted(occurrences_dict.items(), key=lambda x: -x[1]))
                df = Export.dict_to_df(sorted_occurrences_dict)
                Export.df_to_csv(f"{name}_{column}_words_stats")
