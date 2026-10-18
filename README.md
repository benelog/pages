# pages

이런저런 페이지 모음.

**배포 URL**: <https://pages.benelog.net/>

## 페이지 목록

| 날짜 | 제목 | 종류 | 소스 | 보기 |
|------|------|------|------|------|
| 2026-10-18 | 미투데이와 페이스북으로 본 정상혁 | 분석 (Claude Code가 미투데이 글 1,210개와 페이스북 공개 글 1,730개를 읽고 씀) | [`20261018-social-media-analysis/`](20261018-social-media-analysis/) | [HTML](https://pages.benelog.net/20261018-social-media-analysis/) |
| 2026-04-26 | AI agent에게 개인적인 일 시키기 | 발표 자료 (대학 동창 모임) | [`20260426-ai-gent/slides.md`](20260426-ai-gent/slides.md) | [HTML](https://pages.benelog.net/20260426-ai-gent/) · [PDF](https://pages.benelog.net/20260426-ai-gent/slides.pdf) |
| 2014-07-05 | 파워포인트 떠나기 | 발표 자료 (개인 연구 자료) | [`20140705-goodbye-powerpoint/slides.md`](20140705-goodbye-powerpoint/slides.md) | [HTML](https://pages.benelog.net/20140705-goodbye-powerpoint/) · [PDF](https://pages.benelog.net/20140705-goodbye-powerpoint/slides.pdf) |
| 2007-04-28 | 상혁과 나영의 결혼식 초대장 | 청첩장 | [`20070428-wedding/`](20070428-wedding/) | [HTML](https://pages.benelog.net/20070428-wedding/) |
| 1995-11-14 | 이제 윈도우 시대? | 학교 교지 기고문 | [`19951114-windows-era/`](19951114-windows-era/) | [HTML](https://pages.benelog.net/19951114-windows-era/) |

- `20260426-ai-gent/`, `20140705-goodbye-powerpoint/` 는 [presentations](https://github.com/benelog/presentations) 저장소에서 옮겨 왔다.
  같은 [Slidev](https://sli.dev/) 마크다운이고, 테마 `themes/green/` 도 그 저장소에서 복사했다.
  `originals/20140705-goodbye-powerpoint/` 는 Slidev 로 옮기기 전의 reveal.js 원본과 그 발표가 설명하는
  빌드 스크립트(`build.gradle`, `start-py.sh` 등)다. 숫자로 시작하지 않아 빌드 대상에서 빠진다.
- `20070428-wedding/` 은 Dropbox `public-archive/wedding` 에서 옮겨 왔다.
- `19951114-windows-era/` 는 old-com 저장소(옛 PC 의 C: 드라이브)에 남은 아래아한글 3.0 문서 `HWP21/WIN.HWP` 를
  `scripts/win-hwp2html.py` 로 옮긴 것이다. 문서에 저장된 용지·여백·줄 나눔·쪽 나눔·그림 위치를 그대로 써서
  원본과 같은 자리에서 줄과 쪽이 바뀐다. 글은 오타까지 고치지 않았다.
  문서에 들어 있던 그림 3장(BMP)은 `win-0.png`~`win-2.png` 로 뽑았고, 연결만 되어 있던
  `C:\I\DOWN\DUMP0000.PCX` 는 남아 있지 않아 점선 상자로 자리만 표시했다.

  ```bash
  scripts/win-hwp2html.py            # ../old-com 을 읽어 19951114-windows-era/ 를 다시 만든다
  scripts/win-hwp2html.py <old-com 경로>
  ```
- `20261018-social-media-analysis/` 는 2026-10-15 에 올린 '페이스북 글로 본 정상혁'(`20261015-facebook-analysis/`)을
  미투데이 분석과 합치고 2020~2026년 연도별 페이지를 더한 것이다.
  페이스북 글은 '내 정보 내보내기'(게시물, 전체 기간, JSON)로 받았다. 내보내기에는 공개 범위가 없어서
  프로필 게시물 필터(작성자: 나)로 피드를 읽으며 얻은 글마다의 공개 범위·작성 시각과 대조해,
  전체 공개 글과 'SW업계사람' 친구 목록에 공개한 글을 골랐다('SW업계사람' 글 중 내보내기에 없는 21개는 피드에서 본문을 읽음).
  그 결과를 `originals/20261018-social-media-analysis/facebook-public-posts.jsonl` 에 두었다(글마다 `audience` 필드).

  ```bash
  scripts/fb-public-posts.py <내보내기 폴더> <전체 공개 글 시각 목록> <출력 .jsonl> [<SW업계사람 글 시각 목록> [<피드에서만 읽은 글 .jsonl>]]
  ```

## 구조 / 빌드

- 페이지마다 `YYYYMMDD-slug/` 디렉터리 하나. 루트 `index.html` 이 목록 페이지다.
- 디렉터리에 `slides.md` 가 있으면 Slidev 로 HTML(SPA)·PDF 를 빌드하고, 없으면 정적 파일로 그대로 복사한다 (`scripts/build.sh`).

```bash
npm install                              # 최초 1회 (Slidev 를 쓰는 페이지용)
npm run build                            # dist/ 에 전체 빌드
npm run dev -- 20260426-ai-gent/slides.md   # 슬라이드 라이브 미리보기
```

main 에 push 하면 GitHub Actions(`.github/workflows/deploy.yml`)가 빌드해서 GitHub Pages 로 배포한다.
