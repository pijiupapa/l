# -*- coding=utf-8 -*-
import argparse
import sys
from importlib import import_module

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('work_file')
    options = parser.parse_args()
    module_path = 'cron.' + options.work_file
    module = import_module(module_path)
