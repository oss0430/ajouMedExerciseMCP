#!/usr/bin/env bash
# PART 3 (30분 실습) 시작 상태 만들기 + 환경 점검
#   bash agent_lab/part3_setup.sh              # 시작 상태로 되돌리고 점검
#   bash agent_lab/part3_setup.sh --with-skill # gh skill install 이 안 될 때: 저장소 사본으로 scanpy 스킬 설치
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
WITH_SKILL=0; [ "${1:-}" = "--with-skill" ] && WITH_SKILL=1

echo "════════════════════════════════════════"
echo "  PART 3 · 시작 상태 만들기"
echo "════════════════════════════════════════"

# ① .mcp.json 은 비워 둔다 — ② 단계에서 학생이 biomcp · ols 를 직접 넣는다
printf '{\n  "mcpServers": {}\n}\n' > .mcp.json
echo "  ✓ .mcp.json  비움 (②에서 채움)"

# ② settings.json 은 allow 만 — ② 단계에서 학생이 deny 를 넣는다
mkdir -p .claude
cp agent_lab/reference/part3/settings.start.json .claude/settings.json
echo "  ✓ .claude/settings.json  allow 규칙만 (deny 는 ②에서)"

# ②-b 내 서버(lab-mcp)는 시작본으로 — marker_evidence 는 ②에서 학생이 붙여 넣는다
cp agent_lab/reference/part3/lab_mcp.start.py agent_lab/lab_mcp.py
echo "  ✓ agent_lab/lab_mcp.py  시작본 (도구 1개 · marker_evidence 는 ②에서)"

# ③ scanpy 스킬은 ① 단계에서 학생이 gh skill install 로 설치한다
mkdir -p .claude/skills
rm -rf .claude/skills/scanpy
if [ "$WITH_SKILL" = "1" ]; then
  cp -R agent_lab/reference/skills/scanpy .claude/skills/scanpy
  echo "  ✓ .claude/skills/scanpy  저장소 사본으로 설치 (--with-skill)"
else
  echo "  ✓ .claude/skills/scanpy  없음 (①에서 gh skill install)"
fi

# ④ 산출물 정리
rm -rf figures out; mkdir -p out
echo "  ✓ out/ figures/  정리"

echo
python3 agent_lab/verify.py
python3 agent_lab/check.py agent_lab/lab_mcp.py 2>/dev/null || echo "  (lab-mcp 점검은 mcp 패키지가 있는 환경에서만 됩니다)"
