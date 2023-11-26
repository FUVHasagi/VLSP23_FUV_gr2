#!/bin/bash
if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
    exit 1
fi
curl -X POST $1:$2/test -H "Content-Type: text/xml" --data-binary "@$3"
