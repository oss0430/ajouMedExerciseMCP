"""
lab-mcp — 우리 랩 MCP 서버 (PART 3 ②)

내 서버입니다. 함수 하나가 도구 하나이고, docstring 이 곧 Claude 가 읽는 설명입니다.
남의 MCP(BioMCP)는 범용 도구 36개를 줍니다. 우리는 그중 문헌 검색을
**우리 연구 질문에 맞는 전용 도구**로 감싸서 이 서버에 둡니다.

실습 ②: 아래 "여기에 붙여 넣으세요" 자리에 marker_evidence 도구를 넣고 Claude Code 를 재시작합니다.
        (붙여 넣을 내용: agent_lab/reference/part3/tool_marker_evidence.py)
"""
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

# mcp 패키지 버전에 따라 이름이 다릅니다. 둘 다 받습니다.
try:
    from mcp.server.mcpserver import MCPServer as _Server      # mcp 2.x
except ImportError:                                            # pragma: no cover
    from mcp.server.fastmcp import FastMCP as _Server          # mcp 1.x

mcp = _Server("lab-mcp")

logging.getLogger("mcp").setLevel(logging.WARNING)   # 점검 출력에 INFO 로그가 섞이지 않게


def _find_root() -> Path:
    """이 파일이 어디에 있든 저장소 루트(agent_lab/ 가 있는 곳)를 찾습니다."""
    for p in Path(__file__).resolve().parents:
        if (p / "agent_lab" / "reference" / "part3" / "gene_signatures.lab.json").exists():
            return p
    return Path.cwd()


ROOT = _find_root()
_PANEL_FILE = ROOT / "agent_lab" / "reference" / "part3" / "gene_signatures.lab.json"


# ────────────────────────────────────────────────────────────
#  도구 ①  우리 랩 마커 패널 (예시 도구 — 이미 들어 있음)
# ────────────────────────────────────────────────────────────

@mcp.tool()
def lab_marker_panel(cell_type: str) -> dict:
    """우리 랩이 정한 세포유형별 마커 패널(기준 마커 목록)을 돌려줍니다.

    Args:
        cell_type: 예) "NK cells", "CD8 T cells", "CD4 T cells", "B cells", "CD14+ Monocytes"
    """
    panel = json.loads(_PANEL_FILE.read_text(encoding="utf-8"))
    ct = cell_type.lower()
    for key, name in (("nk", "NK_lab"), ("cd8", "CD8_T_lab"), ("cd4", "CD4_T_lab"),
                      ("b cell", "B_lab"), ("mono", "CD14_mono_lab")):
        if key in ct:
            return {"세포유형": cell_type, "패널": name, "마커": panel[name]}
    return {"거부": f"'{cell_type}' 에 해당하는 패널이 없습니다.", "있는_패널": list(panel)}


# ────────────────────────────────────────────────────────────
#  도구 ②  marker_evidence — 실습 ②에서 직접 넣습니다
# ────────────────────────────────────────────────────────────

# ↓↓↓ 실습 ②: 여기에 marker_evidence 도구를 붙여 넣으세요 ↓↓↓
#     (agent_lab/reference/part3/tool_marker_evidence.py 의 내용 전체)


if __name__ == "__main__":
    mcp.run()
