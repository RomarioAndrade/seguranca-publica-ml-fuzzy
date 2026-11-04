"""Extrai as listas 'Presença de facções em municípios no Estado de ...' do PDF
da 4ª edição do Cartografias da Violência na Amazônia (2025).
Uso: python extrair_cartografias_2025.py <texto_pdftotext_layout.txt> <saida.csv>"""
import re, sys
import pandas as pd

EST = {'Acre': 'AC', 'Amapá': 'AP', 'Amazonas': 'AM', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
       'Pará': 'PA', 'Rondônia': 'RO', 'Roraima': 'RR', 'Tocantins': 'TO'}
FAC = re.compile(r'^(CV|PCC|B40|B13|FTA|UCA|BDM|PCM|GDE|TDR|ADE|EMC|PCP|CCA|TROPA|Piratas|Tren|Trem)', re.I)
sp = lambda l: [p.strip() for p in re.split(r'\s{2,}', l.strip()) if p.strip()]

L = open(sys.argv[1], encoding='utf-8').read().split('\n')
rows = []
for i, l in enumerate(L):
    if 'Presença de' not in l or 'facç' not in l:
        continue
    p = sp(l)
    if not p or p[0] not in EST:
        continue
    if len(p) == 5:                       # linha completa
        est, mun, fac, sit, tip = p
    elif len(p) == 4:                     # um campo quebrou em duas linhas (acima e abaixo)
        extra = (' '.join(sp(L[i - 1])) + ' ' + ' '.join(sp(L[i + 1]))).strip()
        if FAC.match(p[1]):               # faltou o nome do município
            est, fac, sit, tip = p; mun = extra
        else:                             # faltou a lista de facções
            est, mun, sit, tip = p; fac = extra
    else:
        raise ValueError(f'linha {i+1} inesperada: {p}')
    rows.append(dict(estado=est, uf=EST[est], municipio=re.sub(r'\s+', ' ', mun).strip(),
                     faccoes=re.sub(r'\s+', ' ', fac).strip(),
                     situacao='Presença de duas ou mais facções' if 'duas' in sit.lower() else 'Presença de uma facção',
                     tipologia=tip, linha_txt=i + 1))
d = pd.DataFrame(rows)
d.drop(columns='linha_txt').to_csv(sys.argv[2], index=False)
print(d.shape, 'duplicados:', d.duplicated(['uf', 'municipio']).sum())
print(d.groupby('uf').size().to_dict())
print(d.situacao.value_counts().to_dict()); print(d.tipologia.value_counts().to_dict())
print(d[d.linha_txt.isin([3926, 3946, 3951, 4084, 4211, 4272, 4277, 4280, 4288, 4509, 4708, 4716, 4720])][['uf', 'municipio', 'faccoes', 'situacao']].to_string())
