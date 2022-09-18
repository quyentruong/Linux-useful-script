tree -Dnfit -I "*.txt|*.html" -o "$PWD/path.txt"
tree -DC -I "*.txt|*.html" -H "$PWD" "$PWD" -o "$PWD/nice.html"
tree -DCfit -I "*.txt|*.html" -H "$PWD" "$PWD" --nolinks -o "$PWD/path.html"