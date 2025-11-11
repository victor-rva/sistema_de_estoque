```markdown
# 🧮 Controle de Estoque com Concorrência

Este projeto implementa uma **API RESTful em Flask (Python)** com banco **MySQL**,  
acompanhada de um **frontend em HTML, CSS e JavaScript puro**, simulando um **painel real de controle de estoque**.

O foco é demonstrar boas práticas de arquitetura backend, **controle de concorrência em transações** e integração entre backend e frontend sem frameworks.

---

## Estrutura do Projeto

```

inventory-case/
│
├─ backend/
│  ├─ app.py                      # Inicializa o Flask e registra os blueprints
│  ├─ db.py                       # Gerencia conexão MySQL via variáveis .env
│  ├─ schema.sql                  # Criação das tabelas do banco
│  ├─ seed.sql                    # Dados iniciais para testes
│  ├─ requirements.txt            # Dependências Python
│  ├─ .env.example                # Exemplo de variáveis de ambiente
│  │
│  ├─ routes/
│  │   ├─ products.py             # GET /products, GET /products/{id}
│  │   ├─ orders.py               # GET /orders, POST /orders
│  │   └─ admin_products.py       # Rotas administrativas (/admin/products)
│  │
│  ├─ models/
│  │   ├─ product_model.py        # Funções SQL relacionadas a produtos
│  │   └─ order_model.py          # Funções SQL relacionadas a pedidos
│  │
│  ├─ services/
│  │   └─ order_service.py        # Lógica de transação e concorrência
│  │
│  └─ tests/
│      └─ concurrency_test.py     # Teste de requisições simultâneas (concorrência)
│
├─ frontend/
│  ├─ index.html                  # Interface principal do painel de estoque
│  ├─ css/
│  │   └─ style.css               # Estilos do painel
│  └─ js/
│      └─ app.js                  # Integrações com a API via fetch()
│
└─ README.md

````

---

## Configuração e Execução

### Requisitos
- **Python 3.10+**
- **MySQL 8+**
- Navegador moderno (Chrome, Edge, Firefox)

---

### Criar o banco e tabelas

```bash
mysql -u root -p < backend/schema.sql
mysql -u root -p < backend/seed.sql
````

---

### Configurar variáveis de ambiente

Crie um arquivo `.env` dentro da pasta `backend/` com base no exemplo:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dbpassword
DB_NAME=inventory_db
FLASK_ENV=development
PORT=5000
```

---

### Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

---

### Executar o backend

```bash
python app.py
```

A API iniciará em:

👉 [http://localhost:5000](http://localhost:5000)

---

### Abrir o frontend

Abra `frontend/index.html` diretamente no navegador
ou use o *Live Server* do VSCode.

---

## Funcionalidades

* **Listagem de produtos** e **pedidos**
* **Criação de pedidos com controle de concorrência**
* **Painel administrativo completo**:

  * Adicionar produto
  * Repor estoque
  * Remover produto
  * Registrar vendas
* **Tratamento de erros** e **validação de estoque**

---

## Estrutura do Banco de Dados

```sql
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  stock INT NOT NULL DEFAULT 0
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

---

## Endpoints da API

### Produtos

| Método  | Endpoint         | Descrição                      |
| :------ | :--------------- | :----------------------------- |
| **GET** | `/products`      | Lista todos os produtos        |
| **GET** | `/products/{id}` | Retorna detalhes de um produto |

---

### Pedidos

| Método   | Endpoint  | Corpo (JSON)                        | Descrição                                                           |
| :------- | :-------- | :---------------------------------- | :------------------------------------------------------------------ |
| **GET**  | `/orders` | —                                   | Lista todos os pedidos                                              |
| **POST** | `/orders` | `{ "productId": 1, "quantity": 2 }` | Cria um novo pedido, debitando estoque com controle de concorrência |

---

### Administração (extra – painel de controle)

| Método     | Endpoint               | Corpo (JSON)                          | Descrição                  |
| :--------- | :--------------------- | :------------------------------------ | :------------------------- |
| **POST**   | `/admin/products`      | `{ "name": "Caneta", "stock": 10 }`   | Adiciona novo produto      |
| **PATCH**  | `/admin/products/{id}` | `{ "action": "add", "amount": 5 }`    | Reabastece o estoque       |
| **PATCH**  | `/admin/products/{id}` | `{ "action": "remove", "amount": 2 }` | Remove unidades do estoque |
| **DELETE** | `/admin/products/{id}` | —                                     | Remove produto do sistema  |

---

## Teste de Concorrência

O arquivo `backend/tests/concurrency_test.py` simula **múltiplas requisições simultâneas** para o endpoint `POST /orders`.

Esse teste garante que o sistema **nunca permite estoque negativo** e que o **controle transacional** funciona corretamente.

### 🧾 Exemplo de execução:

```bash
cd backend/tests
python concurrency_test.py
```

Exemplo de saída esperada:

```
[OK] Pedido 1 criado
[OK] Pedido 2 criado
[OK] Pedido 3 criado
...
Estoque final: 0
Nenhum erro de concorrência detectado
```

---

## Frontend

A interface foi construída **sem frameworks**, usando apenas:

* HTML5
* CSS3
* JavaScript (fetch API)

### Recursos:

* Botão **“Novo Produto”** → chama `POST /admin/products`
* Botão **“+ Estoque”** → chama `PATCH /admin/products/{id}`
* Botão **“Vender”** → abre modal e executa `POST /orders`
* Botão **“Remover”** → chama `DELETE /admin/products/{id}`
* Botão **“Atualizar”** → recarrega a lista de produtos/pedidos

---

## Tecnologias Utilizadas

| Camada             | Tecnologia                                              |
| :----------------- | :------------------------------------------------------ |
| **Backend**        | Python 3.10, Flask, Flask-CORS, MySQL Connector, Dotenv |
| **Banco de Dados** | MySQL 8                                                 |
| **Frontend**       | HTML, CSS, JavaScript                                   |
| **Testes**         | Script Python com `requests` e `threading`              |
| **Padrão de API**  | REST (JSON)                                             |

---

## Controle de Concorrência

O controle é implementado via **transações e bloqueios (FOR UPDATE)** no MySQL,
garantindo consistência mesmo sob múltiplas requisições simultâneas.

**Fluxo resumido do `process_order`:**

1. Inicia transação
2. Faz `SELECT stock FROM products WHERE id = %s FOR UPDATE`
3. Verifica se há estoque suficiente
4. Atualiza estoque (`UPDATE products SET stock = stock - %s`)
5. Cria registro em `orders`
6. Dá `COMMIT`

Se algo falhar, executa `ROLLBACK`.

---

## requirements.txt

```txt
Flask==3.0.3
flask-cors==5.0.0
mysql-connector-python==9.0.0
python-dotenv==1.0.1
requests==2.31.0
```

```
