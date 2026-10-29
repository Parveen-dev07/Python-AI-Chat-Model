#!/usr/bin/env bash
# Copy built widget into Accessibility Platform admin (adjust ADMIN_PUBLIC if needed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADMIN_PUBLIC="${ADMIN_PUBLIC:-$ROOT/../accessibility-app/apps/admin/public}"
WIDGET_DIST="$ROOT/apps/widget/dist"

if [[ ! -f "$WIDGET_DIST/ai-chat-widget.js" ]]; then
  echo "Run: cd apps/widget && npm run build"
  exit 1
fi

mkdir -p "$ADMIN_PUBLIC"
cp "$WIDGET_DIST/ai-chat-widget.js" "$ADMIN_PUBLIC/"
cp "$WIDGET_DIST/style.css" "$ADMIN_PUBLIC/ai-chat-widget.css"
echo "Copied widget to $ADMIN_PUBLIC"
