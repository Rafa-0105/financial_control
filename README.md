# Controle Financeiro API

API robusta de controle financeiro desenvolvida com **FastAPI**, utilizando **MySQL** para persistência de dados. O sistema permite o gerenciamento de despesas mensais, cálculo automático de totais anuais e gerenciamento de usuários com autenticação segura.

## 🚀 Tecnologias Utilizadas

- **Python 3.x**
- **FastAPI**: Framwork web moderno e rápido.
- **MySQL**: Banco de dados relacional.
- **PyMySQL**: Driver para conexão com MySQL.
- **Pydantic**: Para validação de dados e schemas.
- **Bcrypt**: Para hashing seguro de senhas.
- **Uvicorn**: Servidor ASGI para rodar a aplicação.

## 📁 Estrutura do Projeto

```text
├── database/            # Conexão e operações com banco de dados
│   └── connection_db.py # Lógica de persistência e funções SQL
├── models/              # Schemas Pydantic para validação
│   ├── schemas.py       # Schemas de despesas
│   └── user_schemas.py  # Schemas de usuários
├── routes/              # Definição das rotas (GET, POST, PUT, DELETE)
│   ├── get/
│   ├── post/
│   ├── put/
│   └── delete/
├── main.py              # Ponto de entrada da aplicação
├── .env                 # Variáveis de ambiente (DB_HOST, DB_USER, etc.)
└── verify_*.py          # Scripts de teste e verificação
```

## ⚙️ Configuração e Instalação

### 1. Requisitos Prévios
- MySQL Server rodando.
- Python instalado.

### 2. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
DB_HOST=seu_host
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=finacias
DB_CHARSET=utf8mb4
```

### 3. Instalação
```bash
pip install -r requirements.txt
```

### 4. Execução
```bash
python main.py
```
A API estará disponível em `http://localhost:8000`. A documentação interativa (Swagger) pode ser acessada em `/docs`.

---

## 🔐 Autenticação e Usuários

### Criar Usuário
`POST /users`
- **Body**: `{"username": "nome", "email": "user@email.com", "password": "123"}`
- **Resposta**: Dados do usuário criado (sem a senha).

### Login
`POST /login`
- **Body**: `{"email": "user@email.com", "password": "123"}`
- **Resposta**: Mensagem de sucesso e ID do usuário.

---

## 📊 Endpoints de Despesas

Todas as rotas de despesa utilizam o prefixo `/despesas`.

### Listar Todas as Despesas
`GET /despesas`
- Retorna uma lista de todas as despesas no formato aninhado.

### Buscar Despesa por ID
`GET /despesas/{id}`

### Criar Nova Despesa
`POST /despesas`
- **Body**:
  ```json
  {
    "despesa": "Aluguel",
    "janeiro": 1200.00,
    "fevereiro": 1200.00,
    ...
  }
  ```
- **Nota**: O sistema calcula automaticamente o total anual. Aceita valores em string (ex: "R$ 1.200,50") ou float.

### Atualizar Despesa
`PUT /despesas/{id}`
- **Body**: Envie apenas os campos que deseja atualizar. O total anual será recalculado.

### Deletar Despesa
`DELETE /despesas/{id}`

---

## 🧠 Lógica Interna e Funções Chave

### `calculate_total` (database/connection_db.py)
Esta função é o coração do cálculo financeiro. Ela:
1. Percorre todos os meses de Janeiro a Dezembro.
2. Limpa strings monetárias (remove "R$", espaços, pontos de milhar e converte vírgula em ponto).
3. Soma os valores e retorna o total arredondado para 2 casas decimais.

### `format_response_nested`
Transforma o retorno plano do banco de dados em uma estrutura organizada:
```json
{
  "id": 1,
  "despesa": "Exemplo",
  "monthly_data": { "janeiro": 100.0, ... },
  "annual_total": 1200.0
}
```

---

## ✅ Verificação e Testes

Existem scripts utilitários para garantir o funcionamento da aplicação:
- `verify_parsing.py`: Testa a lógica de limpeza e conversão de valores monetários.
- `verify_total.py`: Realiza um fluxo completo de criação e atualização via API para validar o cálculo do total.
- `verify_login.py`: Valida o fluxo de autenticação.

Para rodar (com a API ligada):
```bash
python verify_total.py
```
