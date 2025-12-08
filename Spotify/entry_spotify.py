from os.path import join

from hgutilities import defaults
from hgutilities.utils import make_folder

from Output.output import Output
from Output.time_series import TimeSeries


class Entry(TimeSeries):

    def __init__(self, spotify, attribute, name):
        self.set_attributes(spotify, attribute, name)
        self.set_df()
        self.set_path()

    def set_attributes(self, spotify, attribute, name):
        self.spotify = spotify
        self.attribute = attribute
        self.name = name
        self.inherit_from_spotify()

    def inherit_from_spotify(self):
        kwargs = ["output", "title_date"]
        defaults.inherit(self, self.spotify, kwargs)

    def set_df(self):
        self.df = self.spotify.df.loc[
            self.spotify.df[self.attribute] == self.name]
        self.df = self.df.drop(columns=self.attribute)

    def set_path(self):
        self.path_output = join(self.spotify.path_output,
                                self.attribute, self.name)
        make_folder(self.path_output)

    def plot_date(self):
        name = f"Listening History of '{self.name}'"
        self.plot_time_series_date(
            self.df, name, "Date", "Frequency Density")

    def plot_day(self):
        name = f"Listening History Over a Day of '{self.name}'"
        self.plot_time_series_day(
            self.df, name, "Time", "Frequency Density")

defaults.load(Entry)
