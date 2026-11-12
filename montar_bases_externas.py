"""
montar_bases_externas.py — variáveis de outras bases abertas, por município, para os experimentos.

Gera dados/variaveis_externas_municipio.csv (808 municípios), usado em experimentos_variaveis.ipynb.
Os arquivos brutos são baixados para dados/brutos/ (fora do git)
e reaproveitados se já existirem.

Fontes (acesso em nov. 2026):
  * IBGE — Municípios da Faixa de Fronteira 2024 (geoftp.ibge.gov.br)
  * IBGE — Malha municipal (API de malhas v3), para a vizinhança entre municípios
  * IBGE — Censo 2022, população urbana e rural (SIDRA, tabela 9923)
  * IBGE — REGIC 2018, hierarquia urbana
  * INPE — DETER Amazônia (TerraBrasilis), alertas 2021–23: desmatamento e mineração
  * IBAMA — Autos de infração e termos de destruição 2021–23 (dadosabertos.ibama.gov.br)

Os arquivos do IBAMA têm nome e CPF/CNPJ dos autuados; aqui só guardamos contagens por município.
"""
import json
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from utils import PASTA, carregar_base

BRUTOS = PASTA / "dados" / "brutos"
SAIDA = PASTA / "dados" / "variaveis_externas_municipio.csv"
UFS = ["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"]
ANOS = ("2021", "2022", "2023")

URL_FAIXA = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/"
             "municipios_da_faixa_de_fronteira/2024/Mun_Faixa_de_Fronteira_Cidades_Gemeas_2024.xls")
URL_MALHA = ("https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf}?intrarregiao=municipio"
             "&formato=application/vnd.geo%2Bjson&qualidade=intermediaria")
URL_SIDRA = "https://apisidra.ibge.gov.br/values/t/9923/n6/all/v/93/p/2022/c1/allxt"
URL_REGIC = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/divisao_regional/regioes_de_influencia_das_cidades/"
             "Regioes_de_influencia_das_cidades_2018_Resultados_definitivos/base_tabular/"
             "REGIC2018_Municipios_Hierarquia_e_regiao.xlsx")
# O servidor devolve no máximo 50 mil feições por pedido e a paginação não é estável:
# pedimos um semestre por vez, cada um abaixo do limite.
URL_DETER = ("https://terrabrasilis.dpi.inpe.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature"
             "&typeNames=deter-amz:deter_amz&outputFormat=csv&propertyName=classname,view_date,areamunkm,mun_geocod,uf"
             "&CQL_FILTER=view_date%20BETWEEN%20'{ini}'%20AND%20'{fim}'")
URL_AUTOS = ("https://stibamadadosabertosprd.blob.core.windows.net/dados-abertos/dados/SIFISC/"
             "auto_infracao/auto_infracao/auto_infracao_csv.zip")
URL_TAD = ("https://stibamadadosabertosprd.blob.core.windows.net/dados-abertos/dados/TERMOS/"
           "TERMO_DESTRUICAO/termo_destruicao_inutilizacao.csv")

# Autos de infração de garimpo ou mineração ilegal, pela descrição do auto
PADRAO_GARIMPO = (r"\bgarimp|\blavra\b|\blavrar\b|extra[çc][ãa]o mineral|recursos? minera|subst[âa]ncias? minera"
                  r"|\bmin[ée]rios?\b|\bouro\b|cassiterita|merc[úu]rio|\bdragas?\b|pesquisa mineral")


def baixar(url, destino):
    destino = Path(destino)
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        print("baixando", destino.name)
        urllib.request.urlretrieve(url, destino)
    return destino


def faixa_de_fronteira():
    x = pd.read_excel(baixar(URL_FAIXA, BRUTOS / Path(URL_FAIXA).name), dtype={"CD_MUN": str})
    x = x.dropna(subset=["CD_MUN"]).set_index("CD_MUN")
    return pd.DataFrame({"faixa_fronteira": 1, "toca_limite": (x["TOCA_LIM"] == "SIM").astype(int)})


def vizinhos():
    """Dois municípios são vizinhos se as malhas compartilham pelo menos 2 vértices."""
    vert = defaultdict(set)
    for uf in UFS:
        g = json.load(open(baixar(URL_MALHA.format(uf=uf), BRUTOS / "malhas" / f"{uf}.json")))
        for f in g["features"]:
            cod, geo = f["properties"]["codarea"], f["geometry"]
            polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
            for poly in polys:
                for anel in poly:
                    for x, y in anel:
                        vert[(round(x, 4), round(y, 4))].add(cod)
    comum = defaultdict(int)
    for cods in vert.values():
        for a in cods:
            for b in cods:
                if a < b:
                    comum[(a, b)] += 1
    viz = defaultdict(set)
    for (a, b), n in comum.items():
        if n >= 2:
            viz[a].add(b); viz[b].add(a)
    return pd.Series({c: ";".join(sorted(v)) for c, v in viz.items()}, name="vizinhos")


def urbanizacao():
    u = pd.DataFrame(json.load(open(baixar(URL_SIDRA, BRUTOS / "sidra_9923_urbana.json")))[1:])
    u = u.pivot_table(index="D1C", columns="D4N", values="V", aggfunc="first").replace("-", "0").astype(float)
    return (u["Urbana"] / (u["Urbana"] + u["Rural"])).rename("taxa_urbanizacao")


def regic():
    r = pd.read_excel(baixar(URL_REGIC, BRUTOS / Path(URL_REGIC).name))
    r["codmun"] = r["codmun"].astype(str)
    nivel = r.set_index("codmun")["Hierarquia 3"].astype(str).str[0].astype(int)   # 1 (metrópole) a 5 (centro local)
    return nivel.rename("regic_nivel")


def deter():
    arq = BRUTOS / "deter_2021_23.csv"
    if not arq.exists():
        partes = []
        for a in ANOS:
            for ini, fim in (("01-01", "06-30"), ("07-01", "12-31")):
                tmp = baixar(URL_DETER.format(ini=f"{a}-{ini}", fim=f"{a}-{fim}"), BRUTOS / f"deter_{a}_{ini}.csv")
                partes.append(pd.read_csv(tmp)); tmp.unlink()
        pd.concat(partes).to_csv(arq, index=False)
    x = pd.read_csv(arq, dtype={"mun_geocod": str})
    desm = x[x["classname"].str.startswith(("DESMATAMENTO", "CS_"))].groupby("mun_geocod")["areamunkm"].sum()
    gar = x[x["classname"] == "MINERACAO"].groupby("mun_geocod")["areamunkm"].agg(["size", "sum"])
    return pd.DataFrame({"deter_desmat_km2": desm, "deter_mineracao_alertas": gar["size"],
                         "deter_mineracao_km2": gar["sum"]})


def ibama():
    cols = ["COD_MUNICIPIO", "UF", "TIPO_INFRACAO", "DES_INFRACAO", "DES_AUTO_INFRACAO", "SIT_CANCELADO"]
    partes = []
    with zipfile.ZipFile(baixar(URL_AUTOS, BRUTOS / "auto_infracao_csv.zip")) as z:
        for a in ANOS:
            with z.open(f"auto_infracao_{a}.csv") as f:
                partes.append(pd.read_csv(f, sep=";", usecols=cols, dtype=str, on_bad_lines="skip"))
    ai = pd.concat(partes)
    ai = ai[ai["UF"].isin(UFS) & (ai["SIT_CANCELADO"] != "S")]
    texto = (ai["DES_AUTO_INFRACAO"].fillna("") + " " + ai["DES_INFRACAO"].fillna("")).str.lower()
    ai["garimpo"] = texto.str.contains(PADRAO_GARIMPO)
    ai["flora"] = ai["TIPO_INFRACAO"].str.lower().str.contains("flora", na=False)
    autos = ai.groupby("COD_MUNICIPIO").agg(ibama_autos=("UF", "size"), ibama_autos_garimpo=("garimpo", "sum"),
                                            ibama_autos_flora=("flora", "sum"))
    t = pd.read_csv(baixar(URL_TAD, BRUTOS / "termo_destruicao_inutilizacao.csv"), sep=";", dtype=str,
                    encoding="utf-8-sig", usecols=["DAT_TAD", "COD_MUNICIPIO", "SIG_UF", "SIT_CANCELADO"],
                    on_bad_lines="skip")
    t = t[t["SIG_UF"].isin(UFS) & t["DAT_TAD"].str[:4].isin(ANOS) & (t["SIT_CANCELADO"] != "S")]
    return autos.join(t.groupby("COD_MUNICIPIO").size().rename("ibama_termos_destruicao"), how="outer")


def montar():
    cods = carregar_base()["cod_ibge"]
    t = pd.DataFrame(index=pd.Index(cods, name="cod_ibge"))
    for parte in (faixa_de_fronteira(), vizinhos(), urbanizacao(), regic(), deter(), ibama()):
        t = t.join(parte)
    contagens = [c for c in t.columns if c.startswith(("faixa", "toca", "deter_", "ibama_"))]
    t[contagens] = t[contagens].fillna(0)
    t.to_csv(SAIDA)
    return t


if __name__ == "__main__":
    t = montar()
    print(t.shape, "->", SAIDA.relative_to(PASTA))
    print(t.drop(columns="vizinhos").describe().T[["count", "mean", "max"]].round(2))
