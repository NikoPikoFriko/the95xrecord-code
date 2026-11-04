#!/usr/bin/env bash
# Rebuild derived SSOT artifacts and publish. Run from anywhere.
set -euo pipefail
ROOT="C:/Users/NIKO/TEMPLE"
python "$ROOT/tools/ssot/build_texts.py"
python "$ROOT/tools/ssot/build_crossref.py" 2>/dev/null || true
python "$ROOT/tools/ssot/verify_published.py" || echo "WARN: live verification reported fails (see above)"
bash "$ROOT/tools/deploy-live.sh"
