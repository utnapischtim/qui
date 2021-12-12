# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Christoph Ladurner

import json
import os
import sys
from collections import OrderedDict
from dataclasses import dataclass
from os.path import isfile
from pathlib import Path
from pprint import pprint

import click
import jq
import matplotlib.pyplot as plt


class JSONFile(click.File):
    """JSONFile provides the ability to load a json file."""

    name = "JSON_FILE"

    def convert(self, value, param, ctx):
        """This method converts the json file to the dictionary representation."""
        input_file = super().convert(value, param, ctx)

        try:
            return json.load(input_file)
        except Exception as e:
            click.secho(e.msg, fg="red")
            click.secho("The input file is not a valid JSON File", fg="red")
            return


def plot(x, y):
    plt.plot(x, y)
    plt.xlabel("x - axis ")
    plt.ylabel("y - axis")
    plt.title("My first graph!")
    plt.show()


def load(filename):
    with open(filename, "r") as fp:
        return json.load(fp)


@click.group()
@click.version_option()
def qui():
    """Initialize CLI context."""


@qui.command()
@click.option("--input-dir", type=click.Path(), required=True)
def find_biggest(input_dir):
    biggest = 0
    biggest_filename = ""

    for filename in os.listdir(input_dir):
        filepath = f"{input_dir}/{filename}"
        if not isfile(filepath):
            continue

        obj = load(filepath)
        if (t := obj["globalInformations"]["sizes"]["motorcycles"]) > biggest:
            biggest = t
            biggest_filename = filepath

    print(biggest_filename)


@dataclass
class Dist:
    file_path: str
    diff: float
    vel_a: dict
    vel_b: dict


@qui.command()
@click.option("--input-dir", type=click.Path(), required=True)
@click.option("--output-file", type=click.STRING, default="")
def motorcycle_velocity_distribution(input_dir, output_file):
    slowest_diffs = [10]
    # fastest_diffs = [Dist("", 0)]
    fastest_diffs = []

    for filename in os.listdir(input_dir):

        file_path = f"{input_dir}/{filename}"
        if not isfile(file_path):
            continue
        # print(file_path)
        obj = load(file_path)
        velocities = jq.compile(".motorcycles[].velocity").input(obj).all()

        try:
            velocities.sort()
        except TypeError:
            print(f"file_path: {file_path}")
            continue

        # if len(velocities) < 10:
        #     print(filepath)
        #     continue

        # if slowest_diffs[len(slowest_diffs)].diff > (velocities[0] - velocities[1]):
        # size = obj["globalInformations"]["sizes"]["motorcycles"]
        # size = len(velocities)
        # pprint(velocities)
        # print(size)
        # print(velocities[size - 1])
        # print(velocities[size - 2])
        # if (diff := velocities[size - 1] - velocities[size - 2]) >= fastest_diffs[
        #     len(fastest_diffs) - 1
        # ].diff and diff > 0.00000000001:
        #     fastest_diffs.append(Dist(file_path, diff))
        #     fastest_diffs.sort(key=lambda o: o.diff, reverse=True)

        # if len(fastest_diffs) > 10:
        #     fastest_diffs.pop()
        size = len(velocities)
        diff = velocities[size - 1] - velocities[size - 2]
        vel_a = velocities[size - 1]
        vel_b = velocities[size - 2]
        fastest_diffs.append(Dist(file_path, diff, vel_a, vel_b))

    if output_file:
        with open(output_file, "w") as fp:
            json.dump(fastest_diffs, fp)
    else:
        pprint(fastest_diffs)


@qui.command()
@click.option("--input-file", required=True)
def fix_null(input_file):
    with open(input_file, "r") as fp:
        obj = json.load(fp)

    # print(input_file)
    # pprint(list(filter(lambda m: m["velocity"] is None, obj["motorcycles"])))

    obj["motorcycles"] = list(
        filter(lambda m: m["velocity"] is not None, obj["motorcycles"])
    )

    with open(input_file, "w") as fp:
        json.dump(obj, fp)


@qui.command()
@click.option("--data-a", type=JSONFile("r"), required=True)
@click.option("--data-b", type=JSONFile("r"), required=True)
@click.option("--output", type=click.File("w"))
def compare(data_a, data_b, output):
    orders_a = [[obj["text"] for obj in experiment] for experiment in data_a]
    orders_b = [
        [obj["text"] for obj in experiment["reductionCounterInformation"]]
        for experiment in data_b["list"]
    ]

    json.dump(orders_a, output)


@qui.command()
@click.option("--data", type=JSONFile("r"), required=True)
@click.option("--do-plot", type=bool, is_flag=True)
def added_by_index(data, do_plot):
    histo = {}

    for reflex_node_count in data:
        for i, key in enumerate(sorted(map(int, data[reflex_node_count].keys()))):
            if i not in histo:
                histo[i] = 0
            histo[i] += data[reflex_node_count][str(key)]

    if do_plot:
        x = histo.keys()
        y = histo.values()

        plt.plot(x, y)
        plt.xlabel("x - axis added by index")
        plt.ylabel("y - axis how often")
        plt.title("added by index!")
        plt.show()
    else:
        pprint(histo)


@qui.command()
@click.option("--data", type=JSONFile("r"), required=True)
def nested_histogram(data):
    # x = [i for i in range(1, 70)]
    # y = [i for i in range(0, 80000)]

    x_axis_max = 0

    for reflex_node_count in data:
        if int(reflex_node_count) % 100 != 0:
            continue

        obj = data[reflex_node_count]

        # x = list(int(i) for i in obj.keys())
        x = list(map(int, obj.keys()))
        x.sort()

        if x_axis_max < max(x):
            x_axis_max = max(x)

        y = list(int(obj[str(i)]) for i in x)

        plt.plot(x, y)

    plt.xticks(list(i for i in range(0, x_axis_max + 2) if i % 2 == 0))

    plt.xlabel("x - axis added by reflex node count")
    plt.ylabel("y - axis how often")
    plt.title("added by index!")
    plt.show()


@qui.command()
@click.option("--data", type=JSONFile("r"), required=True)
@click.option("--do-plot", type=bool, is_flag=True)
def histogram(data, do_plot):
    histo = {}

    for reflex_node_count in data:
        for k, v in data[reflex_node_count].items():
            if k not in histo:
                histo[k] = 0

            histo[k] += v

    ordered_histo = OrderedDict(
        [(key, histo[str(key)]) for key in sorted(map(int, histo.keys()))]
    )

    if do_plot:
        x = ordered_histo.keys()
        y = ordered_histo.values()

        plt.plot(x, y)
        plt.xlabel("x - axis added by reflex node count")
        plt.ylabel("y - axis how often")
        plt.title("added by index!")
        plt.show()
    else:
        pprint(ordered_histo)


@qui.command()
@click.option("--input-dir", type=click.Path(exists=True))
def fix_output_format(input_dir):
    pathlist = Path(input_dir).rglob("*.json")

    for path in pathlist:
        with open(path) as fp:
            obj = json.load(fp)

        if "list" in obj:
            if "reductionCounterInformation" in obj["list"][0]:
                if isinstance(obj["list"][0]["reductionCounterInformation"], dict):
                    print(f"to nested path: {path}")
                    obj["list"] = [
                        o["reductionCounterInformation"] for o in obj["list"]
                    ]
                    with open(path, "w") as fp:
                        json.dump(obj, fp)

        if "globalInformations" in obj:
            continue

        output_obj = {
            "list": [{"reductionCounterInformation": a, "duration": 0} for a in obj],
            "globalInformations": {
                "sizes": {"motorcycles": 0, "intersections": 0},
                "performance": {
                    "motorcycles": 0,
                    "intersectionCache": 0,
                    "calculateRandomLists": 0,
                },
            },
        }

        with open(path, "w") as fp:
            json.dump(output_obj, fp)


# @click.option("--data", type=JSONFile("r"), required=True)
@qui.command()
@click.option("--input-dir", type=click.Path(exists=True))
@click.option("--output-file", type=click.File("w+"), default="-")
def run(input_dir, output_file):
    pathlist = Path(input_dir).rglob("*.json")
    biggest_reduction_counter = 0
    histogram = {}

    for path in pathlist:
        with open(path) as fp:
            obj = json.load(fp)
        for k in obj["list"]:
            try:
                biggest_t = max(
                    o["reductionCounter"] for o in k["reductionCounterInformation"]
                )
            except TypeError:
                print(f"TypeError: path {path}")
                sys.exit()

            reflex_node_count = len(k["reductionCounterInformation"])
            if reflex_node_count not in histogram:
                histogram[reflex_node_count] = {}
            if biggest_t not in histogram[reflex_node_count]:
                histogram[reflex_node_count][biggest_t] = 0
            histogram[reflex_node_count][biggest_t] += 1

            if biggest_t > biggest_reduction_counter:
                biggest_reduction_counter = biggest_t
                json.dump(k, output_file)
                print(
                    f"reflex_node_count: {reflex_node_count}, \
                    biggest: {biggest_reduction_counter}, \
                    duration: {k['duration']}, \
                    filename: {str(path)}"
                )

    # print("")
    # pprint(histogram)

    json.dump(histogram, output_file)
