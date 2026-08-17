# Modelling and Integrating Polarity, Subjectivity and Emotion of Sentiment Data in a Data Warehouse

Dissertação de Mestrado em Engenharia Informática (Universidade do Minho, 2025/2026)

**Autor:** Afonso Miguel Rodrigues Magalhães ([pg53598@alunos.uminho.pt](mailto:pg53598@alunos.uminho.pt))
**Orientação:** Prof. Orlando Manuel Oliveira Belo

---

## Sobre o projeto

Este trabalho propõe um **data warehouse dimensional sensível a sentimento**, aplicado ao domínio do turismo e hotelaria em Portugal, que integra três dimensões afetivas normalmente tratadas de forma superficial pela análise de sentimento tradicional:

- **Polaridade** (positivo / negativo / neutro)
- **Subjetividade** (opinião vs. facto)
- **Emoção** (as 8 emoções de Plutchik: alegria, confiança, medo, surpresa, tristeza, aversão, raiva, antecipação)

A generalidade dos sistemas de *business intelligence* reduz o sentimento extraído de texto a uma única pontuação de polaridade, perdendo informação analítica relevante (duas críticas negativas podem refletir raiva ou desilusão, exigindo respostas de negócio distintas). Este projeto modela essas três dimensões afetivas com o mesmo rigor aplicado a dados de negócio convencionais, dentro de um data warehouse dimensional construído segundo a metodologia de Kimball, permitindo análise histórica, comparativa e multidimensional do sentimento.

A abordagem segue uma metodologia **Design Science Research**, cobrindo desde o estado da arte até um protótipo funcional avaliado com consultas OLAP.

## Objetivos

**Objetivo geral:** desenhar e validar um data warehouse sensível a sentimento capaz de integrar polaridade, subjetividade e emoção extraídas de texto não estruturado, suportando processamento analítico mais rico e expressivo num ambiente multidimensional.

## Arquitetura da solução

O trabalho está organizado em três grandes componentes:

1. **Modelo dimensional (star schema)** — desenho conceptual e lógico do data warehouse, com 6 dimensões e 1 tabela de factos.
2. **Processo de ETL** — transforma texto de críticas não estruturado em medidas de sentimento estruturadas ao nível do aspeto.
3. **Protótipo** — implementação funcional em Python + SQLite, populada com um dataset sintético e validada através de consultas analíticas.

### Modelo dimensional

| Dimensão | Descrição |
|---|---|
| `D_Date` | Calendário, com hierarquias Ano→Trimestre→Mês→Dia e Ano→Estação→Mês→Dia |
| `D_Location` | Localização do serviço (região, distrito, município) |
| `D_Service` | Serviço avaliado (alojamento, restauração, atração turística); **SCD Tipo 2** para acompanhar alterações de categoria de preço/estrelas ao longo do tempo |
| `D_Aspect` | Taxonomia de aspetos avaliados numa crítica (ex.: limpeza, atendimento) |
| `D_Travel_Segment` | Perfil do viajante (nacionalidade, faixa etária, género, tipo de viagem, propósito) |
| `D_Review` | Crítica original, incluindo deteção de edições (`review_group_id`, `is_edit`) |
| `D_Platform` | Plataforma de origem da crítica (ex.: TripAdvisor, redes sociais) |

**Tabela de factos:** `F_Aspect_Sentiment_Observation`, ao grão de *uma observação de sentimento por aspeto, por crítica*, com as medidas:

`polarity_score`, `subjectivity_score`, `sentiment_strength`, `model_confidence` e as 8 medidas de emoção (`joy_score`, `trust_score`, `fear_score`, `surprise_score`, `sadness_score`, `disgust_score`, `anger_score`, `anticipation_score`).

### Processo de ETL

| Ferramenta | Papel |
|---|---|
| **VADER** | Deriva a polaridade, ao nível da frase associada a um aspeto |
| **TextBlob** | Deriva a subjetividade (opinião vs. facto) |
| **NRC Emotion Lexicon** | Deriva as 8 emoções de Plutchik |

O ETL divide cada crítica em frases, identifica o aspeto de cada frase através de um dicionário de palavras-chave e deriva as medidas de sentimento através das três bibliotecas acima — tudo integrado diretamente na fase de transformação, sem passos intermédios de exportação/importação.

## Protótipo

- **Linguagem:** Python
- **Base de dados:** SQLite (ficheiro único, portátil, sem servidor)
- **Dataset sintético:** 80 serviços (40 alojamentos, 24 restauração/bares, 16 pontos turísticos) em 22 municípios, cobrindo as 7 regiões de Portugal (incluindo os Açores); 5 plataformas; 1.000 críticas (900 threads distintas, 100 com uma edição), entre 2022 e 2025
- Perfis de sentimento distintos por serviço (positivo / misto / negativo) para garantir contraste real na análise
- 3 serviços com alteração real de atributo ao longo do tempo (para exercitar a lógica SCD Tipo 2)
- Geração determinística (seed fixa), permitindo reproduzir o dataset de forma idêntica

### Pipeline (7 etapas, execução única via `run_pipeline.py`)

| Etapa | Ficheiro(s) | Função |
|---|---|---|
| 1 — Criação do esquema | `schema.sql`, `raw_schema.sql` | Cria as 8 tabelas do DW e as 2 tabelas da camada raw |
| 2 — Dimensões independentes | `populate_d_date.py`, `populate_d_aspect.py`, `populate_d_location.py`, `municipality_data.py` | Popula `D_Date`, `D_Aspect`, `D_Location` |
| 3 — Geração de críticas em bruto | `generate_raw_reviews.py`, `service_data.py`, `platform_data.py`, `fragment_library.py` | Gera o dataset sintético descrito acima |
| 4 — Dicionário de palavras-chave | `populate_keyword_dict.py` | Popula o dicionário usado na identificação de aspetos |
| 5 — Transformação | `transform.py` | Divide as críticas em frases, identifica aspetos e deriva as medidas de sentimento (tabela intermédia `TRANSFORMED_OBSERVATIONS`) |
| 6 — Dimensões dependentes | `load_d_platform.py`, `load_d_service.py`, `load_d_travel_segment.py`, `load_d_review.py` | Popula `D_Platform`, `D_Service`, `D_Travel_Segment`, `D_Review` |
| 7 — Carga da tabela de factos | `load_fact_table.py` | Resolve as chaves das 5 dimensões relevantes e popula `F_Aspect_Sentiment_Observation` |

## Avaliação

O protótipo é avaliado através de consultas OLAP organizadas em várias frentes analíticas: análise estratégica e comparativa, análise ao nível do aspeto e operacional, análise afetiva e de segmentação, e comparação face a abordagens de sentimento mais simples (ex.: apenas classificação de estrelas/polaridade), validando a mais-valia de integrar subjetividade e emoção no modelo.

## Estrutura do repositório (sugerida)

```
.
├── sql/
│   ├── schema.sql              # Esquema do DW (8 tabelas)
│   └── raw_schema.sql          # Esquema da camada raw (2 tabelas)
├── src/
│   ├── run_pipeline.py         # Orquestração das 7 etapas
│   ├── populate_d_date.py
│   ├── populate_d_aspect.py
│   ├── populate_d_location.py
│   ├── municipality_data.py
│   ├── generate_raw_reviews.py
│   ├── service_data.py
│   ├── platform_data.py
│   ├── fragment_library.py
│   ├── populate_keyword_dict.py
│   ├── transform.py
│   ├── load_d_platform.py
│   ├── load_d_service.py
│   ├── load_d_travel_segment.py
│   ├── load_d_review.py
│   └── load_fact_table.py
├── docs/                       # Relatório e figuras da dissertação
└── README.md
```

## Como executar

```bash
# 1. Instalar dependências
pip install vaderSentiment textblob nltk

# 2. Correr o pipeline completo (schema → dimensões → ETL → factos)
python src/run_pipeline.py
```

No final, obtém-se um ficheiro SQLite único e portátil com o data warehouse totalmente populado, pronto para ser explorado com ferramentas OLAP/SQL.

## Palavras-chave

Sentiment Analysis · Data Warehousing · Polarity · Subjectivity · Emotion · Business Intelligence

## Bibliografia principal

- Kimball, R. & Ross, M. (2013). *The Data Warehouse Toolkit*.
- Liu, B. (2012). *Sentiment Analysis and Opinion Mining*.
- Hutto, C. & Gilbert, E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.
- Mohammad, S. & Turney, P. (2013). NRC Emotion Lexicon.
