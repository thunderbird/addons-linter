To update this branch, do the following:

* Navigate to your mozilla-central directory.
* Create a tar file with the toolkit schemas `tar -cf mozilla-central.tar toolkit/components/extensions/schemas/`.
* Copy the commands schema to Thunderbird `cp browser/components/extensions/schemas/commands.json comm/mail/components/extensions/schemas/`.
* Copy the pkcs11 schema to Thunderbird `cp browser/components/extensions/schemas/pkcs11.json comm/mail/components/extensions/schemas/`.
* Copy `comm/mail/components/extensions/schemas/addressBook.json` as `contacts.json` and `mailingLists.json`, remove the namespaces that don't match the filename. The updating script can't handle there being more than one namespace in a file.
* Add the Thunderbird schemas `tar -rf mozilla-central.tar comm/mail/components/extensions/schemas/`.
* Run the update script `./scripts/firefox-schema-import ../mozilla-central/mozilla-central.tar`.

Node had trouble reading the tar file I made, but that seemed to go away when I tried adding the whole `extensions` directory instead of just `extensions/schemas`. Go figure.
