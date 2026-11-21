# 림버스 컴퍼니 편성 도구 — Claude 작업 규칙

자세한 내용은 `docs/HANDOFF.md`를 먼저 읽는다. 아래는 매번 지킬 핵심만 모은 것이다.

## 프로젝트
- 본 프로그램은 단일 파일 `limbus-tool.html` (현재 v0.5). 2026-11-02 GitHub로 옮기면서 버전 번호를 v0.1부터 새로 시작했다(v0.1 = 이전 번호 v3.0). 문서에 나오는 v1.x~v3.0은 이전 번호다.
- 사이트는 claude.ai 아티팩트 공개 링크 `https://claude.ai/artifact/N4Ndtt57YxjetpMU7aSUJD` 하나로 운영한다. 새 링크를 만들지 않는다(데이터 저장소가 링크별로 따로 생김).
- 런타임 기능(capabilities)은 그대로 유지한다:
  `{"db":{"rules":[{"path":"identities","read":"view","write":"admin"},{"path":"egos","read":"view","write":"admin"},{"path":"drafts","read":"admin","write":"admin"},{"path":"history","read":"admin","write":"admin"},{"path":"recs","read":"view","write":"admin"}]},"sample":{},"user":{}}`

## 작업 순서
1. 요구사항을 정리해서 보여주고, 사용자가 명시적으로 승인한 뒤에 코드를 고친다.
2. 고친 뒤 headless 브라우저(playwright)로 테스트한다. 실패하면 올리지 않고 보고한다.
3. 통과하면 같은 공개 링크를 업데이트하고, 커밋을 남긴 뒤 사용자에게 알린다. 버전 커밋은 메시지 첫 줄을 `v0.6: ...`처럼 버전으로 시작한다. 태그(`v0.6`)도 달아서 푸시하되, 클라우드 세션에서 태그 푸시가 막히면(2026-11-02 확인) 커밋 메시지 표기만으로 둔다.
4. 화면·데이터 구조를 바꾸면 `docs/HANDOFF.md`(결정 기록)와 `docs/EGO-변환-안내.md`도 함께 고친다.

## 깃허브 올리는 법 (2026-11-14 요청, 2026-11-21 두 갈래로 바꿈)
- **데이터는 main에 바로**: `gifts/`, `keywords/`, `data/`(인격·E.G.O·추천 덱 `data/db/` 포함) 아래 파일(데이터 json, 아이콘, 생성된 md, 데이터 넣는 도구 `parse_gifts.py`·`add_icon.py`·`make_md.py`)은 새로 넣든 고치든 main에 바로 커밋·푸시한다. PR을 만들지 않는다.
  - json을 고치면 `gifts.md` 같은 생성 파일도 같이 다시 만들어 올린다. 사용자가 깃허브 웹에서 json을 직접 고쳤다고 하면 md만 다시 만든다.
- **사이트·문서는 PR로**: `limbus-tool.html`, `docs/`, `CLAUDE.md`, `README.md`는 다음 버전 브랜치(지금은 `v0.5`)에 커밋하고 그 브랜치의 PR 하나에 모은다.
  - 버전을 올릴 때(테스트 통과 → 공개 링크 업데이트) 그 PR을 main에 합친다. 버전 브랜치는 데이터 작업 뒤 main을 받아 와(merge) 최신 데이터를 사이트에 넣는다.
  - 다음 수정부터는 새 버전 브랜치(`v0.6`)와 새 PR을 만든다. PR 설명에는 들어간 수정 목록을 계속 갱신한다.
- 사이트는 데이터를 파일 안에 넣어 쓰므로, main의 데이터를 고쳐도 공개 사이트에는 다음 버전 때 반영된다.
- **v0.5부터 인격·E.G.O·추천 덱의 원본은 깃허브 `data/db/`**(identities.json, egos.json, recs.json)이다. 사이트는 이 데이터를 파일 안에 넣어 쓴다(`python3 -I tools/embed_db.py`). 저장 공간(db)의 identities/egos/recs는 더 읽지 않는다.
  - 사이트 관리자 탭에서 저장하면 그 기기에만 먼저 적용되고 '깃허브 반영 대기'에 모인다. 사용자가 '변경분 복사' JSON을 채팅에 주면 `python3 -I tools/apply_pending.py 파일`로 `data/db/`에 반영해 main에 올리고, 다음 버전 때 사이트에 넣는다.
  - 캡처로 받은 인격·E.G.O JSON도 같은 형식으로 `data/db/`에 넣을 수 있다.
- 개인 데이터(편성·보유), 변환 초안(drafts), 변경 기록(history)은 계속 저장 공간(db)에 있다.
- 기획서(계획)는 `docs/기획서.md`를 고친다. claude.ai 기획서 문서는 2026-11-14 이후 고치지 않는다.

## 이어서 할 일
- 대화를 시작하면 `gifts/pending/README.md`가 있는지 보고, 있으면 그 내용을 사용자에게 먼저 알린다.

## 캡처 → JSON 변환
- 인격: `docs/HANDOFF.md` 10장. E.G.O: `docs/EGO-변환-안내.md`.
- 출력 전에 JSON 문법(괄호)을 반드시 검사한다.
- 숫자가 정말 애매할 때만 `uncertain`에 넣는다. 줄바꿈처럼 보이는 문장은 한 줄로 합친다. 이탤릭 설명 문구는 뺀다.
- 특정 인격 편성 시에만 적용되는 E.G.O 패시브 효과는 `passive.extra`로 분리한다.

## 사용자와 대화
- 한국어로, 쉬운 말로 짧게.
- 수정 사항은 모아서 한 번에 반영하는 걸 선호한다.
