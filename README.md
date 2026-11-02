# Seguranca-publica-ml-fuzzy
Trabalho Integrado de Fundamentos de IA

### Base de Dados
As bases de dados utilizada neste atividade estão armazenados na pasta [Datasets](https://github.com/RomarioAndrade/seguranca-publica-ml-fuzzy/tree/493f99e27d45b2a411968d59d4ab6c73e75bbb52/Datasets)

### Domínio Escolhido (A definir)
- Trafico de drogras
- Feminicídio
- Milicias e Facções (variaveis ocultas)
- Outros

### Datasets em Avaliação
Lista de datasets a serem analizados se serão cruzados a outros 
datasets
- https://www.rj.gov.br/isp/sites/default/files/2025-12/Plano%20de%20Dados%20Abertos%20ISP.pdf
- https://cran.r-project.org/web/packages/ispdata/readme/README.html
- https://sol.sbc.org.br/index.php/dsw/article/view/25504
- https://www.ba.gov.br/ssp/sites/site-ssp/files/2025-12/Dicion%C3%A1rio%20de%20dados_SSP-BA_23dez25_VI_PUBLICA%C3%87%C3%83O.pdf
- https://www.ba.gov.br/ssp/sites/site-ssp/files/2025-12/Dicion%C3%A1rio%20de%20dados_SSP-BA_23dez25_VI_PUBLICA%C3%87%C3%83O.pdf
- https://cloud.r-project.org/web/packages/healthbR/vignettes/datasus-modules.html
- https://www.gov.br/saude/pt-br/acesso-a-informacao/sic/dados-em-transparencia-ativa/svsa/mortalidade
- https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf
- https://repositorio.ipea.gov.br/bitstream/11058/14031/5/AtlasViolencia2024_Retrato_dos_municipios_brasileros.pdf
- https://forumseguranca.org.br/publicacoes/atlas-da-violencia/
- https://static.poder360.com.br/uploads/2026/07/anuario-seguranca-publica-23jul26.pdf
- https://forumseguranca.org.br/publicacoes/anuario-brasileiro-de-seguranca-publica/
- https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/dados-nacionais-1/base-de-dados-e-notas-metodologicas-dos-gestores-estaduais-sinesp-vde-2022-e-2023
- https://soudapaz.org/wp-content/uploads/2023/09/Guia-Seguranca-Publica-em-dados.pdf


## 1. SINESP VDE — Ministério da Justiça
Página oficial (arquivos + notas metodológicas por estado):
https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/dados-nacionais-1/base-de-dados-e-notas-metodologicas-dos-gestores-estaduais-sinesp-vde-2022-e-2023
Arquivos por ano (.xlsx, ~20-30 MB cada):
- 2024  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2024.xlsx/@@download/file
- 2019  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2019.xlsx/@@download/file
- 2020  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2020.xlsx/@@download/file
- 2021  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2021.xlsx/@@download/file
- 2022  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2022.xlsx/@@download/file
- 2023  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2023.xlsx/@@download/file
- 2026  https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-2026.xlsx/@@download/file   (parcial: jan-ago)

## 2. IBGE — população por ano + mulheres (Censo 2022):
- https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2020/POP2020_20220905.xls
- https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/POP2021_20240624.xls
- https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Populacao_e_domicilios_Primeiros_resultados/Resultados_da_2a_apuracao_20231027/CD2022_Populacao_Coletada_Imputada_e_Total_Municipio_e_UF_20231222.xlsx
- https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2024/POP2024_20241230.xls
- https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2025/POP2025_20260828.xls
- https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2026/estimativa_dou_2026.xlsx
- https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Municipio_csv/Agregados_por_municipios_demografia_BR.zip
- https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx

## 3. CARTOGRAFIAS DA VIOLÊNCIA NA AMAZÔNIA — FBSP / Instituto Mãe Crioula

- 3ª edição (dados de 2024, 260 municípios): tabelas_cartografias-violencia-amazonia-3ed.xlsx
            -> Tabelas 13 a 21 = facções por município
 
- 4ª edição (dados de 2025, 344 municípios) — necessária para estudar EXPANSÃO 2024 -> 2025
            Relatório completo (PDF):
            https://forumseguranca.org.br/wp-content/uploads/2025/11/cartografias-violencia-amazonia-2025.pdf
            Sumário executivo (PDF):
            https://forumseguranca.org.br/wp-content/uploads/2025/11/cartografias-violencia-amazonia-2025-sumario-executivo.pdf
            Página especial (procurar o arquivo "tabelas ... 4ed.xlsx"):
            https://forumseguranca.org.br/especial-cop30/
            
 
## 3. IBGE — população, códigos e recorte da Amazônia Legal