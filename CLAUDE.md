# 림버스 컴퍼니 편성 도구 — Claude 작업 규칙

자세한 내용은 `docs/HANDOFF.md`를 먼저 읽는다. 아래는 매번 지킬 핵심만 모은 것이다.

## 프로젝트
- 본 프로그램은 단일 파일 `limbus-tool.html` (현재 v0.4). 2026-11-02 GitHub로 옮기면서 버전 번호를 v0.1부터 새로 시작했다(v0.1 = 이전 번호 v3.0). 문서에 나오는 v1.x~v3.0은 이전 번호다.
- 사이트는 claude.ai 아티팩트 공개 링크 `https://claude.ai/artifact/N4Ndtt57YxjetpMU7aSUJD` 하나로 운영한다. 새 링크를 만들지 않는다(데이터 저장소가 링크별로 따로 생김).
- 런타임 기능(capabilities)은 그대로 유지한다:
  `{"db":{"rules":[{"path":"identities","read":"view","write":"admin"},{"path":"egos","read":"view","write":"admin"},{"path":"drafts","read":"admin","write":"admin"},{"path":"history","read":"admin","write":"admin"},{"path":"recs","read":"view","write":"admin"}]},"sample":{},"user":{}}`

## 작업 순서
1. 요구사항을 정리해서 보여주고, 사용자가 명시적으로 승인한 뒤에 코드를 고친다.
2. 고친 뒤 headless 브라우저(playwright)로 테스트한다. 실패하면 올리지 않고 보고한다.
3. 통과하면 같은 공개 링크를 업데이트하고, 커밋을 남긴 뒤 사용자에게 알린다. 버전 커밋은 메시지 첫 줄을 `v0.5: ...`처럼 버전으로 시작한다. 태그(`v0.5`)도 달아서 푸시하되, 클라우드 세션에서 태그 푸시가 막히면(2026-11-02 확인) 커밋 메시지 표기만으로 둔다.
4. 화면·데이터 구조를 바꾸면 `docs/HANDOFF.md`(결정 기록)와 `docs/EGO-변환-안내.md`도 함께 고친다.

## 캡처 → JSON 변환
- 인격: `docs/HANDOFF.md` 10장. E.G.O: `docs/EGO-변환-안내.md`.
- 출력 전에 JSON 문법(괄호)을 반드시 검사한다.
- 숫자가 정말 애매할 때만 `uncertain`에 넣는다. 줄바꿈처럼 보이는 문장은 한 줄로 합친다. 이탤릭 설명 문구는 뺀다.
- 특정 인격 편성 시에만 적용되는 E.G.O 패시브 효과는 `passive.extra`로 분리한다.

## 사용자와 대화
- 한국어로, 쉬운 말로 짧게.
- 수정 사항은 모아서 한 번에 반영하는 걸 선호한다.
