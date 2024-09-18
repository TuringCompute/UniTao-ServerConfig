#!/usr/bin/env python3

import sys
from lib.utilities import Util


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: veth.py < <json_file_path>")
        sys.exit(-1)

    file_path = sys.argv[1]
    json_data = Util.read_json_file(file_path)