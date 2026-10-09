# pages

이런저런 페이지 모음.

**배포 URL**: <https://pages.benelog.net/>

## 페이지 목록

| 날짜 | 제목 | 종류 | 소스 | 보기 |
|------|------|------|------|------|
| 2026-04-26 | AI agent에게 개인적인 일 시키기 | 발표 자료 (대학 동창 모임) | [`20260426-ai-gent/slides.md`](20260426-ai-gent/slides.md) | [HTML](https://pages.benelog.net/20260426-ai-gent/) · [PDF](https://pages.benelog.net/20260426-ai-gent/slides.pdf) |
| 2007-04-28 | 상혁과 나영의 결혼식 초대장 | 청첩장 | [`20070428-wedding/`](20070428-wedding/) | [HTML](https://pages.benelog.net/20070428-wedding/) |
| 1995-11-14 | 이제 윈도우 시대? | 학교 교지 기고문 | [`19951114-windows-era/`](19951114-windows-era/) | [HTML](https://pages.benelog.net/19951114-windows-era/) |

- `20260426-ai-gent/` 는 [presentations](https://github.com/benelog/presentations) 저장소에서 옮겨 왔다.
  같은 [Slidev](https://sli.dev/) 마크다운이고, 테마 `themes/green/` 도 그 저장소에서 복사했다.
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

## 구조 / 빌드

- 페이지마다 `YYYYMMDD-slug/` 디렉터리 하나. 루트 `index.html` 이 목록 페이지다.
- 디렉터리에 `slides.md` 가 있으면 Slidev 로 HTML(SPA)·PDF 를 빌드하고, 없으면 정적 파일로 그대로 복사한다 (`scripts/build.sh`).

```bash
npm install                              # 최초 1회 (Slidev 를 쓰는 페이지용)
npm run build                            # dist/ 에 전체 빌드
npm run dev -- 20260426-ai-gent/slides.md   # 슬라이드 라이브 미리보기
```

main 에 push 하면 GitHub Actions(`.github/workflows/deploy.yml`)가 빌드해서 GitHub Pages 로 배포한다.
