#!/bin/bash
# fund-advisor CLI 脚本
# 直接运行源码，无需 pip install

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TOOLS_DIR="$PROJECT_ROOT/tools"

exec python3 -c "import sys; sys.path.insert(0, '$TOOLS_DIR'); from src.cli import cli; cli()" "$@"