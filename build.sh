#!/bin/bash

set -euo pipefail

# clean build
rm -rf build/ 

cp -R src/ build/
rm -rf build/blogs/

venv/bin/python scripts/mdparser.py src/blogs/ \
    --out build/blogs/ \
    --template templates/template.html

echo "Build successful!"
