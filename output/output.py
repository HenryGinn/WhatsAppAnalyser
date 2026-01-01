from os.path import join

import matplotlib.pyplot as plt
from hgutilities import defaults
from utils import add_line_breaks


class Output():

    # Initialisation and preprocessing

    def set_title_date(self):
        start = self.start_date.strftime('%B %Y')
        end = self.end_date.strftime('%B %Y')
        self.title_date = f"From {start} to {end}"

    def initialise_figure(self):
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_axes(rect=self.rect)


    # Peripherals

    def set_peripherals(self, ax, df, name, x_label, y_label):
        self.set_tick_labels(ax)
        self.set_ticks(ax, df)
        self.set_title(ax, name)
        self.set_axis_labels(ax, x_label, y_label)
    
    def set_bar_peripherals(self, ax, name, y_label):
        self.set_bar_tick_labels(ax)
        self.set_title(ax, name)
        self.set_axis_labels(ax, y_label=y_label)

    def set_tick_labels(self, ax):
        ax.set_xticks(ax.get_xticks())
        ax.set_yticks(ax.get_yticks())
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=self.fontsize_ticks)
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=self.fontsize_ticks)

    def set_bar_tick_labels(self, ax):
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), rotation=60,
                           ha='right', fontsize=self.fontsize_ticks)

    def set_ticks(self, ax, df):
        pass

    def set_title(self, ax, name):
        title = add_line_breaks(f"{name} {self.title_date}", length=60)
        ax.set_title(title, fontsize=self.fontsize_title)

    def set_axis_labels(self, ax, x_label=None, y_label=None):
        ax.set_xlabel(x_label, fontsize=self.fontsize_axis)
        ax.set_ylabel(y_label, fontsize=self.fontsize_axis)


    # Output

    def output_figure(self, file_name):
        match self.output:
            case "show": plt.show()
            case "save": self.save_figure(file_name)

    def save_figure(self, file_name):
        file_name = file_name.replace("\'", "")
        path = join(self.path_output, f"{file_name}.pdf")
        plt.savefig(path, bbox_inches="tight", format="pdf")
        plt.close("all")

    def save_text(self, df, file_name):
        file_name = file_name.replace("\'", "")
        path = join(self.path_output, f"{file_name}.txt")
        with open(path, "w+") as file:
            file.write(df.to_string())

defaults.load(Output)
