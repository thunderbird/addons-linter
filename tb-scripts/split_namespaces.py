import json
import os
from json import JSONDecodeError

import json5


def get_schemas(directory):
    files = os.listdir(directory)
    for file in files:
        if ".json" not in file:
            continue

        print(f"Checking {file}")

        with open(f"{directory}/{file}", 'r') as fh:
            data = fh.read()
            try:
                data = json5.loads(data)
            except JSONDecodeError as ex:
                print(f"Error reading {file}: {ex.msg}")

            # Grab a copy of the manifest if avail
            # If there's more than one non-manifest namespace, make copy dict of manifest + that one

            schema_files = []

            if len(data) > 1:
                manifest = {}
                for (index, schema) in enumerate(data):
                    if schema['namespace'] == 'manifest':
                        manifest = schema
                        continue

                    schema_files.append([
                        manifest,
                        schema
                    ])

            if len(schema_files) > 1:
                for schemas in schema_files:
                    schema = schemas[1]
                    with open(f"{directory}../out/{schema['namespace']}.json", 'w+') as fw:
                        fw.write(json.dumps(schemas))
            else:
                # Otherwise copy the file over!
                with open(f"{directory}../out/{file}", 'w+') as fw:
                    fw.write(json.dumps(data))



            data = data

if __name__ == '__main__':
    get_schemas('/home/melissaa/Dev/mozilla/comm-thunderbird/source/comm/mail/components/extensions/schemas/old/')
    pass