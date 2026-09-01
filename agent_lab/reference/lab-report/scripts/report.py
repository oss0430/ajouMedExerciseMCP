#!/usr/bin/env python3
"""우리 랩 표준 보고서 생성기 — HTML (결정론적).

사용법:  python report.py run_data.json > report.html

run_data.json 을 '회사 표준 참고자료' 서식의 자체완결 HTML 로 만든다.
LLM 을 거치지 않으므로 같은 입력이면 항상 바이트 단위로 동일한 출력이 나온다.
표준 라이브러리만 사용한다(설치 불필요). 외부 리소스는 Google Fonts 링크 하나뿐이며,
없어도(오프라인) 시스템 폰트로 무난히 렌더된다.
"""
import html
import json
import sys


CSS = """
*{box-sizing:border-box}
:root{
  --bg:#eef1f4; --surface:#ffffff; --ink:#1c232b; --muted:#5b6672;
  --line:#dbe0e6; --accent:#0d6e6e; --accent-soft:#e2f0ef; --badge-ink:#ffffff;
  --up-res:#1a7f4b; --up-res-bg:#e7f3ec; --up-non:#b23a3a; --up-non-bg:#f6e9e9;
  --shadow:0 1px 2px rgba(20,30,40,.06),0 8px 30px rgba(20,30,40,.06);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0d1116; --surface:#151b22; --ink:#e6eaee; --muted:#9aa6b2;
  --line:#262e37; --accent:#4bc7c1; --accent-soft:#123030; --badge-ink:#04201f;
  --up-res:#5fd08a; --up-res-bg:#13251b; --up-non:#e88a8a; --up-non-bg:#2a1717;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 34px rgba(0,0,0,.35);
}}
:root[data-theme="dark"]{
  --bg:#0d1116; --surface:#151b22; --ink:#e6eaee; --muted:#9aa6b2;
  --line:#262e37; --accent:#4bc7c1; --accent-soft:#123030; --badge-ink:#04201f;
  --up-res:#5fd08a; --up-res-bg:#13251b; --up-non:#e88a8a; --up-non-bg:#2a1717;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 34px rgba(0,0,0,.35);
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  line-height:1.6;padding:32px 16px}
.doc{max-width:820px;margin:0 auto;background:var(--surface);
  border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);
  padding:40px 44px 30px}
.masthead{display:flex;justify-content:space-between;align-items:center;gap:16px;
  padding-bottom:14px;border-bottom:2px solid var(--accent);flex-wrap:wrap}
.std{font-size:12px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--accent);font-weight:600}
.std span{color:var(--muted);font-weight:500}
.badge{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;font-weight:500;
  letter-spacing:.04em;color:var(--badge-ink);background:var(--accent);
  padding:4px 11px;border-radius:999px;white-space:nowrap}
h1{font-family:"IBM Plex Serif",Georgia,serif;font-weight:600;
  font-size:26px;line-height:1.25;text-wrap:balance;margin:22px 0 4px}
h2{font-size:12.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
  color:var(--accent);margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
p{margin:0 0 12px;max-width:66ch}
.meta{display:grid;grid-template-columns:auto 1fr;gap:7px 22px;margin-top:18px;font-size:14px}
.meta dt{color:var(--muted);font-weight:500}
.meta dd{margin:0;font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto;margin:2px 0 6px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{text-align:left;font-weight:600;color:var(--muted);font-size:11px;letter-spacing:.05em;
  text-transform:uppercase;padding:8px 12px;border-bottom:1.5px solid var(--line)}
td{padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
.ct{font-weight:600;margin-bottom:2px}
.cl{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:11px;
  color:var(--accent);border:1px solid var(--line);border-radius:5px;
  padding:1px 6px;margin:3px 4px 0 0;white-space:nowrap}
.n{font-variant-numeric:tabular-nums;color:var(--muted)}
.gene{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:12px;
  padding:1px 6px;border-radius:5px;margin:2px 4px 2px 0;white-space:nowrap}
.up-res{color:var(--up-res);background:var(--up-res-bg)}
.up-non{color:var(--up-non);background:var(--up-non-bg)}
.none{color:var(--muted)}
.limits{border-left:3px solid var(--accent);background:var(--accent-soft);
  padding:2px 18px 14px;border-radius:0 8px 8px 0;margin-top:8px}
.limits h2{border:none;padding:0}
.limits p{margin:0;max-width:64ch}
.repro{margin-top:26px;padding-top:14px;border-top:1px solid var(--line);
  font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--muted);word-break:break-word}
.repro .k{color:var(--ink);font-weight:500}
@media(max-width:560px){.doc{padding:28px 20px}.meta{grid-template-columns:1fr;gap:2px 0}
  .meta dt{margin-top:8px}}
"""


def esc(s):
    return html.escape(str(s))


def _yn(v):
    return "O" if v else "X"


def build(data):
    ds = data["dataset"]; run = data["run"]; qc = data["qc"]; de = data["de"]
    기준 = qc.get("기준", {})
    미토 = 기준.get("미토_%", "?"); 최소 = 기준.get("최소세포", "?")
    분석일 = str(run.get("생성시각", "")).split("T")[0]
    none_html = '<span class="none">—</span>'

    rows = ""
    for r in de:
        cls = "".join(
            f'<span class="cl">{esc(c.strip())}</span>'
            for c in str(r.get("cl_id", "")).split(";") if c.strip()
        ) or none_html
        up_r = "".join(f'<span class="gene up-res">{esc(g)}</span>'
                       for g in r.get("반응군_상향", [])) or none_html
        up_n = "".join(f'<span class="gene up-non">{esc(g)}</span>'
                       for g in r.get("비반응군_상향", [])) or none_html
        rows += (
            "<tr>"
            f'<td><div class="ct">{esc(r.get("세포_유형", ""))}</div>{cls}</td>'
            f'<td class="n">{esc(r.get("유의_유전자_수", "?"))}</td>'
            f'<td>{up_r}</td>'
            f'<td>{up_n}</td>'
            "</tr>"
        )

    title = f'흑색종 ICI 차등발현 보고 · {esc(run.get("run_id", ""))}'

    body = f"""<main class="doc">
  <div class="masthead">
    <div class="std">우리 랩 · 단일세포 차등발현 보고 표준 <span>v1.0</span></div>
    <div class="badge">✓ STANDARD-COMPLIANT</div>
  </div>

  <h1>흑색종 ICI · 반응군 vs 비반응군 차등발현 보고</h1>

  <dl class="meta">
    <dt>데이터셋</dt><dd>{esc(ds.get("출처", ""))} · ID {esc(ds.get("id", ""))}</dd>
    <dt>run_id</dt><dd>{esc(run.get("run_id", ""))} (배치보정 {_yn(run.get("batch_corrected"))} · 클러스터 {esc(run.get("클러스터_수", "?"))})</dd>
    <dt>분석일</dt><dd>{esc(분석일)}</dd>
    <dt>QC</dt><dd>{"통과" if qc.get("통과") else "실패"} — 미토 중앙값 {esc(qc.get("미토_비율_중앙값_%", "?"))}% (기준 {esc(미토)}%)</dd>
  </dl>

  <h2>Methods</h2>
  <p>전처리는 정규화 {_yn(run.get("normalize", True))} · 환자·배치 통합 {_yn(run.get("batch_corrected"))} 로 수행했다.
  QC 기준은 미토콘드리아 비율 중앙값 &lt; {esc(미토)}%, 세포 수 &ge; {esc(최소)} 이다.
  차등발현은 세포 유형 안에서 반응군 vs 비반응군으로 환자 단위 비교했으며, 유의 기준은 padj &lt; 0.05 이다.</p>

  <h2>결과 · 반응군 vs 비반응군</h2>
  <div class="tablewrap">
    <table>
      <thead><tr><th>세포 유형 (Cell Ontology)</th><th>유의 유전자</th><th>반응군 &uarr;</th><th>비반응군 &uarr;</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <div class="limits">
    <h2>한계</h2>
    <p>반응군과 비반응군이 서로 다른 환자에 몰려 있어(환자↔응답 얽힘) 환자 교란 가능성이 있다. 배치보정은 {"적용" if run.get("batch_corrected") else "미적용"}되었다.</p>
  </div>

  <div class="repro">
    <span class="k">재현</span> — run_id={esc(run.get("run_id", ""))} · qc_passed={esc(run.get("qc_passed"))} · 미토기준={esc(미토)}% · 최소세포={esc(최소)} · 생성={esc(run.get("생성시각", ""))}
  </div>
</main>"""

    return (
        '<!doctype html>\n<html lang="ko">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title}</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    )


def main():
    if len(sys.argv) != 2:
        sys.exit("사용법: python report.py run_data.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    sys.stdout.write(build(data))


if __name__ == "__main__":
    main()
