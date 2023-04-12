import argparse
import os

import polib

"""
This script is for future use (or maybe not :thinking_face:), currently the gettext functionality doesn't seem to work as implemented...
"""

# Grabbed this some config.js
supported_locales = [
    'af',
    'ar',
    'ast',
    'bg',
    'bn',
    'bs',
    'ca',
    'cak',
    'cs',
    'da',
    'de',
    'dbl',
    'dbr',
    'dsb',
    'el',
    'en-CA',
    'en-GB',
    'en-US',
    'es',
    'eu',
    'fa',
    'fi',
    'fr',
    'fy-NL',
    'ga-IE',
    'he',
    'hsb',
    'hu',
    'id',
    'it',
    'ja',
    'ka',
    'kab',
    'ko',
    'mk',
    'mn',
    'ms',
    'nl',
    'nb-NO',
    'nn-NO',
    'pl',
    'pt-BR',
    'pt-PT',
    'ro',
    'ru',
    'sk',
    'sl',
    'sq',
    'sv-SE',
    'te',
    'th',
    'tr',
    'uk',
    'ur',
    'vi',
    'zh-CN',
    'zh-TW',
]

# Various little messages we can patch for english locale (ATN)
english_patches = {
    'This API has not been implemented by Firefox.': 'This API has not been implemented by Thunderbird or may be an experiment extension.',
    """This API can cause issues when loaded
      temporarily using about:debugging in Firefox unless you specify
      applications|browser_specific_settings > gecko > id in the manifest.
      Please see: https://mzl.la/2hizK4a for more.""": """This API can cause issues when loaded
      temporarily using about:debugging in Thunderbird unless you specify
      browser_specific_settings > gecko > id in the manifest.
      Please see: https://mzl.la/2hizK4a for more."""
}


def patch_locale(locale, locale_dir):
    """
    Patches a locales messages.po with Thunderbird references instead of Firefox
    :param locale:
    :param locale_dir:
    :return:
    """
    po_path = os.path.join(locale_dir, locale, 'LC_MESSAGES', 'messages.po')
    print(f"Patching {po_path}")
    po = polib.pofile(po_path)

    for entry in po:
        # If we have a custom string english string, use that instead
        if 'en-' in locale and entry.msgid in english_patches:
            entry.msgstr = english_patches[entry.msgid]
            continue

        if 'en-US' == locale:
            entry.msgstr = entry.msgid

        # Simply replace Firefox with Thunderbird
        entry.msgstr = entry.msgstr.replace('Firefox', 'Thunderbird')

    po.save(po_path)


def main(locale_arg, locale_dir):
    locales = [locale_arg]

    if locale_arg == 'all':
        locales = supported_locales

    for locale in locales:
        patch_locale(locale, locale_dir)

    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thunderbird Locale Patcher")

    parser.add_argument("--locale-dir", default='../locale', help='The directory containing all of the locale folders')
    parser.add_argument("--locale", default='all', help='Specify a locale, or "all" for every locale')
    args = parser.parse_args()

    main(args.locale, args.locale_dir)
