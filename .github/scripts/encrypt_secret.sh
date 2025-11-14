#!/usr/bin/env bash
#
# Script:               encrypt_secret.sh
# Synopsis:             Encrypts a given file in local/ and exports to .github/encrypted/
# Created By:           Jeff Shurtliff
# Last Modified By:     Jeff Shurtliff
# Modified Date:        2025-11-14
# Version:              2.0.0

# Ensure the script fails if a non-zero exit code is returned and to fail more gracefully
set -euo pipefail

# This function displays usage information about the script
usage() {
    echo "Usage: $0 <filename>"
    echo "Example: $0 helper_dm.yml"
    exit 1
}

# Display the usage information if no parameters are passed when running the script
if [ "$#" -ne 1 ]; then
    usage
fi

# Exit the script with an error if the passphrase is not defined in the expected environment variable
if [ -z "${HELPER_DECRYPT_PASSPHRASE:-}" ]; then
    echo "Error: HELPER_DECRYPT_PASSPHRASE environment variable is not set."
    echo "Set it before running this script, for example:"
    echo "  export HELPER_DECRYPT_PASSPHRASE='your-passphrase'"
    exit 1
fi

# Resolve the directory of this script
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Repo root is two levels up from .github/scripts
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

LOCAL_DIR="${REPO_ROOT}/local"
ENCRYPTED_DIR="${REPO_ROOT}/.github/encrypted"

INPUT_NAME="$1"
INPUT_PATH="${LOCAL_DIR}/${INPUT_NAME}"
OUTPUT_PATH="${ENCRYPTED_DIR}/${INPUT_NAME}.gpg"

# Exit the script with an error if the file is not found in the local/ directory
if [ ! -f "$INPUT_PATH" ]; then
    echo "Error: Input file not found: $INPUT_PATH"
    exit 1
fi

# Ensure the .github/encrypted/ directory exists
mkdir -p "$ENCRYPTED_DIR"

# Encrypt using GPG with AES256 and the provided passphrase
gpg \
  --batch \
  --yes \
  --pinentry-mode loopback \
  --passphrase "$HELPER_DECRYPT_PASSPHRASE" \
  --symmetric \
  --cipher-algo AES256 \
  --output "$OUTPUT_PATH" \
  "$INPUT_PATH"

# Display the results of the script execution
echo "Encrypted:"
echo "  $INPUT_PATH"
echo "to:"
echo "  $OUTPUT_PATH"
