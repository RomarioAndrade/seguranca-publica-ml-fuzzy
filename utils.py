"""
utils.py — carga e preparação dos dados: facções na Amazônia Legal.

Pergunta:
    "O município da Amazônia Legal tem presença de facção criminosa (2024),
     dado o seu porte e o padrão de violência registrado entre 2021 e 2023?
     E o modelo antecipa quais municípios passaram a ter facção em 2025?"

Fontes:
  * Rótulos: Cartografias da Violência na Amazônia (Instituto Mãe Crioula / FBSP)
      - 3ª edição: presença de facções por município em 2024 (Tabelas 13–21)
      - 4ª edição: presença em 2025 (quadros por estado, extraídos do PDF)
  * Atributos: SINESP VDE / MJSP, 2020–2023, por município.
  * População: IBGE (Censo 2022 e estimativas).

Unidade de análise: 808 municípios dos 9 estados da Amazônia Legal
(o Maranhão entra inteiro; só 181 dos seus 217 municípios pertencem à região).
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
PASTA = Path(__file__).resolve().parent
ARQ_BASE = PASTA / "dados" / "amazonia_legal_faccoes_2024_2025_vde_pop.csv"

# UFs da Amazônia Legal que fazem fronteira com outro país
UF_FRONTEIRA = {"AC", "AM", "AP", "RR", "RO", "PA", "MT"}

ATRIBUTOS_CAT = ["PORTE", "TXH", "TXT", "ESC", "LATRO", "UF"]
DESCRICAO = {
    "PORTE": "População (Censo 2022): 0=pequeno (<10 mil), 1=médio (10–50 mil), 2=grande (50 mil+)",
    "TXH": "Taxa anual de homicídio doloso 2021–23 por 100 mil hab., em tercis (0=baixa, 1=média, 2=alta)",
    "TXT": "Taxa anual de tentativas de homicídio 2021–23 por 100 mil hab., em tercis",
    "ESC": "Teve morte a esclarecer em 2021–23 (0/1)",
    "LATRO": "Teve latrocínio em 2021–23 (0/1)",
    "UF": "Unidade da Federação (9 estados da Amazônia Legal)",
    "FRONT": "A UF faz fronteira com outro país (0/1) — usada na rede bayesiana",
    "ALVO": "Presença de facção em 2024 segundo o Cartografias, 3ª ed. (0/1)",
    "REGIME": "2024: 0=sem registro, 1=uma facção (domínio), 2=duas ou mais (disputa)",
    "ALVO_2025": "Presença de facção em 2025 segundo o Cartografias, 4ª ed. (0/1)",
    "ENTRADA_2025": "Sem facção em 2024 e com facção em 2025 (0/1); vazio para quem já tinha",
}


def carregar_base(caminho=ARQ_BASE) -> pd.DataFrame:
    return pd.read_csv(caminho, dtype={"cod_ibge": str})


def montar_tabela(base: pd.DataFrame | None = None) -> pd.DataFrame:
    """Uma linha por município com atributos categóricos, numéricos e os alvos."""
    w = carregar_base() if base is None else base.copy()
    d = w.copy()
    d["PORTE"] = pd.cut(w["pop_2022"], [0, 10_000, 50_000, np.inf], labels=[0, 1, 2]).astype(int)
    d["TXH"] = pd.qcut(w["taxa_homicidio_2021_23"].rank(method="first"), 3, labels=[0, 1, 2]).astype(int)
    d["TXT"] = pd.qcut(w["taxa_tent_homicidio_2021_23"].rank(method="first"), 3, labels=[0, 1, 2]).astype(int)
    d["ESC"] = (w["mortes_esclarecer_total_2021_23"] > 0).astype(int)
    d["LATRO"] = (w["latrocinio_total_2021_23"] > 0).astype(int)
    d["UF"] = w["uf"]
    d["FRONT"] = w["uf"].isin(UF_FRONTEIRA).astype(int)
    antes = w["homicidio_2020"] + w["homicidio_2021"]
    depois = w["homicidio_2022"] + w["homicidio_2023"]
    d["variacao_hom"] = (depois - antes) / (antes + 1)          # variação relativa suavizada
    d["ALVO"] = w["faccao_2024"].astype(int)
    d["REGIME"] = w["sit24"].astype(int)
    d["ALVO_2025"] = w["faccao_2025"].astype(int)
    d["REGIME_2025"] = w["sit25"].astype(int)
    d["ENTRADA_2025"] = np.where(d["ALVO"] == 0, d["ALVO_2025"], np.nan)
    return d


def juntar_externas(d: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as variáveis de outras bases (montar_bases_externas.py) e os indicadores de garimpo."""
    ext = pd.read_csv(PASTA / "dados" / "variaveis_externas_municipio.csv", dtype={"cod_ibge": str})
    d = d.merge(ext, on="cod_ibge", how="left")
    d["GARIMPO_IBAMA"] = (d["ibama_autos_garimpo"] > 0).astype(int)    # auto de infração por garimpo/mineração
    d["GARIMPO_INPE"] = (d["deter_mineracao_alertas"] > 0).astype(int)  # alerta DETER da classe mineração
    return d


TAXAS_TERCIL = {"TXH": "taxa_homicidio_2021_23", "TXT": "taxa_tent_homicidio_2021_23"}


def tercis_do_treino(d: pd.DataFrame, X: pd.DataFrame, tr) -> pd.DataFrame:
    """Refaz TXH e TXT de X com os cortes dos tercis calculados só nas linhas de treino.

    Os tercis de montar_tabela usam a base inteira; na validação cruzada isso deixa o
    teste influenciar os cortes. Aqui o teste recebe os cortes do treino.
    tr: posições (como as de StratifiedKFold.split) das linhas de treino em d.
    """
    X = X.copy()
    for nome, col in TAXAS_TERCIL.items():
        if nome in X:
            cortes = np.quantile(d[col].values[tr], [1 / 3, 2 / 3])
            X[nome] = np.digitize(d[col].values, cortes, right=True)
    return X


def atributos_numericos_log(d: pd.DataFrame, anos=(2020, 2021, 2022)) -> pd.DataFrame:
    """log(população) + contagens anuais em log(1+x) para as Etapas 2 e 4."""
    eventos = ["homicidio", "tent_homicidio", "mortes_esclarecer", "latrocinio", "mandados"]
    X = pd.DataFrame({"log_populacao": np.log(d["pop_2022"])})
    for e in eventos:
        for a in anos:
            X[f"log_{e}_{a}"] = np.log1p(d[f"{e}_{a}"])
    return X


if __name__ == "__main__":
    t = montar_tabela()
    print(t.shape)
    print("Com facção em 2024:", round(t["ALVO"].mean(), 4), "| em 2025:", round(t["ALVO_2025"].mean(), 4))
    print("Entraram em 2025 (entre os sem facção em 2024):", round(t["ENTRADA_2025"].mean(), 4))
