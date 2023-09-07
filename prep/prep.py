#!/usr/bin/env python

""" Script to alter weapon properties """

import os
import re
import sys

enabled_weapons = [
    "Battleaxe",        # versatile
    "Club",             # light
    # "Dagger",         # finesse
    # "Dart",           # finesse, two handed
    "Flail",            # n/a
    "Glaive",           # heavy, two handed
    "Greataxe",         # heavy, two handed
    "Greatclub",        # two handed
    "Greatsword",       # heavy, two handed
    "Halberd",          # heavy, reach, two handed
    "HandCrossbow",     # light
    "Handaxe",          # light, thrown
    "HeavyCrossbow",    # heavy, two handed
    "Javelin",          # thrown
    "LightCrossbow",    # two handed
    "LightHammer",      # light
    "Longbow",          # heavy, two handed
    "Longsword",        # versatile
    "Mace",             # n/a
    "Maul",             # heavy, two handed
    "Morningstar",      # n/a
    "Pike",             # heavy, reach, two handed
    "Quarterstaff",     # versatile
    # "Rapier",         # finesse
    # "Scimitar",       # finesse
    "Shortbow",         # two handed
    # "Shortsword",     # finesse, light
    "Sickle",           # light
    "Sling",            # n/a
    "Spear",            # versatile
    "Trident",          # thrown, versatile
    "WarPick",          # n/a
    "Warhammer",        # versatile
]


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

    return [source]


def parse(source, weapons=enabled_weapons):
    data = {}
    wpn_group_re = "WPN_({})".format('|'.join(weapons))
    with open(source, "r") as f:
        for block in f.read().split('\n\n'):
            if len(block) == 0:
                continue

            lines = block.split('\n')
            if len(lines) < 3:
                continue

            """ Obtain item weapon_name """
            m = re.match(r'new entry "(?P<name>[^"]+)"', lines[0])
            if not m:
                print(f" [!] parsing issue in block")
                print(block)
                print()
                continue
            weapon_name = m.group('name')

            """ Direct match """
            m = re.match(wpn_group_re, weapon_name)
            if m:
                weapon_type = m.group(1)
                # print(f" [D] weapon found directly: {weapon_name}, {weapon_type}")
                if not data.get(weapon_type, None):
                    data[weapon_type] = {}

                data[weapon_type][weapon_name] = lines
                continue

            """ Skip internal weapons """
            if weapon_name[0] == "_" or weapon_name == "NoWeapon":
                continue

            """ Skip non-weapons """
            if not lines[1] == 'type "Weapon"':
                print(f"{weapon_name} not weapon")

            """ Skip unimplemented, if using inheritance  """
            weapon_type = None
            if lines[2].find('using') > -1:
                wpn_re = f"using \"{wpn_group_re}.*\""
                m_type = re.match(wpn_re, lines[2])
                if not m_type:
                    continue
                weapon_type = m_type.group(1)
                # print(f" [D] weapon found via using: {weapon_name}, {weapon_type}")

            if not data.get(weapon_type, None):
                data[weapon_type] = {}

            data[weapon_type][weapon_name] = lines

    return data


def add_finesse(props):
    p = set(props.split(';'))
    p.add('Finesse')
    properties = ';'.join(sorted(p))
    return f'data "Weapon Properties" "{properties}"'


def prepare_file(source, prefix="FinesseWeaponsExtended", prop_re=r'data "Weapon Properties" "(?P<props>[^=]+)"'):
    """ Prepares new weapon file """
    data = parse(source)
    for weapon_type in data.keys():
        weapon_file = f"{prefix}_{weapon_type}_{source}"
        print(f"Writing: {weapon_type} to {weapon_file}")
        with open(weapon_file, "w") as f:
            for weapon_name, lines in data[weapon_type].items():
                print(f"Processing {weapon_name}")
                for line in lines:
                    m = re.match(prop_re, line)
                    if m:
                        props = m.group('props')
                        line = add_finesse(props)
                    f.write(line + '\n')
                f.write('\n')
        print()


if __name__ == "__main__":
    opts = get_options(sys.argv)
    prepare_file(*opts)
