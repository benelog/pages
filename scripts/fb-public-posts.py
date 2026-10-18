#!/usr/bin/env python3
"""페이스북 '정보 내보내기'(JSON)의 내 게시물에서 전체 공개 글만 골라 JSONL로 쓴다.

사용법: scripts/fb-public-posts.py <내보내기 폴더> <공개 글 시각 목록> <출력 .jsonl>

- 내보내기 파일에는 공개 범위가 없다. 그래서 프로필의 게시물 필터(작성자: 나, 공개 범위: 전체 공개)로
  피드를 끝까지 내리면서 GraphQL 응답의 creation_time 을 모은 목록을 따로 받는다(한 줄에 유닉스 시각 하나).
  내보내기의 timestamp 와 creation_time 은 대부분 같고, 2017년 이전 글은 몇 초 어긋나기도 해서 60초 안이면 같은 글로 본다.
  목록에는 내 글에 공유된 남의 글 시각도 섞여 있지만, 이런 글은 내 글과 10분 넘게 떨어져 있어 걸리지 않는다.
- 페이스북이 UTF-8 바이트를 latin-1 문자로 넣어 둔 문자열을 되돌린다.
- 업로드 IP, EXIF, 미디어 경로는 버린다. 남의 담벼락에 쓴 글도 뺀다.
- 링크만 있고 본문이 빈 항목 중, 같은 링크를 본문과 함께 올린 항목이 1시간 안에 있으면 중복이라 뺀다.
"""
import bisect
import datetime
import json
import sys
from pathlib import Path

KST = datetime.timezone(datetime.timedelta(hours=9))


def fix(s):
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def to_row(p):
    text = "\n".join(fix(d["post"]) for d in p.get("data", []) if "post" in d)
    links, media, extra = [], 0, []
    for a in p.get("attachments", []):
        for d in a.get("data", []):
            ec = d.get("external_context")
            if ec:
                link = {"url": ec.get("url", "")}
                if ec.get("name"):
                    link["name"] = fix(ec["name"])
                links.append(link)
            m = d.get("media")
            if m:
                media += 1
                desc = fix(m.get("description", ""))
                if desc and desc != text and desc not in extra:
                    extra.append(desc)
            if "text" in d:
                extra.append(fix(d["text"]))
    if not text and extra:
        text = extra.pop(0)
    ts = p["timestamp"]
    row = {
        "timestamp": ts,
        "date": datetime.datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d %H:%M"),
        "title": fix(p.get("title", "")),
        "text": text,
    }
    if extra:
        row["extra_text"] = extra
    if links:
        row["links"] = links
    if media:
        row["media_count"] = media
    return row


def main(export_dir, public_list, out):
    posts = json.loads(Path(export_dir, "your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.json").read_text())
    public = sorted(int(x) for x in Path(public_list).read_text().split())

    def is_public(ts):
        i = bisect.bisect_left(public, ts - 60)
        return i < len(public) and public[i] <= ts + 60

    rows = [to_row(p) for p in posts if is_public(p["timestamp"])]
    rows = [r for r in rows if "'s profile" not in r["title"] and "'s timeline" not in r["title"]]

    texted = {}
    for r in rows:
        if r["text"]:
            for link in r.get("links", []):
                texted.setdefault(link["url"], []).append(r["timestamp"])

    def is_dup(r):
        return not r["text"] and any(
            abs(t - r["timestamp"]) <= 3600 for link in r.get("links", []) for t in texted.get(link["url"], []))

    rows = sorted((r for r in rows if not is_dup(r)), key=lambda r: r["timestamp"])
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} posts -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
