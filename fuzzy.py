"""
fuzzy.py — Sistema de inferência fuzzy Mamdani (scikit-fuzzy) para facções.

Entradas:
  presenca  : P(facção no município), média da rede bayesiana (Etapa 5) e do Naive Bayes + EM (Etapa 4), em [0, 1]
  tendencia : variação relativa dos homicídios de 2020–21 para 2022–23, limitada a [-1, 2]
              (-1 = caiu 100%, 0 = estável, +1 = dobrou)
Saída:
  prioridade: prioridade de monitoramento / inteligência policial, em [0, 100]
"""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def criar_sistema():
    presenca = ctrl.Antecedent(np.arange(0, 1.001, 0.001), "presenca")
    tendencia = ctrl.Antecedent(np.arange(-1, 2.001, 0.001), "tendencia")
    prioridade = ctrl.Consequent(np.arange(0, 101, 1), "prioridade")

    # Taxa-base de facção na região ~32%: "baixa" e "alta" giram em torno desse valor.
    presenca["baixa"] = fuzz.trimf(presenca.universe, [0.0, 0.0, 0.35])
    presenca["media"] = fuzz.trimf(presenca.universe, [0.15, 0.40, 0.65])
    presenca["alta"] = fuzz.trimf(presenca.universe, [0.45, 1.0, 1.0])

    tendencia["queda"] = fuzz.trimf(tendencia.universe, [-1, -1, 0])
    tendencia["estavel"] = fuzz.trimf(tendencia.universe, [-0.5, 0, 0.5])
    tendencia["alta"] = fuzz.trimf(tendencia.universe, [0, 2, 2])

    prioridade["baixa"] = fuzz.trimf(prioridade.universe, [0, 0, 50])
    prioridade["media"] = fuzz.trimf(prioridade.universe, [25, 50, 75])
    prioridade["alta"] = fuzz.trimf(prioridade.universe, [50, 100, 100])

    regras = [
        # R1: presença alta E (homicídios subindo OU estáveis) -> prioridade alta
        ctrl.Rule(presenca["alta"] & (tendencia["alta"] | tendencia["estavel"]), prioridade["alta"]),
        # R2: presença alta E homicídios em queda -> prioridade média (possível domínio consolidado)
        ctrl.Rule(presenca["alta"] & tendencia["queda"], prioridade["media"]),
        # R3: presença média E homicídios subindo -> prioridade alta (possível expansão)
        ctrl.Rule(presenca["media"] & tendencia["alta"], prioridade["alta"]),
        # R4: presença média E (estável OU queda) -> prioridade média
        ctrl.Rule(presenca["media"] & (tendencia["estavel"] | tendencia["queda"]), prioridade["media"]),
        # R5: presença baixa -> prioridade baixa
        ctrl.Rule(presenca["baixa"], prioridade["baixa"]),
    ]
    return ctrl.ControlSystem(regras), (presenca, tendencia, prioridade)


def avaliar(sistema, presenca_valor, tendencia_valor):
    sim = ctrl.ControlSystemSimulation(sistema)
    sim.input["presenca"] = float(np.clip(presenca_valor, 0, 1))
    sim.input["tendencia"] = float(np.clip(tendencia_valor, -1, 2))
    sim.compute()
    return float(sim.output["prioridade"])


def rotulo(prioridade):
    if prioridade < 40:
        return "baixa"
    if prioridade < 60:
        return "média"
    return "alta"
