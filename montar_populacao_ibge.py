"""
montar_populacao_ibge.py — junta as estimativas de população do IBGE (2020, 2021, 2024, 2025),
o Censo 2022 (população total e de mulheres) e calcula 2023 por interpolação.

Uso:
  python montar_populacao_ibge.py <pasta_com_arquivos_ibge> <saida.csv>

Arquivos esperados na pasta:
  POP2020_20220905.xls, POP2021_20240624.xls, POP2024_20241230.xls, POP2025_20260828.xls,
  CD2022_Populacao_Coletada_Imputada_e_Total_Municipio_e_UF_20231222.xlsx,
  Agregados_por_municipios_demografia_BR.zip (contém o CSV com V01006 = moradores, V01008 = mulheres)
"""
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

UF_COD = {11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA", 22: "PI",
          23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA", 31: "MG", 32: "ES",
          33: "RJ", 35: "SP", 41: "PR", 42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF"}


def numero(v):
    """Remove notas de rodapé, pontos e espaços: '12.345(1)' -> 12345."""
    s = re.sub(r"\(.*?\)", "", str(v))
    s = re.sub(r"[^0-9]", "", s)
    return int(s) if s else None


def ler_estimativa(arq, ano):
    x = pd.ExcelFile(arq)
    aba = [s for s in x.sheet_names if s.upper().startswith("MUNIC")][0]
    df = x.parse(aba, header=1, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df[df["COD. UF"].fillna("").str.strip().str.isdigit()]
    out = pd.DataFrame({
        "cod_ibge": df["COD. UF"].str.strip() + df["COD. MUNIC"].str.strip().str.zfill(5),
        "uf": df["UF"].str.strip(),
        "municipio_ibge": df["NOME DO MUNICÍPIO"].str.strip(),
        f"pop_{ano}": df["POPULAÇÃO ESTIMADA"].map(numero),
    })
    return out


def ler_censo(arq):
    df = pd.read_excel(arq, sheet_name="Municípios", header=2, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df[df["COD. UF"].fillna("").str.strip().str.isdigit()]
    return pd.DataFrame({
        "cod_ibge": df["COD. UF"].str.strip() + df["COD. MUNIC"].str.strip().str.zfill(5),
        "pop_2022": df["POP. TOTAL"].map(numero),
    })


def ler_mulheres(arq_zip):
    with zipfile.ZipFile(arq_zip) as z:
        nome = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        df = pd.read_csv(z.open(nome), sep=";", dtype=str, encoding="latin-1")
    return pd.DataFrame({"cod_ibge": df["CD_MUN"].str.strip(),
                         "mulheres_2022": df["V01008"].map(numero)})


def main(pasta, saida):
    p = Path(pasta)
    pop = ler_estimativa(p / "POP2020_20220905.xls", 2020)
    for arq, ano in [("POP2021_20240624.xls", 2021), ("POP2024_20241230.xls", 2024), ("POP2025_20260828.xls", 2025)]:
        pop = pop.merge(ler_estimativa(p / arq, ano)[["cod_ibge", f"pop_{ano}"]], on="cod_ibge", how="outer")
    pop = pop.merge(ler_censo(p / "CD2022_Populacao_Coletada_Imputada_e_Total_Municipio_e_UF_20231222.xlsx"),
                    on="cod_ibge", how="left")
    pop = pop.merge(ler_mulheres(p / "Agregados_por_municipios_demografia_BR.zip"), on="cod_ibge", how="left")
    pop["pop_2023"] = ((pop["pop_2022"] + pop["pop_2024"]) / 2).round()   # sem estimativa oficial em 2023
    pop["uf"] = pop["uf"].fillna(pop["cod_ibge"].str[:2].astype(int).map(UF_COD))
    cols = ["cod_ibge", "uf", "municipio_ibge"] + [f"pop_{a}" for a in range(2020, 2026)] + ["mulheres_2022"]
    pop = pop[cols].sort_values("cod_ibge")
    pop.to_csv(saida, index=False)
    print(pop.shape)
    print(pop.isna().sum()[pop.isna().sum() > 0])
    return pop


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
