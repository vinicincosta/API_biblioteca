# API Biblioteca

API REST do sistema de biblioteca digital. É o backend compartilhado pelo [app mobile](https://github.com/vinicincosta/app_biblioteca) e pela [interface web](https://github.com/vinicincosta/Biblioteca_Web): cadastro de livros e usuários, controle de empréstimos com prazo de devolução e dados para relatórios.

## Funcionalidades

- Login com JWT; o token carrega o id e o papel do usuário (`admin` ou `usuario`)
- Cadastro de usuários com senha em hash e validação de CPF (11 dígitos numéricos)
- CRUD de livros, incluindo o campo `leitura` (texto lido dentro do app)
- Empréstimos com prazo de 20 dias, bloqueio de livro já emprestado, devolução e histórico por usuário
- Listagens de livros disponíveis e de empréstimos ativos
- Endpoints de dados para gráficos: livros mais emprestados e usuários que mais emprestam

## Tecnologias

- Python 3 e Flask 3.1
- SQLAlchemy 2.0 (ORM) com SQLite
- Flask-JWT-Extended (autenticação)
- Werkzeug (hash de senha) e python-dateutil (cálculo de prazos)
- `vercel.json` para deploy na Vercel

## Estrutura

```
API_biblioteca/
├── app_2.py           # rotas Flask
├── models.py          # engine, sessão e modelos SQLAlchemy
├── requirements.txt   # dependências
├── config.ini         # lido por models.py na importação
├── nome.sqlite3       # banco SQLite local
└── vercel.json        # configuração de deploy
```

## Modelo de dados

| Tabela | Campos principais |
|---|---|
| `USUARIOS` | `id_usuario`, `nome`, `email` (único), `cpf`, `endereco`, `senha_hash`, `papel`, `status_user` |
| `LIVROS` | `id_livro`, `titulo`, `autor`, `ISBN`, `resumo`, `leitura` |
| `EMPRESTIMOS` | `id`, `data_de_emprestimo`, `data_de_devolucao`, `livro_emprestado_id` → `LIVROS`, `usuario_emprestado_id` → `USUARIOS`, `status` (`Ativo` ou `Devolvido`) |

As datas são gravadas como texto no formato `dd-mm-AAAA`.

## Como rodar

```bash
git clone https://github.com/vinicincosta/API_biblioteca.git
cd API_biblioteca

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`models.py` lê o `config.ini` ao ser importado e exige a seção `[database]` com a chave `url`. Hoje o engine está fixo em SQLite (`nome.sqlite3`), então o valor não é usado; um placeholder basta:

```ini
[database]
url=postgresql://USUARIO:SENHA@HOST/BANCO
```

Para criar as tabelas em um banco vazio (o repositório já traz um `nome.sqlite3`):

```bash
python models.py
```

Para subir a API:

```bash
python app_2.py
```

A API fica em `http://localhost:5000` (modo debug, escutando em `0.0.0.0`). Para o app em um celular, use o IP da máquina na rede local no lugar de `localhost`.

## Endpoints

Todas as respostas são JSON.

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| POST | `/login` | Recebe `email` e `senha`; retorna `access_token`, `papel` e `nome` |
| POST | `/cadastro` | Recebe `nome`, `cpf`, `email`, `senha`, `endereco` e, opcionalmente, `papel` (padrão `usuario`) |

### Livros

| Método | Rota | Descrição |
|---|---|---|
| GET | `/livro` | Lista todos os livros |
| GET | `/livros_disponiveis` | Livros sem empréstimo ativo |
| GET | `/get_livro/<id>` | Busca um livro |
| POST | `/novo_livro` | Cadastra: `titulo`, `autor`, `ISBN`, `resumo`, `leitura` |
| PUT | `/editar_livro/<id>` | Edita os mesmos campos |
| DELETE | `/deletar_livro/<id>` | Remove o livro |

### Usuários

| Método | Rota | Descrição |
|---|---|---|
| GET | `/usuario` | Lista os usuários |
| GET | `/get_usuario/<id>` | Busca um usuário |
| PUT | `/editar_usuarios/<id>` | Edita `nome`, `cpf`, `email`, `endereco`, `papel`, `status_user` |
| POST | `/novo_usuario` | Em revisão; use `/cadastro` |

### Empréstimos

| Método | Rota | Descrição |
|---|---|---|
| GET | `/emprestimo` | Lista os empréstimos (veja a observação abaixo) |
| GET | `/livros_emprestados` | Empréstimos com status `Ativo` |
| POST | `/novo_emprestimo` | Recebe `livro_emprestado_id` e `usuario_emprestado_id`; devolução em 20 dias |
| PUT | `/editar_emprestimo/<id>` | Com `{"status": "Devolvido"}`, registra a devolução |
| PUT | `/devolver_emprestimo/<id>` | Em revisão; use `/editar_emprestimo/<id>` |
| GET | `/historico_emprestimos/<id_usuario>` | Empréstimos de um usuário |
| GET | `/calcular_devolucao/<dd-mm-AAAA>` | Data de devolução a partir de uma data de empréstimo |

Ao listar os empréstimos, a API marca como `Devolvido` os empréstimos ativos cuja data de devolução já passou.

### Relatórios

| Método | Rota | Descrição |
|---|---|---|
| GET | `/grafico_livros_mais_emprestados` | `{"livros": [{"titulo", "total"}]}` |
| GET | `/usuarios_que_mais_realizaram_emp` | `{"usuarios": [{"nome", "total"}]}` |

## Exemplos

Login:

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@exemplo.com", "senha": "sua-senha"}'
```

```json
{ "access_token": "...", "papel": "usuario", "nome": "..." }
```

Novo empréstimo:

```bash
curl -X POST http://localhost:5000/novo_emprestimo \
  -H "Content-Type: application/json" \
  -d '{"livro_emprestado_id": 1, "usuario_emprestado_id": 1}'
```

```json
{
  "success": "Empréstimo criado com sucesso!",
  "data_emprestimo": "14-10-2026",
  "data_devolucao": "03-11-2026",
  "prazo_maximo": 20
}
```


## Projetos relacionados

- [app_biblioteca](https://github.com/vinicincosta/app_biblioteca): app mobile em Flet
- [Biblioteca_Web](https://github.com/vinicincosta/Biblioteca_Web): interface web
