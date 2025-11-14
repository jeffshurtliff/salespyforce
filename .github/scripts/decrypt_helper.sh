#!/bin/sh
#
# Script:               decrypt_helper.sh
# Synopsis:             This script decrypts Helper configuration files that have been PGP encrypted
# Created By:           Jeff Shurtliff
# Last Modified By:     Jeff Shurtliff
# Modified Date:        2025-11-14
# Version:              1.0.1

# Decrypt the file
mkdir "$HOME"/secrets
gpg --quiet --batch --yes --decrypt --passphrase="$HELPER_DECRYPT_PASSPHRASE" \
--output "$HOME"/secrets/helper_dm_conn.yml ./.github/encrypted/helper_dm_conn.yml.gpg
