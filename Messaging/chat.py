import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import append_to_column_names


class Chat():

    conversion_dict = {
        "Sender": pd.StringDtype(),
        "Timestamp": "datetime64[ms]",
        "Message": pd.StringDtype(),
        "Geoblocked": np.bool,
        "Unsent": np.bool}

    def __init__(self, service, name):
        self.service = service
        self.name = name
        self.set_path()
        self.create_output_folder()

    def set_path(self):
        self.path = os.path.join(
            self.service.path,
            self.name)

    def create_output_folder(self):
        self.set_output_path()
        if not os.path.exists(self.output_path):
            os.makedir(self.output_path)

    def set_output_path(self):
        self.output_path = os.path.join(
            self.service.output_path,
            self.name)

    def load_messages(self):
        raise Exception(
            f"load_messages method not implemented for {self.service}")


    # Summary stats

    def set_summary(self):
        self.set_word_count()
        self.set_character_count()
        self.init_summary()
        self.set_message_count()
        self.set_photo_count()
        self.set_totals_means_stds()
        self.summary.fillna(0, inplace=True)
        self.summary.sort_values("Messages Sent", inplace=True)

    def set_word_count(self):
        self.messages["Word Count"] = (
            self.messages["Message"]
            .apply(lambda x: len(x.split())))

    def set_character_count(self):
        self.messages["Character Count"] = (
            self.messages["Message"]
            .apply(lambda x: len(x)))

    def init_summary(self):
        self.summary = pd.DataFrame(index=self.messages["Sender"].unique())

    def set_message_count(self):
        self.summary["Messages Sent"] = (
            self.messages
            .groupby("Sender")
            .count()["Message"])

    def set_photo_count(self):
        self.summary["Photos Sent"] = (
            self.photos
            .groupby("Sender")
            .count()
            .iloc[:, 0])

    def set_totals_means_stds(self):
        totals = self.get_totals()
        means = self.get_means()
        stds = self.get_stds()
        self.summary = pd.concat((self.summary, totals, means, stds), axis=1)

    def get_totals(self):
        totals = (
            self.messages
            .loc[:, ["Sender", "Word Count", "Character Count"]]
            .groupby("Sender")
            .sum())
        append_to_column_names(totals, " Total")
        return totals

    def get_means(self):
        means = (
            self.messages
            .loc[:, ["Sender", "Word Count", "Character Count"]]
            .groupby("Sender")
            .mean())
        append_to_column_names(means, " Mean")
        return means

    def get_stds(self):
        stds = (
            self.messages
            .loc[:, ["Sender", "Word Count", "Character Count"]]
            .groupby("Sender")
            .std())
        append_to_column_names(stds, " Std")
        return stds

    def output_summary_text(self):
        self.set_output_summary_text_path()
        with open(self.summary_text_path, "w+") as file:
            file.write(self.summary.to_string())

    def set_output_summary_text_path(self):
        self.summary_text_path = os.path.join(
            self.output_path,
            "Summary.txt")

    def output_summary_plot(self):
        self.set_output_summary_plot_path()
        self.init_summary_plot()
        self.summary_plot = self.summary.iloc[:10, :]
        self.plot_summaries()
        plt.savefig(self.summary_plot_path, dpi=600)

    def set_output_summary_plot_path(self):
        self.summary_plot_path = os.path.join(
            self.output_path,
            "Summary.png")

    def init_summary_plot(self):
        self.fig, self.axes = plt.subplots(figsize=(12, 7), nrows=2, ncols=4)
        self.axes = self.axes.T.flatten()
        self.fig.subplots_adjust(
            top=0.92, bottom=0.1, right=0.99,
            left=0.04, hspace=0.35, wspace=0.2)
        self.fig.suptitle(self.name, fontsize=12)
        
    def plot_summaries(self):
        for ax, attribute in zip(self.axes, self.summary):
            self.plot_summary(ax, attribute)
            ax.set_title(attribute, fontsize=10)
            ax.tick_params(axis='x', labelrotation=30, labelsize=6)
            ax.tick_params(axis='y', labelsize=6)

    def plot_summary(self, ax, attribute):
        ax.bar(
            self.summary_plot.index,
            self.summary_plot[attribute].values,
            color="tab:red")


    # Time series

    def set_activity_day(self):
        pass
