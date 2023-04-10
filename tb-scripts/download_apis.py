import argparse
import json
import os
import shutil
from json import JSONDecodeError
from zipfile import ZipFile

import json5
import requests


def get_schemas(directory, out_directory):
    files = os.listdir(directory)
    for file in files:
        if ".json" not in file:
            continue

        print(f"Checking {file}")

        with open(f"{directory}/{file}", 'r') as fh:
            data = fh.read()
            try:
                # Some schemas have comments...we need to use another library to read these
                data = json5.loads(data)
            except JSONDecodeError as ex:
                print(f"Error reading {file}: {ex.msg}")
                continue

            schema_files = []

            # Grab a copy of the manifest if avail
            # If there's more than one non-manifest namespace, make copy dict of manifest + that one
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

            # If we have more than one schema, write it out as a new file
            if len(schema_files) > 1:
                for schemas in schema_files:
                    schema = schemas[1]
                    with open(f"{out_directory}/{schema['namespace']}.json", 'w+') as fw:
                        fw.write(json.dumps(schemas))
            else:
                # Otherwise copy the file over!
                with open(f"{out_directory}/{file}", 'w+') as fw:
                    fw.write(json.dumps(data))


def download_tip(url, filename):
    print(f"Downloading {url} as {filename}, might take a while")

    with requests.get(url, stream=True) as r:
        with open(filename, "wb") as fh:
            for chunk in r.iter_content(8192):
                if chunk:
                    fh.write(chunk)


def main(working_dir, existing_source_dir, mozilla_central_zip, comm_central_zip):
    archives = [
        (mozilla_central_zip, "mozilla-central"),
        (comm_central_zip, "comm-central")
    ]

    mozilla_central_folder = None
    comm_central_folder = None
    merged_folder = "thunderbird_api"
    base_dir = os.path.join('./', working_dir, 'addons_linter')

    if existing_source_dir is not None:
        mozilla_central_folder = existing_source_dir
        comm_central_folder = os.path.join(existing_source_dir, "comm")
    else:
        for archive in archives:
            filename = os.path.join(working_dir, f"{archive[1]}.zip")
            if not os.path.isfile(filename):
                download_tip(archive[0], filename)

        # Mozilla-Central
        print("Extracting schemas from mozilla-central.zip")
        with ZipFile(os.path.join(working_dir, "mozilla-central.zip"), "r") as mozilla_central:
            name_list = mozilla_central.namelist()
            extract_list = []

            # Grab the folder name
            mozilla_central_folder = name_list[0].split('/')[0]

            for file in name_list:
                if "toolkit/components/extensions/schemas" in file \
                        or "browser/components/extensions/schemas" in file:
                    extract_list.append(file)

            mozilla_central.extractall(base_dir, extract_list)

        # Comm-Central
        print("Extracting schemas from comm-central.zip")
        with ZipFile(os.path.join(working_dir, "comm-central.zip"), "r") as comm_central:
            name_list = comm_central.namelist()
            extract_list = []

            # Grab the folder name
            comm_central_folder = name_list[0].split('/')[0]

            for file in name_list:
                if "mail/components/extensions" in file:
                    extract_list.append(file)

            comm_central.extractall(base_dir, extract_list)

    # Copying schemas over
    print("Copying and merging schemas")

    files = {
        mozilla_central_folder: [
            'toolkit/',
            'browser/components/extensions/schemas/commands.json',
            'browser/components/extensions/schemas/pkcs11.json'
        ],
        comm_central_folder: [
            'mail/components/extensions/'
        ],
    }

    # Copy over the files/folders to our merged folder
    for folder, files in files.items():
        for file in files:
            original_path = os.path.join(base_dir, folder, file)

            # Add the "comm" folder
            if folder == comm_central_folder:
                copy_path = os.path.join(base_dir, merged_folder, "comm", file)
            else:
                copy_path = os.path.join(base_dir, merged_folder, file)

            if os.path.isdir(original_path):
                shutil.copytree(original_path, copy_path, dirs_exist_ok=True)
            else:
                os.makedirs(copy_path, exist_ok=True)
                shutil.copy(original_path, copy_path)

    # Remove the schemas folder, as we need to reprocess it
    schema_folder = os.path.join(base_dir, merged_folder, "comm/mail/components/extensions/schemas")
    shutil.rmtree(schema_folder)
    os.makedirs(schema_folder, exist_ok=True)

    print("Splitting comm-central namespaces")
    get_schemas(os.path.join(base_dir, comm_central_folder, "mail/components/extensions/schemas"), os.path.join(base_dir, merged_folder, "comm/mail/components/extensions/schemas"))

    print("Zipping up")
    # File path (without zip), archive format, folder to zip up
    shutil.make_archive(os.path.join(working_dir, 'thunderbird_api'), "zip", os.path.join(base_dir, merged_folder))

    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thunderbird API Downloader Script")

    parser.add_argument("--working-dir", default=os.getenv("WORKING_DIR", "tmp"), help="Temporary working directory to store mozilla-central and comm-central while they are processed.")
    parser.add_argument("--mozilla-central-zip", default=os.getenv("MOZILLA_CENTRAL_ZIP", 'https://hg.mozilla.org/mozilla-central/archive/tip.zip'))
    parser.add_argument("--comm-central-zip", default=os.getenv("COMM_CENTRAL_ZIP", 'https://hg.mozilla.org/comm-central/archive/tip.zip'))

    parser.add_argument("--existing-source-dir", default=os.getenv("EXISTING_SOURCE_DIR", None), help="If specified as a path to an existing mozilla-central with the comm-central module, the script will use that instead of downloading from tip.")

    args = parser.parse_args()

    main(args.working_dir, args.existing_source_dir, args.mozilla_central_zip, args.comm_central_zip)
