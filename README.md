# 아라인사이트 홈페이지

교육·컨설팅 회사 아라인사이트의 정적 홈페이지입니다. 빌드 과정 없이 `index.html` 하나로 동작합니다.

## 구조
- `index.html` — 페이지 전체(디자인 토큰 CSS 변수, 마크업, 스크립트)
- `fonts/gmarket/` — Gmarket Sans Bold (제목용)
- `fonts/pretendard/` — Pretendard Variable 동적 서브셋 (본문용, SIL OFL 1.1)

## 문의 폼 연결
`<form id="inquiry" data-endpoint="">`의 `data-endpoint`에 Formspree 등 폼 수신 주소를 넣으면 실제 전송됩니다.

## 배포
Vercel에서 이 저장소를 가져오면 별도 설정 없이 정적 사이트로 배포됩니다.
