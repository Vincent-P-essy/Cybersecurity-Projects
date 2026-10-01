#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
java -m jdk.compiler/com.sun.tools.javac.Main -Xlint:all -Werror -d build src/*.java tests/*.java
if [[ "${1:-test}" == "demo" ]]; then
  java -cp build ledger.Demo
else
  java -cp build ledger.LedgerTest
fi
