#!/bin/bash
set -e
set -u
set -o pipefail

if [ $# -eq 0 ]; then
	echo "No parameters were passed to the script."
	exit 1
fi

file_name=$1

# record
asciinema rec --cols 100 --rows 24 -t "$file_name" "$file_name".cast
# to gif
agg --theme monokai --font-size 40 --speed 2 "$file_name".cast "$file_name".gif
