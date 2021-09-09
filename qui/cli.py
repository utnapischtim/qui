# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Christoph Ladurner


import json
from pathlib import Path
from pprint import pprint

import click


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


@click.group()
@click.version_option()
def qui():
    """Initialize CLI context."""


# @click.option("--data", type=JSONFile("r"), required=True)
@qui.command()
@click.option("--input-dir", type=click.Path(exists=True))
def run(input_dir):
    pathlist = Path(input_dir).rglob("*.json")
    biggest_reduction_counter = 0
    histogram = {}

    for path in pathlist:
        with open(path) as fp:
            obj = json.load(fp)
            for k in obj:
                biggest_t = max(o["reductionCounter"] for o in k)
                reflex_node_count = len(k)
                if reflex_node_count not in histogram:
                    histogram[reflex_node_count] = {}
                if biggest_t not in histogram[reflex_node_count]:
                    histogram[reflex_node_count][biggest_t] = 0
                histogram[reflex_node_count][biggest_t] += 1

                if biggest_t > biggest_reduction_counter:
                    biggest_reduction_counter = biggest_t
                    print(
                        f"reflex_node_count: {reflex_node_count}, biggest: {biggest_reduction_counter}, filename: {str(path)}"
                    )

    print("")
    pprint(histogram)

    with open("outfile.json", "w") as fp:
        json.dump(histogram, fp)
