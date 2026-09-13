# PART 3 프롬프트 모음 (복사용) · 기준값을 프롬프트에 쓰지 않는다

## ① SKILL 변형 · 파라미터
data/pbmc3k_mini.h5ad 를 scanpy 스킬로 QC 해줘
(SKILL.md 수정 뒤, 같은 문장 그대로 다시)

## ② MCP 변형 · 범위
③에서 NK 마커로 NKG7 을 쓰려고 해. NKG7 이 세포독성(cytotoxicity) 마커라는 근거 논문을 찾아줘
(settings.json deny 적용·재시작 뒤, 같은 문장 그대로 다시)

## ③ SKILL 변형 · 워크플로우
'CD8-positive exhausted alpha-beta T cell' 의 Cell Ontology ID 를 OLS 로 찾아줘
out/qc.h5ad 의 NK cells 와 CD8 T cells 라벨을 우리 랩 워크플로우(Marker 검증)로 검증해서 표로 정리해줘
