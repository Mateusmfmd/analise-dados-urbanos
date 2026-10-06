# Dados de entrada

`amostra_dados_urbanos.csv` é uma **amostra sintética, não oficial e não observacional**, criada para testes e demonstração local. Não foi baixada de uma prefeitura, instituto de estatística ou serviço externo; por isso, não permite descrever uma cidade real nem sustentar inferência.

Cada linha representa uma combinação ilustrativa de zona e mês. A coluna `is_sample` está preenchida com `true` e `source` com `amostra_sintetica` para tornar o escopo explícito também no próprio arquivo.

## Esquema

| Coluna | Tipo | Descrição |
|---|---|---|
| `zone` | texto | Nome ilustrativo da zona |
| `month` | `YYYY-MM` | Período ilustrativo |
| `residents` | inteiro | Contagem ilustrativa de residentes |
| `green_area_m2` | decimal | Área verde ilustrativa em m² |
| `traffic_index` | decimal | Índice ilustrativo sem unidade; não é uma escala oficial |
| `occupancy_rate` | decimal | Taxa ilustrativa entre 0 e 1 |
| `is_sample` | booleano | Marcador de amostra |
| `source` | texto | Identificação da origem sintética |
