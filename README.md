# Do Simbólico à Incerteza: facções criminosas na Amazônia Legal
### Trabalho Integrado de Fundamentos de IA (Domínio P3: Segurança Pública) — Prof. Edjard Mota — IComp/UFAM 2026/2

**Equipe 1:** Gabriel Menezes Rodrigues, Luiz Felipe Gonzaga do Carmo, Joshua Tadeu Bastos Pereira,
Romário Roberto de Pádua Andrade, Ruan Pablo Nascimento de Aragão, Fernando Teles dos Reis.

**Relatório:** [`tex/relatorio.pdf`](tex/relatorio.pdf) (LaTeX em `tex/relatorio.tex`).

**Pergunta:** o município da Amazônia Legal tem presença de facção criminosa (2024), dado o seu
porte e o padrão de violência registrado entre 2021 e 2023? E o modelo antecipa quais
municípios passaram a ter facção em 2025?

- **Rótulos:** *Cartografias da Violência na Amazônia* (Instituto Mãe Crioula / Fórum Brasileiro de
  Segurança Pública) — 3ª edição (2024, Tabelas 13–21) e 4ª edição (2025, quadros por estado,
  extraídos do PDF com `extrair_cartografias_2025.py`).
- **Atributos:** SINESP VDE / Ministério da Justiça, 2020–2023 (2024 entra no teste da janela 2022–24 e do salto de homicídios, Etapa 6).
- **População:** IBGE (Censo 2022 e estimativas), juntada pelo código IBGE.
- **Unidade:** 808 municípios dos 9 estados da Amazônia Legal. Com facção: 32,1% em 2024 e 42,5% em 2025.

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `etapa1.ipynb` | Entropia, ganho, 3 níveis calculados, ID3 do zero × scikit-learn, 5-fold, monotonicidade; grava o ganho e as decisões da árvore para a Etapa 5 |
| `etapa2.ipynb` | Regressão de homicídios 2023 (com log da população): simples, multivariada (GD), Ridge; logística para facção |
| `etapa3.ipynb` | Conjunta, condicionais, Bayes, regra da cadeia, independência condicional, **transições 2024 → 2025**, **garimpo × entrada em 2025** |
| `etapa4.ipynb` | MLE × MAP por UF, Naive Bayes do zero, **EM com 3 regimes ocultos** (contagem × taxa) comparados ao Cartografias; grava a P(facção) do NB + EM para a Etapa 6 |
| `etapa5.ipynb` | Rede bayesiana com colisor PORTE → FACCAO ← FRONT (pais escolhidos pelo ganho da Etapa 1), enumeração × pgmpy, d-separação, **rede × árvore da Etapa 1**; **validação deixando um estado de fora** e sensibilidade ao rótulo |
| `etapa6.ipynb` | Fuzzy Mamdani: prioridade de monitoramento a partir das probabilidades das Etapas 4 e 5; **validação fora do tempo com as entradas de 2025** |
| `experimentos_variaveis.ipynb` | 15 variáveis de outras bases testadas na rede (fronteira por município, VDE, IBGE, INPE, IBAMA) |
| `utils.py`, `em.py`, `fuzzy.py` | Módulos de apoio |
| `montar_base_vde.py`, `montar_populacao_ibge.py`, `extrair_cartografias_2025.py` | Scripts que geram as bases |
| `montar_bases_externas.py` | Baixa e agrega IBGE, INPE e IBAMA em `dados/variaveis_externas_municipio.csv` (brutos em `dados/brutos/`, fora do git) |
| `dados/` | Base rotulada com população, tabelas do Cartografias 2024 e 2025, população do IBGE e as saídas reutilizadas entre etapas (`ganho_etapa1.csv`, `decisoes_arvore.csv`, `probabilidades_etapa4.csv`, `probabilidades_bayesianas.csv`) |
| `tex/relatorio.tex`, `tex/relatorio.pdf` | Relatório final (formato artigo, 7 páginas) |
| `artigos/README.md` | Artigos científicos citados, com links e onde cada um embasa o relatório |
| `figuras/` | Figuras geradas pelos notebooks e usadas no relatório |

## Atributos

| Variável | Definição |
|---|---|
| `PORTE` | População (Censo 2022): pequeno (<10 mil), médio (10–50 mil), grande (50 mil+) |
| `TXH` | Taxa anual de homicídio 2021–23 por 100 mil hab., em tercis |
| `TXT` | Taxa anual de tentativas de homicídio 2021–23 por 100 mil hab., em tercis |
| `ESC` | Teve morte a esclarecer em 2021–23 |
| `LATRO` | Teve latrocínio em 2021–23 |
| `UF` / `FRONT` | Estado / estado faz fronteira com outro país (usado na rede bayesiana) |

## Principais resultados (`seed = 42`)

| Etapa | Resultado |
|---|---|
| 1 | Maior ganho: PORTE (0,165). ID3 prof. 3: acurácia 78,6%, balanceada 0,71 |
| 2 | R² homicídios 2023: simples 0,67; multivariada 0,76; Ridge 0,76. Logística (facção): 75,9%, bal. 0,74 |
| 3 | P(facção \| taxa alta) = 0,42 contra 0,27. Entre os sem facção em 2024, 23,5% entraram em 2025 (14% pequenos, 37% grandes). Com garimpo em 2021–23 (IBAMA ou INPE), 45% entraram, contra 22% sem |
| 4 | Naive Bayes 77,2% (bal. 0,74); NB + EM 77,7% (bal. 0,75). EM: no grupo mais violento, 29% em disputa; no menos, 1,7%. P(facção) do NB + EM fora da dobra: AUC 0,84 |
| 5 | Pais de FACCAO = 2 maiores ganhos da Etapa 1 (PORTE, UF→FRONT). 19 parâmetros contra 215 da conjunta; enumeração idêntica ao pgmpy. Rede como classificador: AUC 0,81 (árvore da Etapa 1: 0,81; concordam em 83%); deixando um estado de fora, 0,80, mas erra o nível em AC e RR (P média ≈ 0,47 com 93–100% de facção). Sem os 45 que "saíram" da lista: AUC 0,83 |
| 6 | Presença = média da P(facção) da rede (E5) e do NB + EM (E4), fora da dobra. Prioridade alta: 64% com facção (2024). **Entrada em 2025:** 14% na prioridade baixa, 45% na alta; AUC 0,75 (rede sozinha: 0,76). Janela 2022–24 não melhora (AUC 0,754 nas duas); salto de homicídios em 2024 não antecipa a chegada |
| Experimentos | Nenhuma das 15 variáveis externas melhora a rede de forma consistente. Fronteira por município: AUC 2024 0,84, mas entrada 2025 cai para 0,71 |

## Como reproduzir

```bash
pip install -r requirements.txt
python utils.py
python montar_bases_externas.py      # baixa ~140 MB na primeira vez
for i in 1 2 3 4 5 6; do jupyter nbconvert --to notebook --execute --inplace etapa$i.ipynb; done
jupyter nbconvert --to notebook --execute --inplace experimentos_variaveis.ipynb
cd tex && latexmk -pdf relatorio.tex   # relatório
```

A ordem importa: a Etapa 1 grava `dados/ganho_etapa1.csv` e `dados/decisoes_arvore.csv`, lidos pela Etapa 5;
a Etapa 4 grava `dados/probabilidades_etapa4.csv` e a Etapa 5 grava `dados/probabilidades_bayesianas.csv`, lidos pela Etapa 6.
Testado com Python 3 e as versões de `requirements.txt`; os números acima saem com `seed = 42`.

## Validação
- **Validação cruzada (5 dobras estratificadas, `seed = 42`)** com o rótulo de 2024. Os tercis de `TXH` e `TXT` são
  recalculados com os cortes do treino de cada dobra (`utils.tercis_do_treino`), para o teste não influenciar os cortes.
- **Deixando um estado de fora** (Etapa 5): treina com 8 estados e testa no 9º.
- **Fora do tempo** (Etapas 3 e 6): entre os 549 municípios sem facção em 2024, quais passaram a ter em 2025.
  As probabilidades usadas na Etapa 6 (Etapas 4 e 5) e as decisões da árvore usadas na Etapa 5 são calculadas fora da dobra, com as mesmas 5 dobras.
- **Sensibilidade ao rótulo** (Etapa 5): sem os municípios que "saíram" da lista e com o rótulo "facção em 2024 ou 2025".

## Limitações
- "Sem registro" no Cartografias significa facção não identificada pelos pesquisadores, não ausência certa.
- Parte das mudanças entre a 3ª e a 4ª edição vem da melhoria do método (o próprio relatório avisa); 45 municípios "saíram" da lista.
- O próprio relatório tem pequenas divergências entre as tabelas por estado e o quadro-resumo (AP, PA, TO);
  definimos "disputa" pelo número de facções listadas.
- O Maranhão entra inteiro (217 municípios), mas só 181 pertencem à Amazônia Legal..
- `FRONT` é definido por estado e só separa MA e TO dos demais; por isso a rede não acerta o nível de facção num estado
  que não viu (Acre e Roraima). A faixa de fronteira por município corrige isso, mas piora a previsão de 2025 (`experimentos_variaveis.ipynb`).
- A violência indica **onde** a facção tende a estar, mas não **quando** chega: o salto de 2024 tem o mesmo efeito do salto de 2023.
- 2023 não tem estimativa do IBGE; as taxas de 2021–23 usam a população do Censo 2022.

## Fontes (acesso em out./nov. 2026)
- Ministério da Justiça e Segurança Pública — Banco VDE (SINESP): https://dadosabertos.mj.gov.br
- IBGE — Censo 2022 e Estimativas da População: https://www.ibge.gov.br
- IBGE — Municípios da Faixa de Fronteira 2024, malha municipal (API v3), SIDRA tabela 9923, REGIC 2018: https://www.ibge.gov.br
- INPE — DETER Amazônia (TerraBrasilis): https://terrabrasilis.dpi.inpe.br
- IBAMA — autos de infração e termos de destruição: https://dadosabertos.ibama.gov.br (só contagens por município; os arquivos brutos identificam os autuados)
- Instituto Mãe Crioula e Fórum Brasileiro de Segurança Pública — *Cartografias da Violência na Amazônia*, 3ª ed. (2024) e 4ª ed. (2025)

## Uso de assistente de IA
Parte do código e do texto foi gerada com apoio de um assistente (Claude, via Claude Code) e revisada pela equipe.
Os principais pedidos estão no Apêndice A do relatório.
^
