#!/usr/bin/env bash
# Freeze current environment for Evidence-phase reproducibility.
# Usage: bash freeze_env.sh [output_dir]
# Default output_dir: ./env_snapshots

set -euo pipefail

OUTPUT_DIR="${1:-./env_snapshots}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$OUTPUT_DIR"

MANIFEST="$OUTPUT_DIR/manifest_${TIMESTAMP}.txt"

echo "[freeze_env] Output directory: $OUTPUT_DIR"

if command -v conda &>/dev/null; then
    ENV_NAME=$(conda info --envs | awk '$1 == "*" {print "base"; exit} $2 == "*" {print $1; exit}')
    ENV_NAME="${ENV_NAME:-conda}"
    conda env export > "$OUTPUT_DIR/env_${ENV_NAME}_${TIMESTAMP}.yml"
    echo "[freeze_env] Conda environment exported to $OUTPUT_DIR/env_${ENV_NAME}_${TIMESTAMP}.yml"
fi

if command -v python &>/dev/null; then
    PYTHON_BIN=python
elif command -v python3 &>/dev/null; then
    PYTHON_BIN=python3
else
    echo "[freeze_env] ERROR: python/python3 not found" >&2
    exit 1
fi

"$PYTHON_BIN" -m pip freeze > "$OUTPUT_DIR/requirements_${TIMESTAMP}.txt" 2>/dev/null || \
    pip freeze > "$OUTPUT_DIR/requirements_${TIMESTAMP}.txt" 2>/dev/null || \
    pip3 freeze > "$OUTPUT_DIR/requirements_${TIMESTAMP}.txt"
echo "[freeze_env] pip freeze saved to $OUTPUT_DIR/requirements_${TIMESTAMP}.txt"

{
    echo "=== System Info ==="
    echo "Date: $(date)"
    echo "Working directory: $(pwd)"
    echo "Python executable: $(command -v "$PYTHON_BIN")"
    echo "Python version: $("$PYTHON_BIN" --version 2>/dev/null)"
    echo "PyTorch: $("$PYTHON_BIN" -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'not installed')"
    echo "CUDA: $("$PYTHON_BIN" -c 'import torch; print(torch.version.cuda)' 2>/dev/null || echo 'N/A')"
    echo "CUDA available: $("$PYTHON_BIN" -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo 'N/A')"
    echo "GPU: $(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null || echo 'N/A')"
    echo "Git commit: $(git rev-parse HEAD 2>/dev/null || echo 'N/A')"
    echo "Git branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
    echo "Git dirty files:"
    git status --short 2>/dev/null || echo 'N/A'
} > "$OUTPUT_DIR/system_info_${TIMESTAMP}.txt"

{
    echo "timestamp=$TIMESTAMP"
    echo "requirements=requirements_${TIMESTAMP}.txt"
    ls "$OUTPUT_DIR"/env_*_"$TIMESTAMP".yml >/dev/null 2>&1 && echo "conda_env=$(basename "$OUTPUT_DIR"/env_*_"$TIMESTAMP".yml)" || echo "conda_env=N/A"
    echo "system_info=system_info_${TIMESTAMP}.txt"
} > "$MANIFEST"

echo "[freeze_env] System info saved to $OUTPUT_DIR/system_info_${TIMESTAMP}.txt"
echo "[freeze_env] Manifest saved to $MANIFEST"
echo "[freeze_env] Done."
