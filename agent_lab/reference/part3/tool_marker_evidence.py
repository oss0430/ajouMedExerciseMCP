@mcp.tool()
def marker_evidence(gene: str, cell_type: str) -> dict:
    """세포유형 마커 유전자의 문헌 근거를 우리 랩 기준으로 돌려줍니다: PubMed 동료심사 논문만, 제목에 유전자가 있는 논문 우선, PMID 3건.

    남의 서버(BioMCP)의 범용 문헌 검색을 우리 연구 질문에 맞게 감싼 도구입니다.
    마커 근거 논문이 필요하면 BioMCP 의 article_searcher 대신 이 도구를 씁니다.

    Args:
        gene: 마커 유전자 기호. 예) "NKG7", "CD8A"
        cell_type: 세포유형 영문명. 예) "NK cell", "CD8 T cell"
    """
    exe = shutil.which("biomcp") or os.path.expanduser("~/.local/bin/biomcp")
    if not os.path.exists(exe):
        return {"오류": "biomcp 명령을 찾을 수 없습니다.", "다음": "uv tool install biomcp-python==0.7.3"}
    cmd = [exe, "article", "search", "--gene", gene, "--keyword", cell_type,
           "--keyword", "marker", "--no-preprints", "--json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
        recs = [r for r in json.loads(out) if isinstance(r, dict) and r.get("pmid")]
    except Exception as e:                                     # 네트워크·파싱 실패도 값으로 돌려줍니다
        return {"오류": f"BioMCP 호출 실패: {type(e).__name__}", "명령": " ".join(cmd)}
    recs = [r for r in recs if r.get("publication_state", "peer_reviewed") == "peer_reviewed"]
    g = gene.upper()
    recs.sort(key=lambda r: r.get("date") or "", reverse=True)                  # 최신순
    recs.sort(key=lambda r: g not in (r.get("title") or "").upper())            # 제목에 유전자 있는 것 먼저
    근거 = [{"PMID": str(r["pmid"]), "제목": r.get("title"), "저널": r.get("journal"),
             "연도": (r.get("date") or "")[:4], "URL": r.get("pubmed_url")} for r in recs[:3]]
    if not 근거:
        return {"유전자": gene, "세포유형": cell_type, "근거": [], "안내": "조건에 맞는 동료심사 논문이 없습니다. PMID 를 지어내지 않습니다."}
    return {"유전자": gene, "세포유형": cell_type,
            "기준": "PubMed 동료심사 · 제목에 유전자 포함 우선 · 최신순 · 3건",
            "근거": 근거,
            "다음": "보고 표에는 PMID 만 적고, 없는 PMID 는 지어내지 않습니다."}
