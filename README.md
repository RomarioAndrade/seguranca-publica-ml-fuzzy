# Pipeline Integrado de IA — EXEMPLO com dados reais: facções na Amazônia Legal
### Trabalho Integrado de Fundamentos de IA (Domínio P3: Segurança Pública) — Prof. Edjard Mota

> **Exemplo didático** para comparar com o exemplo de feminicídio (`../exemplo_feminicidio_dados_reais`).

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
| `etapa1.ipynb` | Entropia, ganho, 3 níveis calculados, ID3 do zero × scikit-learn, 5-fold, monotonicidade |
| `etapa2.ipynb` | Regressão de homicídios 2023 (com log da população): simples, multivariada (GD), Ridge; logística para facção |
| `etapa3.ipynb` | Conjunta, condicionais, Bayes, regra da cadeia, independência condicional, **transições 2024 → 2025** |
| `etapa4.ipynb` | MLE × MAP por UF, Naive Bayes do zero, **EM com 3 regimes ocultos** (contagem × taxa) comparados ao Cartografias |
| `etapa5.ipynb` | Rede bayesiana com colisor PORTE → FACCAO ← FRONT, enumeração × pgmpy, d-separação |
| `etapa6.ipynb` | Fuzzy Mamdani: prioridade de monitoramento; **validação fora do tempo com as entradas de 2025** |
| `utils.py`, `em.py`, `fuzzy.py` | Módulos de apoio |
| `montar_base_vde.py`, `montar_populacao_ibge.py`, `extrair_cartografias_2025.py` | Scripts que geram as bases |
| `dados/` | Base rotulada com população, tabelas do Cartografias 2024 e 2025, população do IBGE e as probabilidades da Etapa 5 |
| `relatorio_exemplo.tex` | Esqueleto do relatório com os resultados |

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
| 3 | P(facção \| taxa alta) = 0,42 contra 0,27. Entre os sem facção em 2024, 23,5% entraram em 2025 (14% pequenos, 37% grandes) |
| 4 | Naive Bayes 77,4% (bal. 0,74); NB + EM 78,0% (bal. 0,75). EM: no grupo mais violento, 29% em disputa; no menos, 1,7% |
| 5 | 19 parâmetros contra 215 da conjunta; enumeração idêntica ao pgmpy. Rede como classificador: AUC 0,81 |
| 6 | Prioridade alta: 62% com facção (2024). **Entrada em 2025:** 13% na prioridade baixa, 45% na alta; AUC 0,77. Janela 2022–24 não melhora (AUC 0,754 nas duas); salto de homicídios em 2024 não antecipa a chegada |

## Como reproduzir

```bash
pip install -r requirements.txt
python utils.py
jupyter nbconvert --to notebook --execute --inplace etapa1.ipynb   # ... até etapa6 (em ordem)
```

## Limitações
- "Sem registro" no Cartografias significa facção não identificada pelos pesquisadores, não ausência certa.
- Parte das mudanças entre a 3ª e a 4ª edição vem da melhoria do método (o próprio relatório avisa); 45 municípios "saíram" da lista.
- O próprio relatório tem pequenas divergências entre as tabelas por estado e o quadro-resumo (AP, PA, TO);
  definimos "disputa" pelo número de facções listadas.
- O Maranhão entra inteiro (217 municípios), mas só 181 pertencem à Amazônia Legal.
- A violência indica **onde** a facção tende a estar, mas não **quando** chega: o salto de 2024 tem o mesmo efeito do salto de 2023.
- 2023 não tem estimativa do IBGE; as taxas de 2021–23 usam a população do Censo 2022.
