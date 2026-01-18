# Documentação Técnica: API de Controle Financeiro

Esta documentação descreve a arquitetura, as classes, as funções e os endpoints da API de Controle Financeiro.

## 1. Tecnologias Utilizadas
- **Framework Web:** FastAPI
- **Banco de Dados:** MySQL (via PyMySQL)
- **Validação de Dados:** Pydantic
- **Autenticação:** Bcrypt para hashing de senhas
- **Gestão de Ambiente:** Dotenv
- **Performance:** Functools.lru_cache para caching de cálculos

---

## 2. Estrutura do Projeto

```text
/
├── main.py                 # Ponto de entrada da aplicação
├── .env                    # Variáveis de ambiente (DB_HOST, etc)
├── requirements.txt         # Dependências do projeto
├── database/               # Camada de persistência e lógica de BD
│   ├── connection_db.py     # Conexão base e operações CRUD simples
│   └── batch_operations.py  # Operações em massa e lógica avançada
├── models/                 # Schemas Pydantic e modelos de dados
│   ├── schemas.py           # Modelos base de despesas
│   ├── excel_schemas.py     # Modelos para operações avançadas
│   └── user_schemas.py      # Modelos de usuário e login
├── routes/                 # Definição dos endpoints da API
│   ├── get/                # Consultas simples
│   ├── post/               # Criação, login e usuários
│   ├── put/                # Atualizações individuais
│   ├── delete/             # Remoção individual
│   ├── batch/              # Operações em lote (Batch)
│   ├── analytics/          # Dashboards e relatórios
│   └── excel/              # Filtros, fórmulas e histórico
└── verify_*.py             # Scripts de teste e verificação
```

---

## 3. Modelos de Dados (Schemas)

### models/schemas.py
- `DespesaBase`: Define a estrutura comum (Nome da despesa + 12 meses).
- `DespesaCreate`: Modelo para criação de novas despesas.
- `DespesaUpdate`: Modelo para atualização parcial.
- `DespesaMonthlyData`: Estrutura aninhada para os valores mensais.
- `DespesaResponseNested`: Estrutura de resposta padronizada com dados aninhados e total anual.

### models/excel_schemas.py
- `FormulaType`: Enum (multiply, divide, add, subtract, percentage).
- `MonthEnum`: Enum com os 12 meses do ano.
- `UpdateItem`: Item individual para atualização em lote.
- `BatchUpdateRequest`: Lista de `UpdateItem`.
- `FormulaRequest`: Dados para aplicação de fórmulas em células.
- `FilterParams`: Parâmetros de busca avançada.
- `CellHistoryResponse`: Estrutura dos logs de auditoria.

---

## 4. Lógica de Banco de Dados

### database/connection_db.py
- `get_connection()`: Gerencia a conexão com o MySQL.
- `calculate_total(data)`: Soma os valores de Janeiro a Dezembro para gerar o `total`.
- `normalize_keys(data)`: Padroniza chaves para minúsculo e garante o cálculo do total.
- `format_response_nested(data)`: Converte o formato flat do BD para o formato aninhado da API.
- `init_db()`: Inicializa as tabelas `users` e `despesa_history`.

### database/batch_operations.py
- `log_change(...)`: Registra alterações de células para auditoria.
- `batch_update_despessas(...)`: Atualiza múltiplas despesas em uma única transação.
- `batch_create_despessas(...)`: Insere múltiplas despesas simultaneamente.
- `apply_excel_formula(...)`: Executa operações matemáticas em uma célula e atualiza o total.
- `revert_cell_value(...)`: Reverte uma célula para um valor anterior (Undo).
- `get_monthly_analytics()`: Gera a soma total de gastos por mês (Cacheado).
- `detect_anomalies(...)`: Identifica meses onde o gasto foge do padrão médio.

---

## 5. Endpoints da API (Resumo)

### Gerenciamento de Despesas
- **GET** `/despesas`: Lista todas as despesas.
- **POST** `/despesas`: Cria uma nova despesa.
- **PUT** `/despesas/{id}`: Atualiza uma despesa.
- **DELETE** `/despesas/{id}`: Deleta uma despesa.

### Operações em Lote (Batch)
- **POST** `/despesas/batch/update`: Atualiza várias células/linhas de uma vez.
- **POST** `/despesas/batch/create`: Cria várias despesas via array JSON.
- **POST** `/despesas/batch/delete`: Remove múltiplas despesas por IDs.

### Inteligência e Analytics
- **GET** `/despesas/analytics/monthly`: Total mensal acumulado.
- **GET** `/despesas/analytics/top`: Top N maiores gastos anuais.
- **GET** `/despesas/analytics/trends`: Identifica o mês mais caro e o mais barato.
- **GET** `/despesas/calculate/sum`: Soma valores de uma coluna específica.

### Excel & Auditoria
- **POST** `/despesas/formulas/apply`: Aplica cálculos (ex: +10%) em uma célula.
- **GET** `/despesas/{id}/history`: Mostra quem alterou o quê e quando.
- **POST** `/despesas/{id}/revert`: Restaura um valor antigo de uma célula.
- **POST** `/despesas/import/csv`: Importa dados de planilhas.
- **GET** `/despesas/export/csv`: Exporta todos os dados em formato CSV.

### Busca e Filtros
- **GET** `/despesas/filter`: Filtra por range de valores, mês específico ou nome similar.
- **GET** `/despesas/sort`: Ordena por qualquer coluna (asc/desc).

---

## 6. Segurança e Performance
- **Senhas:** Armazenadas com hash `bcrypt`.
- **Transações:** Operações batch usam `rollback` em caso de erro para manter integridade.
- **Cache:** Resultados de análise e somas são armazenados em memória (`lru_cache`) e invalidados automaticamente quando os dados mudam.
