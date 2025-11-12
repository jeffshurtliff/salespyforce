#!/bin/sh
#
# Script:               decrypt_helper_local.sh
# Synopsis:             This script decrypts the Helper configuration file locally (not in GitHub Actions)
# Created By:           Jeff Shurtliff
# Last Modified By:     Jeff Shurtliff
# Modified Date:        2025-11-12
# Version:              1.0.0

# Decrypt the file
mkdir ./local
gpg --quiet --batch --yes --decrypt --passphrase="$HELPER_DECRYPT_PASSPHRASE" \
--output ./local/helper_shurt.yml ./.github/encrypted/helper_shurt.yml.gpg
