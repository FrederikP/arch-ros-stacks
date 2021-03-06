#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    echo ""
    echo "Makes sure that all python scripts use the python2 command"
    exit 1
fi

for file in $(grep -rl -e 'env python *$' -e 'bin/python *$' $1); do
    if [ -z "$file" ]; then
        echo "Error finding files."
        exit 1
    fi
    sed -i 's,env python *$,env python2,g' $file
    sed -i 's,/usr/bin/python *$,/usr/bin/env python2,g' $file
done

