#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update version numbers in the hb_revive_installer.ghx file.

This script parses the Grasshopper .ghx (XML) file and updates:
  1. The version panels for honeybee-REVIVE and PH-ADORB.
  2. The Scribble label that displays the release date and version.

The installer has two unnamed Panel components whose UserText values
contain the version numbers. We identify them by their InstanceGuid.

Usage:
    python scripts/update_installer_ghx.py \
        --honeybee-revive=0.1.3 \
        --ph-adorb=0.0.10 \
        --release-version=0.1.3
"""

import argparse
from datetime import datetime, timezone
import re
import sys
from pathlib import Path

# The installer file path relative to the repo root
INSTALLER_PATH = Path(__file__).resolve().parent.parent / "hb_revive_installer.ghx"

# InstanceGuid -> package mapping (from the GHX file)
# These GUIDs identify the Panel components that hold version numbers.
PANEL_GUIDS = {
    # Panel connected to _hb_revive_version input
    "2ecb6469-6ee6-4a56-bb59-df6e1435872c": "honeybee_revive",
    # Panel connected to _ph_adorb_version input
    "cb0dab97-7851-4cb0-969f-2802b7727eee": "ph_adorb",
}


def update_panel_version(content, guid, new_version):
    # type: (str, str, str) -> str
    """Find a Panel by InstanceGuid and update its UserText value."""
    pattern = re.compile(
        r'(<item\s+name="InstanceGuid"[^>]*>{}</item>'
        r'.*?'
        r'<item\s+name="UserText"\s+type_name="gh_string"\s+type_code="10">)'
        r'([^<]*)'
        r'(</item>)'.format(re.escape(guid)),
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        print("WARNING: Could not find panel with GUID {}".format(guid))
        return content

    old_version = match.group(2)
    if old_version == new_version:
        return content

    print("  Panel {}: '{}' -> '{}'".format(guid[:8], old_version, new_version))
    return content[: match.start(2)] + new_version + content[match.end(2) :]


def main():
    parser = argparse.ArgumentParser(description="Update REVIVE installer .ghx version pins")
    parser.add_argument("--honeybee-revive", dest="honeybee_revive", help="honeybee-REVIVE version")
    parser.add_argument("--ph-adorb", dest="ph_adorb", help="PH-ADORB version")
    parser.add_argument("--release-version", dest="release_version", help="Release version for the Scribble label")
    parser.add_argument("--installer-path", dest="installer_path", help="Path to .ghx file (default: auto)")
    args = parser.parse_args()

    installer_path = Path(args.installer_path) if args.installer_path else INSTALLER_PATH
    if not installer_path.exists():
        print("ERROR: Installer file not found: {}".format(installer_path))
        sys.exit(1)

    # Collect updates
    updates = {}
    if args.honeybee_revive:
        updates["honeybee_revive"] = args.honeybee_revive
    if args.ph_adorb:
        updates["ph_adorb"] = args.ph_adorb

    if not updates and not args.release_version:
        print("No version updates specified. Nothing to do.")
        return

    print("Updating installer: {}".format(installer_path.name))

    # Read the GHX file
    content = installer_path.read_text(encoding="utf-8-sig")

    # ---------------------------------------------------------------
    # Update version panels
    # ---------------------------------------------------------------
    for guid, flag_name in PANEL_GUIDS.items():
        if flag_name in updates:
            content = update_panel_version(content, guid, updates[flag_name])

    # ---------------------------------------------------------------
    # Update the Scribble label with the release date and version
    # ---------------------------------------------------------------
    if args.release_version:
        today = datetime.now(timezone.utc).strftime("%b %d, %Y").upper()
        new_label = "{} [v{}]".format(today, args.release_version)

        # Match the first Scribble's Text element (the date/version label)
        scribble_pattern = re.compile(
            r'(<item\s+name="NickName"[^>]*>Scribble</item>'
            r'.*?'
            r'<item\s+name="Text"\s+type_name="gh_string"\s+type_code="10">)'
            r'([^<]*)'
            r'(</item>)',
            re.DOTALL,
        )
        scribble_match = scribble_pattern.search(content)
        if scribble_match:
            old_label = scribble_match.group(2)
            print("  Scribble label: '{}' -> '{}'".format(old_label, new_label))
            content = (
                content[: scribble_match.start(2)]
                + new_label
                + content[scribble_match.end(2) :]
            )
        else:
            print("WARNING: Could not find Scribble label in installer file.")

    installer_path.write_text(content, encoding="utf-8-sig")
    print("\nInstaller updated successfully.")


if __name__ == "__main__":
    main()
