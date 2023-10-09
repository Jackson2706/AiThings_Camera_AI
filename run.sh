#!/bin/bash
python app.py 1>stdout_1.txt 2>stderr_1.txt & python violation_processing.py 1>stdout_2.txt 2>stderr_2.txt