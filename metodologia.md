# Metodologia

## Objetivo

Demonstrar um pipeline determinístico e offline para transformar um CSV pequeno em agregados por zona, dois gráficos SVG e um relatório HTML. O objetivo é técnico e didático; não é produzir um diagnóstico urbano.

## Entrada

O script espera as colunas:

- `zone` e `month` como identificadores;
- `residents`, `green_area_m2`, `traffic_index` e `occupancy_rate` como variáveis numéricas;
- `is_sample` e `source` para rastreabilidade do caráter de amostra.

A leitura é feita com `csv.DictReader`, sem bibliotecas de terceiros. Números inválidos ou colunas ausentes interrompem a execução com erro explícito.

## Transformações

1. Ler todas as linhas do CSV e converter os campos numéricos.
2. Agrupar por `zone`.
3. Calcular, para cada zona:
   - total de `residents`;
   - média de `green_area_m2`;
   - média de `traffic_index`;
   - média de `occupancy_rate`;
   - número de registros.
4. Ordenar zonas alfabeticamente para tornar a saída estável entre execuções.
5. Gravar o resumo em CSV.
6. Renderizar gráficos de barras simples em SVG, com valores desenhados no próprio arquivo.
7. Montar um HTML estático com aviso de escopo, tabela e links para os artefatos.

## Reprodutibilidade

A análise não usa relógio, aleatoriedade, rede ou estado externo. Com o mesmo arquivo de entrada e as mesmas opções, a saída textual e os SVGs devem ser iguais. A CI executa o mesmo comando contra o arquivo versionado.

## Interpretação

Os agregados são descritivos da entrada fornecida. Como a entrada do repositório é sintética, qualquer padrão visual deve ser lido somente como comportamento do exemplo de software. Uma análise real exigiria fonte verificável, definição das métricas, avaliação de qualidade e desenho estatístico apropriado.
