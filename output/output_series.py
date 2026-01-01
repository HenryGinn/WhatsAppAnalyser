import matplotlib.pyplot as plt
import pandas as pd
from hgutilities.utils import get_file_name

from Output.output import Output


class OutputSeries(Output):
    
    def output_series(self, s, name, y_label=None, lower_limit=10):
        s = pd.Series(s.iloc[:, 0]).copy()
        self.file_name = self.get_series_file_name(name)
        self.output_series_to_text(s, name, lower_limit)
        self.output_series_to_bar(s, name, y_label)

    def output_series_to_text(self, s, name, lower_limit):
        s_text = s[s >= lower_limit]
        self.save_text(s_text, self.file_name)

    def get_series_file_name(self, name):
        file_name = get_file_name({
            "Quantity": name, "Start": self.start_date,
            "End": self.end_date}, timestamp=False)
        return file_name

    def output_series_to_bar(self, s, name, y_label):
        s_bar = s.iloc[:50]
        self.initialise_figure()
        self.ax.bar(s_bar.index, s_bar.values, color=self.color_1)
        self.set_bar_peripherals(self.ax, name, y_label)
        self.output_figure(self.file_name)
