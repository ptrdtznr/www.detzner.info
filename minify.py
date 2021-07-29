import htmlmin
from pathlib import Path

input_file = Path('index.html').read_text()

minified = htmlmin.Minifier().minify(input_file)

with open("index.min.html", 'w') as out:
    out.write(minified)
