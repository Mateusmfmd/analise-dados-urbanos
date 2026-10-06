# Análise de dados urbanos (projeto reproduzível)

Projeto didático, sem dependências externas, para demonstrar um fluxo mínimo de análise de dados urbanos: leitura de CSV, agregação por zona, exportação de resumo, gráficos SVG e relatório HTML.

> **Atenção sobre os dados:** `data/amostra_dados_urbanos.csv` é uma **amostra sintética e pequena**, incluída apenas para que o projeto rode offline. Ela não representa nenhuma cidade, período ou fonte oficial. Os números do relatório são métricas calculadas nessa amostra e não devem ser tratados como conclusões sobre dados reais.

## Requisitos

- Python 3.10 ou superior;
- biblioteca padrão do Python apenas;
- nenhum download ou acesso à internet é necessário para executar a análise ou a CI.

## Execução local

Na raiz do projeto:

```bash
python3 scripts/run_analysis.py
```

O comando lê o CSV de amostra e cria:

- `outputs/summary.csv`: agregados por zona;
- `outputs/grafico_residentes.svg`: residentes totais por zona;
- `outputs/grafico_transito.svg`: índice médio de trânsito por zona;
- `outputs/relatorio.html`: relatório navegável com tabelas, gráficos e avisos de escopo.

Para escolher outros caminhos sem alterar o código:

```bash
python3 scripts/run_analysis.py \
  --input data/amostra_dados_urbanos.csv \
  --output-dir outputs \
  --report outputs/relatorio.html
```

Abra `outputs/relatorio.html` em um navegador. Os gráficos são SVGs locais, portanto não dependem de CDN.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

A integração contínua em `.github/workflows/ci.yml` executa os testes e refaz a análise em um runner limpo. O workflow não instala pacotes nem baixa dados.

## Estrutura

```text
.
├── data/
│   ├── README.md
│   └── amostra_dados_urbanos.csv
├── metodologia.md
├── limitacoes.md
├── outputs/                 # artefatos gerados pelo script
├── scripts/run_analysis.py  # entrada de linha de comando
├── src/urban_analysis/      # funções de leitura, agregação e renderização
├── tests/
├── LICENSE
└── .github/workflows/ci.yml
```

## Próximos passos para dados reais

Substitua o arquivo de entrada por um CSV documentado, mantenha o esquema exigido pelo script e registre a fonte, a licença, a data de extração e as transformações aplicadas. Antes de interpretar resultados, faça validação de qualidade, tratamento de dados faltantes e análise de representatividade. Este repositório não faz essas validações automaticamente.
