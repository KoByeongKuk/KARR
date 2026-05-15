# 나만의 AI 1인 기업 워크스페이스 커스터마이징 플랜

현재 클론받은 저장소는 VS Code 안에서 로컬 AI를 연동해 에이전트 팀과 제2의 두뇌를 구축할 수 있게 해주는 **"Connect AI" 익스텐션**입니다. 사장님(유저님)만의 **'1인 기업 맞춤형 워크스페이스'**로 완벽하게 탈바꿈하기 위해 다음과 같은 커스터마이징을 제안합니다.

## User Review Required

> [!IMPORTANT]
> 본격적인 수정에 앞서, 아래 내용에 대한 **사장님의 의견(이름 및 브랜드 설정)**이 필요합니다. 답변해주시면 그에 맞춰 코드와 텍스트를 일괄 수정하겠습니다.

1. **익스텐션(기업) 이름**: 기존 "Connect AI" 대신 사용할 나만의 기업 이름을 알려주세요. (예: `KoByeongKuk AI Lab`, `My AI Studio`, `프리미엄 1인 기업` 등)
2. **퍼블리셔(배포자) 이름**: 기존 `connectailab` 대신 사용할 아이디 (예: `kobyeongkuk`)
3. **설명문(Description)**: 익스텐션 설명에 특별히 추가하고 싶은 사장님만의 비전이나 슬로건이 있다면 알려주세요. (없다면 기본 제공되는 1인 기업용 설명을 사장님 이름에 맞춰 수정하겠습니다.)
4. **아이콘 변경 여부**: 원하신다면, 기존 `Connect AI` 로고 대신 새로운 테마에 맞는 아이콘 이미지를 AI로 생성해 교체할 수 있습니다. 필요하신가요?

---

## Proposed Changes

위 질문들에 대한 확정이 이루어지면, 다음 파일들을 일괄 수정할 계획입니다.

### Extension Config & Documentation

#### [MODIFY] [package.json](file:///c:/Users/user/.antigravity/MyConnectAi/package.json)
- `name`, `displayName`, `publisher`를 사장님만의 브랜드로 교체
- `description` 및 `keywords` 맞춤형 수정
- 등록된 모든 Command(명령어) 타이틀의 "Connect AI" 접두사를 새 이름으로 변경 (예: `Connect AI: New Chat` ➔ `[새 이름]: New Chat`)
- 환경 설정(Configuration) 항목의 타이틀 및 설명문 수정

#### [MODIFY] [README.md](file:///c:/Users/user/.antigravity/MyConnectAi/README.md)
- 최상단 로고, 제목, 슬로건을 사장님의 1인 기업 비전에 맞게 전면 재작성
- "Built for Agent University & Connect AI" 등의 문구를 제거하고 사장님만의 크레딧으로 대체

---

### Core Source Code

#### [MODIFY] [src/extension.ts](file:///c:/Users/user/.antigravity/MyConnectAi/src/extension.ts)
- 시스템 내부에서 로깅되거나 상태 표시줄(StatusBar)에 나타나는 "Connect AI" 텍스트 교체
- 텔레그램 봇 안내 메시지(`TELEGRAM_HELP`) 등 하드코딩된 인사말 및 안내 문구 수정
- 알림 창(`vscode.window.showInformationMessage`)에 표시되는 브랜드명 업데이트
- 웹뷰(Webview) 생성 시 사용되는 탭 타이틀 및 HTML 내부 텍스트 수정

---

## Verification Plan

### Automated Tests
- `npm run compile` 명령어를 통해 타입스크립트 컴파일이 에러 없이 통과하는지 확인

### Manual Verification
- 컴파일 후, 새로운 확장 프로그램 이름과 명령어가 VS Code 내에 제대로 표출되는지 검증
- 설정 화면(Settings) 및 웹뷰 UI에 변경된 브랜드가 올바르게 적용되었는지 확인

---

**어떤 이름과 브랜드로 시작할까요? 편하게 말씀해 주시면 바로 작업을 시작하겠습니다!**
