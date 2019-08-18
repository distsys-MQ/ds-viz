import math
import os
from operator import attrgetter
from typing import Dict, List, Tuple

import PySimpleGUI as sg

from job import Job
from server import get_servers_from_system, traverse_servers, Server, get_results


class Visualisation:
    def __init__(self, config: str, failures: str, log: str, c_height: int = 4, scale: int = 0):
        fnt_f = "Courier New"
        fnt_s = -13
        sg.SetOptions(font=(fnt_f, fnt_s), background_color="whitesmoke", element_padding=(0, 0), margins=(1, 1))

        self.servers = get_servers_from_system(log, config, failures)
        self.s_list = [s for s in traverse_servers(self.servers)]  # Replace with calls to traverse_servers
        self.unique_jids = sorted({j.jid for s in self.s_list for j in s.jobs})
        self.jobs = {
            jid: sorted([j for s in self.s_list for j in s.jobs if j.jid == jid], key=attrgetter("schd"))
            for jid in self.unique_jids
        }  # type: Dict[int, List[Job]]
        self.j_graph_ids = {jid: [] for jid in self.unique_jids}  # type: Dict[int, List[Tuple[int, str]]]

        self.max_scale = int(math.log(max(s.cores for s in self.s_list), 2))
        self.base_scale = min(scale, self.max_scale)
        self.s_factor = 2 ** self.base_scale

        menu_offset = 50
        self.height = sum(min(s.cores, self.s_factor) for s in self.s_list) * c_height + menu_offset
        self.width = 1200

        # The following variables are just used to create the window
        tab_size = (75, 3)

        graph_column = [
            [sg.Graph(canvas_size=(self.width, self.height), graph_bottom_left=(0, self.height),
                      graph_top_right=(self.width, 0), change_submits=True, drag_submits=False,
                      background_color="whitesmoke", key="graph")]]
        left_tabs = sg.TabGroup(
            [[sg.Tab("Current Server",
                     [[sg.T("", size=tab_size, key="current_server")]]),
              sg.Tab("Current Job",
                     [[sg.T("", size=tab_size, key="current_job")]])
              ]]
        )
        right_tabs = sg.TabGroup(
            [[sg.Tab("Current Results",
                     [[sg.T("", size=tab_size, key="current_results")]]),
              sg.Tab("Final Results",
                     [[sg.Multiline(get_results(log), font=(fnt_f, fnt_s + 2), size=tab_size, disabled=True)]])
              ]]
        )

        dum_win = sg.Window("dummy", [[]]).Finalize()
        mon_height = dum_win.GetScreenDimensions()[1]
        dum_win.Close()
        w_height = int(mon_height * 0.9)

        btn_width = 8
        btn_font = (fnt_f, fnt_s + 3)
        slider_settings = {
            "size": (105, 5),
            "orientation": "h",
            "enable_events": True
        }
        slider_label_size = (6, 1)

        layout = [
            [left_tabs, right_tabs],
            [sg.Button("Show Job", size=(btn_width, 1), font=btn_font, button_color=("white", "red"), key="show_job"),
             sg.T("Visualising: {}".format(os.path.basename(log)),
                  size=(99, 1), font=(fnt_f, fnt_s, "underline"), justification="center"),
             sg.T("Scale: {} ({} max cores)".format(self.base_scale, 2 ** self.base_scale),
                  size=(30, 1), justification="right", key="scale"),
             sg.Btn('-', size=(int(btn_width / 2), 1), font=btn_font, key="decrease_scale"),
             sg.Btn('+', size=(int(btn_width / 2), 1), font=btn_font, key="increase_scale")],
            [sg.T("Server", size=slider_label_size),
             sg.Slider((0, len(self.s_list) - 1), default_value=self.s_list[0].sid, key="server_slider",
                       **slider_settings)],
            [sg.T("Job", size=slider_label_size),
             sg.Slider((self.unique_jids[0], self.unique_jids[-1]), default_value=self.unique_jids[0], key="job_slider",
                       **slider_settings)],
            [sg.T("Time", size=slider_label_size),
             sg.Slider((0, Server.last_time), default_value=0, key="time_slider", **slider_settings)],
            [sg.Column(graph_column, size=(self.width, w_height), scrollable=True, vertical_scroll_only=True,
                       key="column")]
        ]

        self.left_margin = 30
        self.right_margin = 15

        self.window = sg.Window("sim-viz", layout, size=(self.width + self.left_margin, w_height), resizable=True,
                                return_keyboard_events=True)
        self.window.Finalize()

        # Not necessary for creating window, but needed for drawing visualisation in graph and handling user input
        # Could create other classes to handle these
        self.x_offset = self.left_margin * 2
        self.norm_time = self.x_offset
        self.timeline = None
        self.s_index = 0
        self.s_ticks = []
        self.highlight_x1 = self.x_offset - 10
        self.s_highlight = None

        # Can be local variables in main loop
        # prev_jid = unique_jids[0]
        # show_job = False
        # cur_scale = base_scale
        # server = s_list[0]
        # job = j_dict[unique_jids[0]][0]
        # time = 0
