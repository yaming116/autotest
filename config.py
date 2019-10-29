#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os import path
from tools.date_utils import current_time_path

project_root = path.abspath(os.path.dirname(__file__))
case_name = current_time_path()
case_logs = path.join(project_root, 'logs', case_name)

# performance
network = path.join(case_logs, 'network.json')
fps = path.join(case_logs, 'fps.json')
cpu = path.join(case_logs, 'cpu.json')
memory = path.join(case_logs, 'memory.json')


