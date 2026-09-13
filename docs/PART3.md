# PART 3 · 기존 Skill과 MCP를 내 워크플로우에 맞게 변형하기 (30분)

> 전제: MCP · Skill 을 **연결하는 법은 이미 안다.** 오늘은 연결을 넘어 **변형**한다.
> 상황: 공개 데이터(10x PBMC 3k)를 받아 왔다. 원시 카운트에 **저자가 붙인 세포유형 라벨**이 있고, 저자 QC 에서 빠진 세포는 라벨이 없다.
> 실습용으로 1,000세포만 담았다: `data/pbmc3k_mini.h5ad`
> 목표: 우리 랩 기준으로 다시 QC 하고, 저자 라벨이 맞는지 **우리 방식으로 검증**하는 Agent 만들기

```
①  SKILL 변형 · 파라미터      K-Dense scanpy 스킬 · QC 기준        9분   재시작 없음
②  MCP  변형 · 범위          BioMCP 도구 36개 → 8개               8분   재시작 2회
③  SKILL 변형 · 워크플로우    Marker 검증 단계 · 스크립트 · 패널    10분  재시작 없음
정리                                                              3분
```

---

## 0. 시작 상태 (1분)

```bash
bash agent_lab/part3_setup.sh      # .mcp.json 비움 · settings.json allow 만 · 스킬 폴더 비움 · 점검
claude
```
```
/model         ← 학생과 같은 모델(Sonnet)인지 확인
/skills        ← scanpy 없음 (①에서 설치)
/mcp           ← 서버 없음 (②에서 연결)
```

---

## ① SKILL 변형 · 파라미터 (9분)

**연결** — 남의 스킬을 가져온다 (10초).
```bash
gh skill install K-Dense-AI/scientific-agent-skills scanpy --agent claude-code
```
> 안 되면: `bash agent_lab/part3_setup.sh --with-skill` (저장소에 든 사본으로 설치)

**실행** — 기준을 말하지 말고 QC 만 시킨다.
```
data/pbmc3k_mini.h5ad 를 scanpy 스킬로 QC 해줘
```
> `Skill(scanpy)` 가 불리고, 스킬이 시키는 대로 `scripts/qc_analysis.py` 가 **스킬 기본값** `--mt-threshold 5 --min-genes 200` 으로 돈다.
> 결과: `Cells 1000 -> 943 (94.3% kept)`. PBMC 튜토리얼 기준이지 우리 랩 기준이 아니다.

**변형** — 우리 랩 기준을 스킬 문서에 심는다. `.claude/skills/scanpy/SKILL.md` **맨 끝**에 아래를 붙인다.
```markdown
## 우리 랩 기본값 (10x PBMC)

QC 는 `scripts/qc_analysis.py` 로 실행한다. 사용자가 기준을 말하지 않으면 아래를 기본으로 쓴다.
`--mt-threshold 10 --min-genes 500 --max-genes 2500 --no-plots -o out/qc.h5ad`
근거: 미토 10% 초과는 죽어가는 세포, 유전자 500 미만은 빈 방울·저품질, 2,500 초과는 이중체 후보로 제외한다.
`--scrublet` 옵션은 쓰지 않는다. 실행 뒤 통과 세포 수(전/후)를 보고한다.
```

**확인** — 같은 문장을 그대로 다시.
```
data/pbmc3k_mini.h5ad 를 scanpy 스킬로 QC 해줘
```
> 명령줄이 우리 랩 값으로 바뀌고 `out/qc.h5ad` 가 생긴다. 결과가 `Cells 1000 -> 890 (89.0% kept)` 로 달라진다.
> **재시작 없음.** 문서 네 줄이 행동을 바꿨다. 남의 스킬이라도 내 사본은 내 것이다.
> (참고: 이 스킬의 `assets/pipeline_config.json` 은 미토 10% 인데 `qc_analysis.py` 기본값은 5% 다. 남의 스킬은 이렇게 안에서 어긋나기도 한다. 우리 기본값이 그것을 정리한다.)

---

## ② MCP 변형 · 범위 (8분)

**연결** — 남의 서버 두 개를 붙인다. `.mcp.json` **전체를** 아래로 교체하고 `/exit` → `claude`.
```json
{
  "mcpServers": {
    "biomcp": { "type": "stdio", "command": "biomcp", "args": ["run"] },
    "ols":    { "type": "http",  "url": "https://www.ebi.ac.uk/ols4/api/mcp" }
  }
}
```
```
/mcp           ← biomcp · ols connected
/context       ← MCP 도구가 차지하는 토큰을 눈여겨 둔다 (biomcp 도구 36개)
```
> 선택: 인증이 필요한 소스(Semantic Scholar 등)는 `"env": {"S2_API_KEY": "${S2_API_KEY}"}` 를 biomcp 항목에 더하면 열린다. 오늘은 키 없이 PubMed 로 충분하다.

**실행** — ③에서 쓸 마커의 근거를 확인한다.
```
③에서 NK 마커로 NKG7 을 쓰려고 해. NKG7 이 세포독성(cytotoxicity) 마커라는 근거 논문을 찾아줘
```
> 36개 도구 사이에서 헤맬 수 있다: `think` 를 먼저 부르거나 `gene_getter` 를 거친 뒤 `article_searcher` 로 간다.
> 전사체 어노테이션에 임상시험 · 약물 · 변이 · FDA 도구는 필요 없다. **출처를 문헌과 유전자 정보로 통제**한다.

**변형** — 남의 서버는 코드를 못 고친다. **설정으로 범위를 정한다.** `.claude/settings.json` 의 `"deny": []` 를 아래로 바꾸고 `/exit` → `claude`.
```json
    "deny": [
      "mcp__biomcp__trial_*",
      "mcp__biomcp__variant_*",
      "mcp__biomcp__openfda_*",
      "mcp__biomcp__nci_*",
      "mcp__biomcp__alphagenome_predictor",
      "mcp__biomcp__think"
    ]
```
> 전체 파일 모양이 헷갈리면 `agent_lab/reference/part3/settings.final.json` 을 그대로 복사한다.

**확인** — 같은 문장을 그대로 다시.
```
③에서 NK 마커로 NKG7 을 쓰려고 해. NKG7 이 세포독성(cytotoxicity) 마커라는 근거 논문을 찾아줘
```
> 이번엔 `article_searcher` 로 **직행**해 PMID 가 붙은 논문이 온다 (예: PMID 40538191 "NKG7 is a Stable Marker of Cytotoxicity …").
> `/context` 를 다시 보면 MCP 도구 토큰이 줄었다. 36개 중 28개가 Claude 의 시야에서 사라졌다. 남은 8개: search · fetch · article_searcher · article_getter · gene_getter · enrichr_analyzer · disease_getter · drug_getter.

---

## ③ SKILL 변형 · 워크플로우 (10분)

**연결** — OLS 는 ②에서 이미 붙었다. 표준 ID 를 하나 물어본다.
```
'CD8-positive exhausted alpha-beta T cell' 의 Cell Ontology ID 를 OLS 로 찾아줘
```
> `CL:0020031`. 브라우저로 `http://purl.obolibrary.org/obo/CL_0020031` 을 열면 **진짜 있는 ID** 다.

**변형 1 · 우리 스크립트를 스킬에 추가** — 라벨별로 우리 패널의 발현 비율과 상위 마커를 계산하는 스크립트.
```bash
cp agent_lab/reference/part3/check_markers.py .claude/skills/scanpy/scripts/
```

**변형 2 · 우리 랩 마커 패널을 스킬 assets 에 추가** — 스킬이 개인화용으로 배포한 `assets/gene_signatures.json` 에 우리 패널 5개(NK_lab, CD8_T_lab, CD4_T_lab, B_lab, CD14_mono_lab)를 합친다.
```bash
python3 agent_lab/reference/part3/merge_lab_signatures.py
cat .claude/skills/scanpy/assets/gene_signatures.json      # NK_lab 등이 보이면 성공
```

**변형 3 · 워크플로우 단계 추가** — `.claude/skills/scanpy/SKILL.md` 맨 끝에 붙인다.
```markdown
## 우리 랩 워크플로우: Annotate 뒤 Marker 검증

`cell_type` 라벨이 있는 QC 통과 데이터(`out/qc.h5ad`)의 라벨을 검증할 때는 아래 순서로 하고, 결과를 한 표로 보고한다.
데이터베이스 결과만 믿지 않는다. 우리 랩 패널의 발현(1)과 데이터베이스 대조(2)를 함께 보고 판정한다.

1. 패널 발현 확인 + 상위 마커 계산 (우리 스크립트):
   `python scripts/check_markers.py out/qc.h5ad --groupby cell_type --signatures assets/gene_signatures.json --top 8 --expect NK_lab="NK cells" CD8_T_lab="CD8 T cells"`
   출력의 판정(확인 / 약함 → 재검토 / 불일치)과 라벨별 상위 마커 8개를 그대로 쓴다.
2. 데이터베이스 대조: 라벨별 상위 마커 8개를 BioMCP `enrichr_analyzer(genes=[...], database="celltypes")` 에 넣어 상위 3개 세포유형을 받는다.
3. 문헌 근거: 패널 대표 마커 1개(NK cells → NKG7, CD8 T cells → CD8A)를 BioMCP `article_searcher(genes=[마커], keywords=[세포유형 영문명], include_preprints=false, page_size=3)` 로 검색해 PMID 1건을 받는다.
4. 표준 명명: OLS `searchClasses(query=<Cell Ontology 정식 명칭>, ontologyId="cl")` 로 CL ID 를 받는다. 질의는 정식 명칭으로 한다 (NK cells → "natural killer cell", CD8 T cells → "CD8-positive, alpha-beta T cell").
5. 표: `라벨 | 세포 수 | 패널 발현% (해당 라벨 / 다른 라벨 최대) | 판정 | DB 상위 유형 | CL ID | 대표 마커 · PMID`
   못 찾은 칸은 비워 두고 지어내지 않는다. 판정이 "재검토"면 이유(예: CD8A 검출 46%)를 한 줄 덧붙인다.
```

**실행**
```
out/qc.h5ad 의 NK cells 와 CD8 T cells 라벨을 우리 랩 워크플로우(Marker 검증)로 검증해서 표로 정리해줘
```
> `Skill(scanpy)` → `check_markers.py`(약 2초) → BioMCP `enrichr_analyzer` ×2 → `article_searcher` ×2 → OLS `searchClasses` ×2 → 표.
> 기대 결말:
> - **NK cells: 확인.** 패널 79% (다른 라벨 최대 33%). NKG7 100% · GNLY 96% · PRF1 96%. DB 상위는 "T Cytotoxic / NK T" 로 세포독성 림프구끼리 갈리지 않는다. 우리 패널이 확정해 준다. CL:0000623.
> - **CD8 T cells: 약함 → 재검토.** 패널 62% (CD4 T 48%). CD8A 46% · CD8B 35% 로 CD8 마커 검출이 낮다. DB 상위도 "NK / T Cells" 동률. CL:0000625.
> 저자 라벨을 그대로 믿었다면 놓쳤을 결론이다.

**확인** — SKILL(어떻게)이 우리 스크립트와 MCP 두 개를 순서대로 지휘했다. 다음 세션에서 같은 요청을 해도 같은 방식으로 움직인다.

---

## 정리 (3분)

```
                고친 곳                                  무엇이 바뀌었나
①  SKILL.md 4줄   (남의 스킬 · 문서)                    QC 기준 5/200 → 10/500~2500, 출력 out/qc.h5ad
②  settings.json 6줄 (남의 서버 · 설정)                  도구 36 → 8, 문헌 검색 직행
③  스크립트 1개 + assets 패널 + SKILL.md 한 단계           Marker 검증: 발현 → DB → 문헌 → 표준명 → 판정
```
**연결을 넘어 변형으로.** MCP = 무엇을 사용할지 · SKILL = 어떻게 할지. 내 스킬은 문서 · 스크립트 · assets 로, 남의 서버는 설정으로 고친다. 마지막 요청 하나에 오늘 고친 세 곳이 전부 쓰였고, 결론은 데이터가 냈다.

---

## 안 될 때

| 증상 | 해볼 것 |
|---|---|
| `gh skill install` 실패 | `bash agent_lab/part3_setup.sh --with-skill` |
| ① 두 번째 실행에도 플래그가 안 바뀜 | SKILL.md 맨 끝에 붙였는지 · 프롬프트에 기준을 쓰지 않았는지 → 그래도 안 되면 `/exit` → `claude` |
| ① Agent 가 `--scrublet` 을 붙여 오류 | 이 스킬 버그(scikit-image 필요). "우리 랩 기본값대로 scrublet 없이" 라고 한 번 더 말한다 |
| `/mcp` 에 biomcp 가 없다 | `.mcp.json` 쉼표·중괄호 확인 → `agent_lab/reference/part3/mcp.final.json` 복사 · 터미널에서 `biomcp --version` |
| `ols` 가 안 붙는다 | 네트워크 정책. ③의 CL ID 는 `CL:0000623 (NK)` · `CL:0000625 (CD8 T)` 로 손으로 채운다 |
| ② 두 번째에도 `think` 가 불린다 | settings.json 저장 후 **재시작**했는지 · `settings.final.json` 과 비교 |
| ③ `check_markers.py` 를 못 찾는다 | 변형 1 의 `cp` 를 했는지 · `ls .claude/skills/scanpy/scripts/` |
| ③ `NK_lab` 시그니처가 없다 | 변형 2 의 `merge_lab_signatures.py` 를 했는지 |
| ③ `find_markers.py` 가 "only contain one sample" 오류 | 정상. 세포 1개짜리 라벨 때문. 우리 스크립트(`check_markers.py --top 8`)를 쓰면 된다 |
| `No module named scanpy` | 코드스페이스 이미지 밖에서 실행 중. `python3 -c "import scanpy"` 확인 |
| 처음부터 다시 | `bash agent_lab/part3_setup.sh` |
