# 환경 구축 — 강사용

> `isg-bspark/ajou-omics-env` 에 넣을 것과, 기존 설정과 합치는 방법.

---

## 1. 넣을 파일

```
ajou-omics-env/
├── .devcontainer/
│   ├── Dockerfile             ← mcp · Claude Code 를 이미지에 굽습니다 ★
│   ├── devcontainer.json      ← 기존 것이 있으면 3절 참고해서 병합
│   └── postCreate.sh          ← 점검만 (verify.py 실행)
├── requirements.txt
├── .mcp.json                  ← 반드시 저장소 루트
├── README.md                  ← 수강생 첫 화면 (선택)
└── agent_lab/
    ├── server.py              도구 3개 · 거부 규칙은 주석 상태
    ├── verify.py              환경 점검 (6항목)
    ├── check.py               서버 단독 점검
    ├── LAB.md                 수강생용 실습 안내
    └── INSTRUCTOR.md          당일 운영 · 대본
```

---

## 2. 확인된 요구사항

| | |
|---|---|
| **Python** | **3.10 이상** — `mcp` 패키지가 `>=3.10` 을 요구합니다 |
| **패키지** | `mcp[cli]` 하나. 현재 최신 **2.0.0** |
| **claude** | `curl -fsSL https://claude.ai/install.sh \| bash` |
| **API 키** | `ANTHROPIC_API_KEY` (Codespaces 시크릿) |
| **머신** | 2코어 / 8GB 로 충분합니다 — 실제 계산을 하지 않습니다 |

`server.py` 는 `mcp` **1.x · 2.x import 를 둘 다** 받게 써두었습니다. 버전이 올라가도 안 깨집니다.

---

## 2-1. 왜 Dockerfile 인가 — 그리고 postCreate 는 왜 남는가

### 시점이 다릅니다

```
[이미지 빌드]      저장소가 아직 없습니다. 시크릿도 없습니다.
      ↓
[컨테이너 생성]    저장소가 /workspaces 에 마운트됩니다.
                   Codespaces 시크릿이 환경변수로 들어옵니다.
      ↓
[postCreate]       여기서부터 저장소 파일을 볼 수 있습니다.
```

| | 이미지에 넣을 수 있나 |
|---|---|
| `mcp` 패키지 · Claude Code | **○ 넣어야 합니다** — 매번 설치할 이유가 없습니다 |
| **API 키** | **✕** 이미지에 구우면 이미지를 받은 사람 누구나 봅니다 |
| **저장소 코드** | **✕** 빌드 시점엔 아직 없습니다 |
| `verify.py` 실행 | **✕** 저장소가 있어야 하니 postCreate |

그래서 이렇게 갈랐습니다.

| | 하는 일 | 실패하면 |
|---|---|---|
| **Dockerfile** | `mcp` 설치 + `import` 검증<br>Claude Code 설치 + `--version` 검증 | **빌드가 멈춥니다** — 바로 압니다 |
| **postCreate.sh** | `verify.py` 실행 (점검만) | 화면에 무엇이 없는지 표시 |

**postCreate 에 설치는 남아 있지 않습니다.** 점검 한 줄뿐입니다.

### ★ Prebuild 를 켜세요

**Settings → Codespaces → Prebuild configuration → Set up prebuild** (`main`)

빌드가 GitHub 쪽에서 **한 번만** 돌고, 수강생은 완성된 이미지를 받습니다.

- 사전배포 7장의 **"5~10분 소요"** 가 사라집니다
- 로그에 보이던 **20개 레이어 pull + 설치**가 매번 반복되지 않습니다
- **30명이 동시에 만들 때 실패 확률이 크게 줄어듭니다**
- 빌드가 깨지면 **prebuild 단계에서** 드러납니다 — 강의 당일이 아니라

> Dockerfile 이 실패하도록(fatal) 만든 이유가 이것입니다.
> 빌드는 강사가 한 번 하고, 수강생은 그 결과만 받습니다.

---

## 3. 기존 devcontainer 와 합치기

**기존 것을 덮어쓰지 마세요.** 세 가지만 있으면 됩니다.

### ① 이미지 — Dockerfile 로

```jsonc
// 전
"image": "<기존 이미지>"

// 후
"build": { "dockerfile": "Dockerfile" }
```

그리고 `.devcontainer/Dockerfile` 의 `FROM` 을 **기존 이미지로 바꾸세요.**

```dockerfile
FROM <기존 이미지>
RUN python3 -m pip install --no-cache-dir "mcp[cli]" && python3 -c "import mcp"
```

**Python 3.10 이상**이어야 합니다 — `mcp` 가 요구합니다.

### ② `postCreateCommand` 뒤에 이어 붙이기

```jsonc
// 전
"postCreateCommand": "<기존 명령>"

// 후
"postCreateCommand": "<기존 명령> && bash .devcontainer/postCreate.sh"
```

`postCreate.sh` 는 **아무것도 설치하지 않습니다.** `verify.py` 를 돌려 화면에 결과만 찍습니다.

### ③ (선택) VS Code 확장

```jsonc
"customizations": { "vscode": { "extensions": ["anthropic.claude-code"] } }
```

---

## 4. 사전배포 자료와의 관계

`postCreate.sh` 가 **Claude Code 를 자동 설치**합니다.
그러면 사전배포 **8장(`curl … install.sh | bash` 직접 입력)이 불필요**해집니다.

두 가지 중 하나를 고르세요.

| | |
|---|---|
| **A · 권장** | 자동 설치를 쓰고, 8장은 *"자동으로 설치됩니다. 안 되면 이 명령"* 으로 바꿉니다 |
| **B** | `postCreate.sh` 의 ① 블록을 지우고, 사전배포대로 수강생이 직접 입력합니다 |

**A 가 낫습니다.** 30명이 각자 `curl` 을 치는 시간이 사라집니다. 그리고 실패해도 안내 문구가 나옵니다.

---

## 5. ⚠ Fork 타이밍 — 지금 결정하셔야 합니다

사전배포가 이미 나갔다면, 수강생 일부가 **이미 fork** 했습니다.
그 뒤에 업스트림에 파일을 추가해도 **각자 fork 에는 들어가지 않습니다.**

| | |
|---|---|
| **A · 권장** | **지금 다 넣고 확정.** 이후 저장소를 건드리지 않습니다 |
| **B** | 당일 첫 순서로 GitHub **Sync fork** 안내 (스크린샷 한 장 필요) |

---

## 6. 구축 후 검증 — 이 순서로

### 강사 로컬 또는 테스트 코드스페이스에서

```bash
python3 agent_lab/verify.py
```

여섯 항목이 모두 ✓ 여야 합니다.

```
✓ Python 3.10 이상        3.12.x
✓ mcp 패키지              v2.0.0
✓ claude 명령             /home/vscode/.local/bin/claude
✓ API 키 환경변수          ANTHROPIC_API_KEY
✓ .mcp.json               .mcp.json
✓   서버 항목              sc-omics
✓   sc-omics 스크립트      agent_lab/server.py
✓ 서버 응답               도구 3개
```

### 그다음 Claude Code 로

```bash
claude
/mcp                      # sc-omics 가 connected
```

```
이 데이터가 뭔지 알려줘
```

`dataset_overview` 가 불리고 **세포 12,000** 이 나오면 끝입니다.

### 마지막으로 실습 ② 상태

`agent_lab/server.py` 의 `# ` 네 줄을 지우고 재시작해서 **거부가 나오는지** 확인하세요.
확인 후 **반드시 되돌려 놓으세요.** (`git checkout agent_lab/server.py`)

---

## 7. 원격 서버 — 강의 전날 확인

실습 ③에 쓸 무인증 원격 서버입니다. **실제로 붙여보셔야 합니다.**

```bash
claude mcp add -s user -t http biocontext https://mcp.biocontext.ai/mcp/
claude
/mcp
```

| | |
|---|---|
| **1안** | `https://mcp.biocontext.ai/mcp/` — 생명과학 DB 묶음. **사용량 제한 있음** |
| **2안** | `https://mcp.deepwiki.com/mcp` — GitHub 저장소 질문. 안정적 |

**사용량 제한 때문에 실습 ③은 강사 시연으로만** 하시는 편이 안전합니다.
그리고 조직 Codespaces 네트워크 정책으로 막힐 수 있으니 **테스트 코드스페이스 안에서** 확인하세요.

---

## 8. 체크리스트

- [ ] 파일 6개 + `.devcontainer` 2개 커밋
- [ ] 기존 `devcontainer.json` 과 병합 (3절)
- [ ] 사전배포 8장 처리 결정 (4절)
- [ ] Fork 타이밍 결정 (5절)
- [ ] 테스트 코드스페이스에서 `verify.py` 6항목 통과
- [ ] `claude` → `/mcp` → 도구 호출까지 확인
- [ ] 실습 ② 거부 확인 후 `server.py` 되돌리기
- [ ] 원격 서버 두 개 중 최소 하나 확인
