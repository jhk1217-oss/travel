# 여행 루트 라이브러리 (Cloudflare Workers)

유튜브 가이드 영상 기반 도보 루트 가이드 모음 사이트.
구조: 첫 화면(국가 선택) → 국가별 루트 목록 → 루트 가이드(HTML).

---

## 1. GitHub에 올리기 (최초 1회)
```bash
git init
git add .
git commit -m "init: travel routes"
git branch -M main
git remote add origin https://github.com/jhk1217-oss/travel.git
git push -u origin main
```

## 2. 자동 배포 연결 — 두 방법 중 하나

### 방법 A (추천 · 무설정): Cloudflare Git 연동 (Workers Builds)
1. Cloudflare 대시보드 → **Workers & Pages → Create(생성) → Workers → Import a repository(저장소 가져오기)**
2. GitHub 계정 연결 후 `travel` 저장소 선택
3. 설정 확인: Build command는 비워두고, Deploy command `npx wrangler deploy` → 저장

끝. 이후 **main에 push할 때마다 자동 배포**된다. (다른 브랜치 push는 프리뷰 빌드 생성)
토큰·시크릿 등록이 전혀 필요 없다.

### 방법 B: GitHub Actions (동봉된 `.github/workflows/deploy.yml` 사용)
1. Cloudflare API 토큰 생성: dash.cloudflare.com/profile/api-tokens → **Create Token → "Edit Cloudflare Workers" 템플릿**
2. Account ID 확인: 대시보드 Workers & Pages 화면 우측
3. GitHub 저장소 → Settings → Secrets and variables → Actions → 시크릿 2개 등록:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
4. main에 push → Actions 탭에서 배포 확인

> 방법 A를 쓰면 B의 워크플로 파일은 있어도 무해하다(시크릿이 없으면 실패로 표시만 됨).
> A만 쓸 경우 `.github/workflows/deploy.yml`을 지워도 된다.

배포 주소: `https://travel.<계정서브도메인>.workers.dev`
커스텀 도메인: 대시보드 → Workers → travel → Settings → Domains.

## 3. 수동 배포 / 로컬 미리보기
```bash
wrangler deploy   # 수동 배포
wrangler dev      # http://localhost:8787
```

## 4. 새 루트 추가 (2단계 → push하면 자동 배포)
1. 루트 HTML을 `public/routes/`에 추가. 파일명: `{국가코드}-{도시}-{슬러그}.html`
   (제작은 동봉된 「루트가이드_표준_제작명령서.md」를 에이전트에게 영상 전사본과 함께 주면 된다)
2. `public/data/routes.json`에 엔트리 1개 추가 → `git add . && git commit && git push`

새 국가는 routes.json의 `countries` 배열에 `{code, name, flag, routes:[]}` 객체를 추가하면
첫 화면에 자동으로 카드가 생긴다.
