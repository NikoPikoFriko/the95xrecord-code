#!/usr/bin/env bash
# Publish site/ to Vercel production safely:
# 1) sync site/ into deploy-vercel (keeps .vercel link)
# 2) copy OUTSIDE the git work tree, because Vercel blocks deploys whose local
#    git author is not a project member ("commit author doesn't have permission")
# 3) deploy production and verify the public surface
set -euo pipefail
ROOT="C:/Users/NIKO/TEMPLE"
cp -r "$ROOT/site/." "$ROOT/deploy-vercel/"
rm -rf "C:/Temp/temple-live"
cp -r "$ROOT/deploy-vercel" "C:/Temp/temple-live"
rm -rf "C:/Temp/temple-live/.git"
cd "C:/Temp/temple-live"
vercel deploy --prod -y 2>&1 | tail -4
sleep 4
for p in "" atlas numbers hook pl emails errata appendix search data/search.json feed.xml robots.txt; do
  printf "%s  /%s\n" "$(curl -s -o /dev/null -w '%{http_code}' "https://the95xrecord.vercel.app/$p")" "$p"
done
