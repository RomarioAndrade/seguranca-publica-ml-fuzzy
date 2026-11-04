"""
montar_base_vde.py — Empilha os arquivos BancoVDE_<ano>.xlsx (SINESP/MJSP)
e gera bases por município:

  vde_municipio_mes.csv.gz  -> uma linha por (uf, municipio, mês)
  vde_municipio_ano.csv     -> uma linha por (uf, municipio, ano)

Uso:
  python montar_base_vde.py <pasta_com_xlsx> <pasta_saida>

Regras de limpeza (ver notas metodológicas do MJSP):
  * só abrangência 'Estadual' (evita contar mandados da PF em dobro);
  * exclui o município 'NÃO INFORMADO';
  * linhas repetidas no mesmo mês (ex.: Brasília) são SOMADAS, não removidas;
  * eventos de vítima usam 'total_vitima'; mandados usam 'total';
  * para homicídio doloso também guarda as vítimas do sexo feminino.
"""
import re
import sys
from pathlib import Path

import pandas as pd

# evento original -> nome curto da coluna
EVENTOS_VITIMA = {
    "Feminicídio": "feminicidio",
    "Tentativa de feminicídio": "tent_feminicidio",
    "Homicídio doloso": "homicidio",
    "Tentativa de homicídio": "tent_homicidio",
    "Roubo seguido de morte (latrocínio)": "latrocinio",
    "Lesão corporal seguida de morte": "lesao_morte",
    "Suicídio": "suicidio",
    "Morte no trânsito ou em decorrência dele (exceto homicídio doloso)": "morte_transito",
    "Mortes a esclarecer (sem indício de crime)": "mortes_esclarecer",
}
EVENTO_MANDADO = "Mandado de prisão cumprido"


def ler_ano(caminho: Path) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    df = df[(df["abrangencia"] == "Estadual") & (df["municipio"] != "NÃO INFORMADO")]
    chaves = ["uf", "municipio", "data_referencia"]

    v = df[df["evento"].isin(EVENTOS_VITIMA)]
    wide = v.pivot_table(index=chaves, columns="evento", values="total_vitima",
                         aggfunc="sum").rename(columns=EVENTOS_VITIMA)

    hom_f = (v[v["evento"] == "Homicídio doloso"]
             .groupby(chaves)["feminino"].sum().rename("homicidio_fem"))
    mand = (df[df["evento"] == EVENTO_MANDADO]
            .groupby(chaves)["total"].sum().rename("mandados"))

    out = wide.join(hom_f, how="left").join(mand, how="left").reset_index()
    return out


def main(pasta_in: str, pasta_out: str) -> None:
    pasta_in, pasta_out = Path(pasta_in), Path(pasta_out)
    pasta_out.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(pasta_in.glob("*BancoVDE_*.xlsx"))
    partes = []
    for arq in arquivos:
        ano = re.search(r"(\d{4})", arq.stem.split("_")[-1]).group(1)
        print(f"lendo {arq.name} ({ano})...")
        partes.append(ler_ano(arq))

    mes = pd.concat(partes, ignore_index=True)
    mes = (mes.groupby(["uf", "municipio", "data_referencia"], as_index=False)
              .sum(min_count=1))
    mes.insert(2, "ano", mes["data_referencia"].dt.year)
    mes.insert(3, "mes", mes["data_referencia"].dt.month)
    mes = mes.drop(columns="data_referencia").sort_values(["uf", "municipio", "ano", "mes"])

    cols_ev = [c for c in mes.columns if c not in ("uf", "municipio", "ano", "mes")]
    mes[cols_ev] = mes[cols_ev].fillna(0).astype(int)
    mes.to_csv(pasta_out / "vde_municipio_mes.csv.gz", index=False)

    ano = (mes.groupby(["uf", "municipio", "ano"])
              .agg(meses_cobertos=("mes", "nunique"), **{c: (c, "sum") for c in cols_ev})
              .reset_index())
    ano.to_csv(pasta_out / "vde_municipio_ano.csv", index=False)

    print(f"mensal: {mes.shape} | anual: {ano.shape}")
    print(ano.groupby("ano")[["meses_cobertos"]].max().T)


if __name__ == "__main__":
    main(*sys.argv[1:3])
