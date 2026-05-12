# 🔑 계정 / 채널 (공유 설정)

여기 한 번만 채워두면 다른 모든 YouTube 도구(트렌드 스나이퍼·내 영상 체크·댓글 수집기·경쟁 채널 분석·텔레그램 보고)가 이 값을 그대로 가져다 씁니다. 매번 도구마다 같은 키를 넣지 않아도 돼요.

## 채워야 하는 항목

| 키 | 설명 | 채우는 법 |
|---|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 키 | [console.cloud.google.com](https://console.cloud.google.com/) → 프로젝트 → "YouTube Data API v3" 사용 설정 → 사용자 인증 정보 → API 키. 무료 한도 충분(하루 10,000 단위). |
| `MY_CHANNEL_HANDLE` | 본인 채널 @핸들 | 예: `@mychannel`. 핸들 또는 ID 둘 중 하나만 채우면 됨. |
| `MY_CHANNEL_ID` | 본인 채널 ID (UCxxxx) | 핸들로 못 잡힐 때 백업용. studio.youtube.com → 설정 → 채널에서 확인. |
| `WATCHED_CHANNELS` | 댓글 수집 대상 채널 핸들 목록 | 예: `["@channel_a", "@channel_b"]`. 댓글 수집기가 이 채널들 최근 영상의 댓글을 메모리로 가져옵니다. |
| `COMPETITOR_CHANNELS` | 경쟁 채널 분석 대상 | 같은 형식. 경쟁 채널 분석 도구가 패턴을 뽑아 다음 액션을 추천합니다. |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 | @BotFather에서 /newbot으로 봇 만들고 받은 `123:ABC...` 형식 토큰. 비워두면 보고 알림 OFF. |
| `TELEGRAM_CHAT_ID` | 본인 chat_id | 봇한테 아무 메시지 보낸 뒤 `https://api.telegram.org/bot<TOKEN>/getUpdates` 열어서 `chat.id` 확인. |
| `OLLAMA_URL` | 로컬 LLM 주소 | 기본 `http://127.0.0.1:11434`. LM Studio면 보통 `http://127.0.0.1:1234`. |
| `MODEL` | 분석에 쓸 모델 이름 | 비워두면 첫 번째로 발견된 모델을 자동 선택. |

## 실행하면?
입력값이 제대로 들어왔는지 확인 리포트만 출력합니다 (실제 데이터 호출 X). 키가 비어있으면 알려줍니다.

## 어디 저장되나?
이 폴더의 `youtube_account.json` 한 파일에. 브레인 폴더 안이라 GitHub 백업도 같이 됩니다.
