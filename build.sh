#!/bin/bash

set -euo pipefail

# clean build
rm -rf build/ 

cp -R src/ build/
rm -rf build/blogs/

python3 scripts/mdparser.py src/blogs/ \
    --out build/blogs/ \
    --template templates/blog-template.html

echo "Build successful!"
