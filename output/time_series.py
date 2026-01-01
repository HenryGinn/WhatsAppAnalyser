from hgutilities import defaults
import matplotlib.dates as mdates
import pandas as pd

from Output.output import Output


class TimeSeries(Output):

    def plot_time_series_date(self, df, name, x_label, y_label):
        self.initialise_figure()
        df = self.get_time_series_date(df)
        self.ax.plot(df, color=self.color_1)
        self.set_peripherals(self.ax, df, name, x_label, y_label)
        self.output_figure(name)

    def get_time_series_date(self, df):
        df = df.loc[:, "Count"].copy()
        df = df.resample("D").sum()
        df = df.rolling(14, center=True).mean().dropna()
        return df

    def plot_time_series_day(self, df, name, x_label, y_label):
        self.initialise_figure()
        df = self.get_time_series_day(df)
        self.ax.plot(df, color=self.color_1)
        self.set_peripherals(self.ax, df, name, x_label, y_label)
        self.output_figure(name)

    def get_time_series_day(self, df):
        df = df.set_index(df.index.time).copy()
        df = df.loc[:, "Count"]
        df.index = pd.to_datetime(df.index, format="%H:%M:%S")
        df = df.resample("10min").sum()
        df = df.rolling(6, center=True).mean().dropna()
        self.spotify.a = df
        return df

    def set_ticks(self, ax, df):
        if df.index[-1] - df.index[0] < pd.Timedelta(days=1):
            locator = mdates.AutoDateLocator()
            formatter = mdates.DateFormatter('%H:%M')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            self.fig.autofmt_xdate()


defaults.load(TimeSeries)
