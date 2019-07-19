from typing import List

import numpy as np
import PySimpleGUI as pSG

from job import Job
from server import get_servers_from_system

svrs = get_servers_from_system("config100.xml.your.log", "config100.xml")

l_width = 5
width = 1200
height = len(svrs) * l_width * 2.5
w_width = 1300
w_height = 760
margin = 30
end_time = 86400


column = [
    [pSG.Graph(canvas_size=(w_width, height), graph_bottom_left=(0, 0), graph_top_right=(w_width, height), key="graph")]
]

layout = [
    [pSG.Column(column, size=(w_width, w_height - 22), scrollable=True, vertical_scroll_only=True,
                background_color="whitesmoke")]
]

window = pSG.Window("sim-viz", layout, size=(w_width, w_height), background_color="whitesmoke", resizable=True)
window.Finalize()
graph = window.Element("graph")


def norm(jobs: List[Job]) -> List[Job]:
    if not jobs:
        return []

    arr = np.array([(j.start, j.end) for j in jobs])
    arr = np.interp(arr, (0, end_time), (margin * 2, width - margin))

    return [Job(j.jid, j.cores, j.schd, start, end)
            for (start, end), j in zip([(int(i), int(k)) for (i, k) in arr], jobs)]


def draw():
    for i, s in enumerate(svrs):
        y = height - margin - l_width * 2 * i
        graph.DrawText("{} {}".format(s.kind, s.sid), (margin, y))

        for j in norm(s.jobs):
            graph.DrawLine((j.start + margin, y), (j.end, y), width=l_width)


draw()

while True:
    event, values = window.Read()
