#!/bin/sh
#
# Script:               encrypt_secret.sh
# Synopsis:             This script encrypts a file with symmetric encryption
# Created By:           Jeff Shurtliff
# Last Modified By:     Jeff Shurtliff
# Modified Date:        2023-05-27
# Version:              1.0.0

gpg --symmetric --cipher-algo AES256 "$1"
