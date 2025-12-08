from os.path import join
from os import listdir
from json import load

import pandas as pd

from Processing.base import Base


class PreprocessSpotify(Base):

    column_processing_dict = {
        "ts": {"Type": "object", "Name": "Timestamp"},
        "platform": {"Type": "category", "Name": "Platform"},
        "ms_played": {"Type": "int", "Name": "TimePlayed"},
        "master_metadata_track_name": {"Type": "object", "Name": "Track"},
        "master_metadata_album_artist_name": {"Type": "object", "Name": "Artist"},
        "master_metadata_album_album_name": {"Type": "object", "Name": "Album"},
        "spotify_track_uri": {"Type": "object", "Name": "URI"},
        "reason_start": {"Type": "category", "Name": "ReasonStart"},
        "reason_end": {"Type": "category", "Name": "ReasonEnd"},
        "shuffle": {"Type": "bool", "Name": "Shuffle"},
        "skipped": {"Type": "bool", "Name": "Skipped"},
        "offline": {"Type": "bool", "Name": "Offline"},}

    def preprocess(self):
        self.collect_history_paths()
        self.populate_dataframe()
        self.postprocess_dataframe()
        self.output_dataframe()


    # Construction of dataframe

    def collect_history_paths(self):
        self.paths_history = [
            join(self.path_base, file_name)
            for file_name in listdir(self.path_base)
            if "Streaming_History" in file_name]

    def populate_dataframe(self):
        dataframes = []
        for path in self.paths_history:
            with open(path, "r") as file:
                dataframes.append(pd.read_json(file))
        self.df = pd.concat(dataframes)

    def postprocess_dataframe(self):
        self.postprocess_dataframe_drop_columns()
        self.postprocess_dataframe_set_types()
        self.postprocess_dataframe_rename_columns()
        self.postprocess_dataframe_add_count_column()
        self.postprocess_dataframe_set_index()

    def postprocess_dataframe_drop_columns(self):
        columns_to_drop = [column for column in self.df.columns.values
                           if column not in self.column_processing_dict]
        self.df = self.df.drop(columns=columns_to_drop)

    def postprocess_dataframe_set_types(self):
        types_dict = {key: value["Type"] for key, value in
                      self.column_processing_dict.items()}
        self.df = self.df.astype(types_dict)
        self.df["ts"] = pd.to_datetime(
            self.df["ts"], format="%Y-%m-%dT%H:%M:%SZ")
        
    def postprocess_dataframe_rename_columns(self):
        names_dict = {key: value["Name"] for key, value in
                      self.column_processing_dict.items()}
        self.df = self.df.rename(columns=names_dict)

    def postprocess_dataframe_add_count_column(self):
        self.df.loc[:, "Count"] = 1
        self.df = self.df.astype({"Count": "int"})

    def postprocess_dataframe_set_index(self):
        self.df = self.df.set_index("Timestamp")
        self.df = self.df.sort_index()


    # Output and input

    def output_dataframe(self):
        self.df.to_pickle(self.path_dataframe)
        df = self.df.astype("string").replace(',', ' ', regex=True)
        df.to_csv(self.path_csv)
        self.filter_time()

    def read(self):
        self.df = pd.read_pickle(self.path_dataframe)
        self.filter_time()
