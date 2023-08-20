#!/usr/bin/env bash

grep 'new entry' FinesseWeaponsExtended_*.txt | awk '{ print $3 }' | tr -d '"'
