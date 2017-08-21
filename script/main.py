# -*- coding=utf-8 -*-
import sys
import argparse
import importlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="must be script")
    parser.add_argument("script_path", help="script path to execute")
    options = parser.parse_known_args(sys.argv[1:])[0]
    module_path = options.script_path[:-3].replace('/', '.')
    module = importlib.import_module(module_path)
    executor_cls = getattr(module, "Executor")
    executor = executor_cls(sys.argv[3:])
    executor.execute()
