# 설치 목록은 이 파일이 아니라 아래 두 곳에 있습니다.
#   ../requirements.txt   파이썬 패키지
#   ./tools.txt           uvx 로 받아둘 MCP 서버
#
# devcontainer.json 의 build.context 가 ".." 여야 requirements.txt 가 보입니다.
FROM mcr.microsoft.com/devcontainers/python:3.12

COPY requirements.txt .devcontainer/tools.txt /tmp/setup/

# ① 파이썬 패키지
RUN python3 -m pip install --no-cache-dir -r /tmp/setup/requirements.txt \
 && python3 -c "import importlib.metadata as m; print('mcp', m.version('mcp'))" \
 && uvx --version

USER vscode

# ② MCP 서버 미리 받아두기 (uvx 는 서버마다 격리된 환경을 씁니다)
RUN sed -e 's/#.*//' -e '/^[[:space:]]*$/d' /tmp/setup/tools.txt \
    | xargs -r -n1 uv tool install \
 && uv tool list

# ③ Claude Code — pip 패키지가 아니라 여기 남습니다
#    claude.ai 가 막힌 망이면: USER root / RUN npm install -g @anthropic-ai/claude-code
RUN curl -fsSL https://claude.ai/install.sh | bash \
 && ~/.local/bin/claude --version

USER root
ENV PATH="/home/vscode/.local/bin:${PATH}"
