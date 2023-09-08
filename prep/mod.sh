#!/usr/bin/env bash

DIVINE_EXE="/e/Modding/BG3/ExportTool-v1.18.5/Tools/divine.exe"
UUIDGEN_EXE="/e/Modding/uuidgen.exe"
ZIP_EXE="/c/Program Files/7-Zip/7z.exe"

SOURCES=(
  "Weapon_Shared.txt"
  "Weapon_SharedDev.txt"
  "Weapon_Gustav.txt"
  "Weapon_GustavDev.txt"
  "Weapon_BasketOfEquipment.txt"
)

WEAPONS=(
  "Battleaxe"
  "Club"
  "Flail"
  "Glaive"
  "Greataxe"
  "Greatclub"
  "Greatsword"
  "Halberd"
  "HandCrossbow"
  "Handaxe"
  "HeavyCrossbow"
  "Javelin"
  "LightCrossbow"
  "LightHammer"
  "Longbow"
  "Longsword"
  "Mace"
  "Maul"
  "Morningstar"
  "Pike"
  "Quarterstaff"
  "Shortbow"
  "Sickle"
  "Sling"
  "Spear"
  "Trident"
  "WarPick"
  "Warhammer"
)

function ensuredir() {
  dirname=$1
  [ ! -d ${dirname} ] && mkdir -p "${dirname}"
}

function ensuremeta() {
  [ -f "$1" ] && return 0

  metafile="$1"
  cp ../PAK/Mods/FinesseWeaponsExtended/meta.lsx "${metafile}"
  
  uuid=$("${UUIDGEN_EXE}")
  sed -i "s#\(FinesseWeaponsExtended\)#\1${WEAPON}#" "${metafile}"
  sed -i "s#\(Finesse Weapons Extended\)#\1 (${WEAPON})#" "${metafile}"
  sed -i "s#\(id=\"UUID\" type=\"FixedString\" value=\)\(\"[^\"]*\"\)#\1\"${uuid}\"#" "${metafile}"
}

function updateinfo() {
  infofile="$1"
  metafile="$2"
  weaponname="$3"
  cp "../release/info.json" "${infofile}"

  # Get UUID from mod and update it
  uuid=$(sed -n 's#.*id="UUID" type="FixedString" value="\([^"]*\)".*#\1#p' ${metafile})
  if [ -z "$uuid" ]; then
    echo " [!] fatal: UUID for mod not found in metafile ${metafile}"
    exit 2
  fi
  sed -i 's#\(.*"UUID": \)"\([^"]*\)"\(.*\)#\1"\2"\3#' "${infofile}"

  # Update mod name and description
  sed -i "s#\(FinesseWeaponsExtended\)#\1${weaponname}#" "${infofile}"
  sed -i "s#\(Finesse Weapons Extended\)#\1 (${weaponname})#" "${infofile}"
}

rm -f FinesseWeaponsExtended*.txt
for SOURCE in "${SOURCES[@]}"; do
  ./prep.py $SOURCE
done

for WEAPON in "${WEAPONS[@]}"; do
  # Create mod PAK structure, if necessary
  MOD_NAME="FinesseWeaponsExtended${WEAPON}"
  WEAPON_PAK_DIR="../PAK-${WEAPON}"
  WEAPON_MODS_DIR="${WEAPON_PAK_DIR}/Mods/${MOD_NAME}"
  WEAPON_DATA_DIR="${WEAPON_PAK_DIR}/Public/${MOD_NAME}/Stats/Generated/Data"
  ensuredir "${WEAPON_PAK_DIR}"
  ensuredir "${WEAPON_MODS_DIR}"
  ensuredir "${WEAPON_DATA_DIR}"

  # Create new meta if not created
  ensuremeta "${WEAPON_MODS_DIR}/meta.lsx"
  
  # Copy data to PAK 
  echo "Moving data for ${WEAPON}"
  mv FinesseWeaponsExtended_"${WEAPON}"*.txt "${WEAPON_DATA_DIR}"
  
  # Create mod release folder, if necessary
  WEAPON_RELEASE_DIR="../release-${WEAPON}"
  ensuredir "${WEAPON_RELEASE_DIR}"

  # Update info with global version all the time
  updateinfo "${WEAPON_RELEASE_DIR}/info.json" "${WEAPON_MODS_DIR}/meta.lsx" "${WEAPON}"

  [ -n "${SKIP_PACKAGING}" ] && continue
  
  # Create PAK
  echo "Creating PAK for ${WEAPON}"
  WEAPON_PAK_DIR_FULL=$(readlink -f "${WEAPON_PAK_DIR}")
  WEAPON_RELEASE_DIR_FULL=$(readlink -f "${WEAPON_RELEASE_DIR}")
  WEAPON_PAK="${WEAPON_RELEASE_DIR_FULL}/${MOD_NAME}.pak"
  WEAPON_ZIP="${WEAPON_RELEASE_DIR_FULL}/${MOD_NAME}.zip"
  "${DIVINE_EXE}" -g "bg3" --action "create-package" --source "${WEAPON_PAK_DIR_FULL}" --destination "${WEAPON_PAK}" -l "all"

  # Create ZIP
  echo "Creating ZIP for ${WEAPON}"
  "${ZIP_EXE}" a "${WEAPON_ZIP}" "${WEAPON_RELEASE_DIR}"/*.{json,pak}

done


