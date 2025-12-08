import os

import numpy as np
import pandas as pd


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

    def set_path(self):
        self.path = os.path.join(
            self.service.path,
            self.name)

    def load_messages(self):
        raise Exception(
            f"load_messages method not implemented for {service}")

    def set_summary(self):
        self.set_word_count()
        self.set_character_count()
        self.init_summary()
        self.set_message_count()
        self.set_photo_count()
        self.set_totals_means_stds()
        self.summary.fillna(0, inplace=True)

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
        return totals

    def get_means(self):
        means = (
            self.messages
            .loc[:, ["Sender", "Word Count", "Character Count"]]
            .groupby("Sender")
            .mean())
        return means

    def get_stds(self):
        stds = (
            self.messages
            .loc[:, ["Sender", "Word Count", "Character Count"]]
            .groupby("Sender")
            .std())
        return stds
