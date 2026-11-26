#!/bin/sh
# Builds the scenario object scripts/opencollar from a checkout of OpenCollar and the test driver.
# Usage: tools/assemble.sh <path to the OpenCollar checkout>
set -e
cd "$(dirname "$0")/.."
oc="${1:?path to the OpenCollar checkout}"
rm -rf scripts/opencollar
mkdir -p scripts/opencollar/Root scripts/opencollar/Driver
for name in oc_api oc_auth oc_core oc_dialog oc_settings oc_states oc_rlvsys oc_rlvsuite oc_rlvextension; do
  cp "$oc/src/collar/$name.lsl" scripts/opencollar/Root/
done
cp driver/driver.lsl scripts/opencollar/Driver/
