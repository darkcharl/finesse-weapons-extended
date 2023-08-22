#!/usr/bin/env python

""" Script to modify contents of character file """

import os
import re
import sys


def usage():
    print("prep.py source_file target_file")
    sys.exit(1)


def get_options(args):
    """ Returns options from command line """
    nargs = len(sys.argv)
    if nargs < 2:
        usage()

    source = sys.argv[1]
    if not os.path.exists(source):
        print(f"No such file: {source}")
        sys.exit(2)

    target = f"FinesseWeaponsExtended_{source}"
    if nargs == 3:
        target = sys.argv[2]

    return source, target


def parse(source, weapons=["Club", "Flail", "Glaive", "Greataxe", "Handaxe", "LightHammer", "Longsword", "Javelin", "Pike", "Sickle", "Spear", "Trident", "Quarterstaff"]):
    data = {}
    wpn_group_re = "WPN_({})".format('|'.join(weapons))
    with open(source, "r") as f:
        for block in f.read().split('\n\n'):
            if len(block) == 0:
                continue

            lines = block.split('\n')
            if len(lines) < 3:
                continue

            """ Obtain item key """
            m = re.match(r'new entry "(?P<name>[^"]+)"', lines[0])
            if not m:
                print(f"parsing issue in block")
                continue
            key = m.group('name')

            """ Direct match """
            if re.match(wpn_group_re, key):
                data[key] = lines
                continue

            """ Skip internal """
            if key[0] == "_" or key == "NoWeapon":
                continue

            """ Skip non-weapons """
            if not lines[1] == 'type "Weapon"':
                print(f"{key} not weapon")

            """ Skip unimplemented, if using inheritance  """
            if lines[2].find('using') > -1:
                wpn_re = f"using \"{wpn_group_re}.*\""
                m_type = re.match(wpn_re, lines[2])
                if not m_type:
                    continue

            data[key] = lines

    return data


def add_finesse(props):
    p = set(props.split(';'))
    p.add('Finesse')
    properties = ';'.join(sorted(p))
    return f'data "Weapon Properties" "{properties}"'


def prepare_file(source, target, prop_re=r'data "Weapon Properties" "(?P<props>[^=]+)"'):
    """ Prepares new weapon file """
    data = parse(source)
    with open(target, "w") as f:
        for k, v in data.items():
            print(f"Processing {k}")
            for line in v:
                m = re.match(prop_re, line)
                if m:
                    props = m.group('props')
                    line = add_finesse(props)

                f.write(line + '\n')

            f.write('\n')


if __name__ == "__main__":
    opts = get_options(sys.argv)
    prepare_file(*opts)
