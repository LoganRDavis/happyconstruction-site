#!/usr/bin/env bash
set -euo pipefail

# Ensure host directories exist before Docker tries to bind-mount them
mkdir -p "${HOME}/.claude"
