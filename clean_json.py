import json
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "rt") as f:
    input_data = json.loads(f.read())

for elem in input_data:
    if "index" in elem:
        del elem["index"]
    if "note" in elem:
        done = False
        urls = []
        while not done:
            url_index = elem["note"].find("http")
            if url_index >= 0:
                newline_index = elem["note"][url_index:].find("\n")
                if newline_index >= 0:
                    newline_index += url_index
                    url = elem["note"][url_index:newline_index]
                    elem["note"] = elem["note"][:url_index] + elem["note"][newline_index + 1:]
                else:
                    url = elem["note"][url_index:]
                    elem["note"] = elem["note"][:url_index]
                urls.append(url)
            else:
                done = True
        if len(urls) > 0:
            elem["website"] = "\n".join(urls)
        if len(elem["note"]) > 0 and elem["note"][-1] == "\n":
            elem["note"] = elem["note"][:-1]
        if len(elem["note"]) == 0:
            del elem["note"]

with open(output_file, "wt") as f:
    f.write(json.dumps(input_data, indent=2))
