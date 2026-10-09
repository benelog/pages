#!/usr/bin/env bash
# 모든 페이지를 dist/ 로 모은다.
#  - YYYYMMDD-slug/ 에 slides.md 가 있으면 Slidev 로 HTML(SPA)·PDF 를 빌드
#  - 그 밖의 YYYYMMDD-slug/ 는 정적 파일이라 그대로 복사
#  - 루트의 index.html 은 목록 페이지
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
SLIDEV="$ROOT/node_modules/.bin/slidev"

rm -rf "$DIST"
mkdir -p "$DIST"
cp "$ROOT/index.html" "$DIST/"

shopt -s nullglob
for dir in "$ROOT"/[0-9]*/; do
  dir="${dir%/}"
  name="$(basename "$dir")"
  out="$DIST/$name"

  if [ -f "$dir/slides.md" ]; then
    if [ ! -x "$SLIDEV" ]; then
      echo "slidev not found. Run 'npm install' first." >&2
      exit 1
    fi
    echo "→ slides $name"
    "$SLIDEV" build "$dir/slides.md" --base "/$name/" --out "$out"
    "$SLIDEV" export "$dir/slides.md" --output "$out/slides.pdf"
    # 런타임에 참조되는 이미지 등 (frontmatter 이미지는 번들되지 않음)
    for asset in "$dir"/*; do
      case "$asset" in
        *.md|*.drawio) continue ;;
      esac
      if [ -f "$asset" ]; then cp "$asset" "$out/"; fi
    done
  else
    echo "→ static $name"
    cp -r "$dir" "$out"
  fi
done

echo "✓ $DIST"
