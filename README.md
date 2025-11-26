# 🎓 Sistema de Gestão de Estudantes

Sistema de gerenciamento acadêmico desenvolvido para fins educacionais na disciplina de Banco de Dados (Prof. Howard).

O sistema agora utiliza **MongoDB**, substituindo completamente:

- Oracle → **MongoDB**
- SQL → **consultas MongoDB (`find`, `aggregate`, `update`, `delete`)**
- Conexão Oracle → **PyMongo**

---

## 🧭 Visão Geral

O projeto é dividido em duas camadas principais:

- **Backend:** Desenvolvido em Python (Flask) com banco NoSQL MongoDB  
- **Frontend:** Desenvolvido em HTML, CSS e JavaScript, com painéis dinâmicos e modais interativos

---

## 📁 Estrutura do Projeto

```
C2-RealSystemSimulation-MongoDB/
├── backend/
│   ├── controllers/          # Controladores para cada entidade
│   ├── db/                   # Conexão e configuração MongoDB
│   ├── app.py                # Aplicação Flask principal
│   ├── requirements.txt      # Dependências Python
│   └── .env.example          # Exemplo de configuração
├── frontend/
│   ├── index.html            # Interface principal
│   ├── scripts/              # JavaScript (API, CRUD, relatórios)
│   └── styles/               # CSS global
└── README.md
```

---

## ⚙️ Instalação e Configuração

### 1. 🧩 Requisitos

- **Python 3.x**
- **MongoDB** instalado e rodando em `localhost:27017`
- **pip**

---

### 2. 📦 Instalar Dependências

No diretório `backend/`, execute:

```bash
cd backend
pip install -r requirements.txt
```

---

### 3. 🔐 Configurar Variáveis de Ambiente

Crie o arquivo `.env` baseado no `.env.example`:

```ini
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=sge_database
```

---

## 🗃️ Banco de Dados (MongoDB)

### Coleções Criadas

- `students`
- `courses`
- `professors`
- `subjects`
- `offers`
- `enrollments`

---

## 🚀 Executar o Backend

Dentro da pasta `backend/`, execute:

```bash
python app.py
```

A aplicação iniciará em:

```
http://localhost:5000
```

---

## 🔗 Exemplos de Endpoints

```
GET  /api/students
POST /api/students
GET  /api/reports/course-statistics
GET  /api/reports/offers-complete
```

---

# 🔄 Consultas convertidas para MongoDB

## 📊 Estatísticas por Curso (equivalente ao COUNT/SUM SQL)

```python
db.students.aggregate([
    {
        "$group": {
            "_id": "$course_id",
            "total_students": {"$count": {}}
        }
    }
])
```

---

## 📚 Ofertas Completas (equivalente ao SQL com vários JOINs)

```python
db.offers.aggregate([
    {
        "$lookup": {
            "from": "subjects",
            "localField": "subject_id",
            "foreignField": "_id",
            "as": "subject"
        }
    },
    {
        "$lookup": {
            "from": "professors",
            "localField": "professor_id",
            "foreignField": "_id",
            "as": "professor"
        }
    },
    {
        "$lookup": {
            "from": "courses",
            "localField": "course_id",
            "foreignField": "_id",
            "as": "course"
        }
    }
])
```

---

# ⚙️ Conexão MongoDB (PyMongo)

```python
from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
```

---

## 🧱 Funcionalidades Principais

### 🧍‍♂️ Alunos
- CRUD completo  
- Validação  
- Datas em múltiplos formatos  

### 🎓 Cursos
- Associação com matérias e alunos  
- Controle de carga horária  

### 👩‍🏫 Professores
- Cadastro e consultas  
- Status ativo/inativo  

### 📚 Matérias e Ofertas
- Uso de `$lookup` para relacionamentos  
- Controle de semestre e professor  

### 📝 Matrículas
- Controle via coleção `enrollments`  
- Status de cursando, aprovado, reprovado  

### 📊 Relatórios
- Estatísticas por curso  
- Lista completa de ofertas  
- Dashboard geral  

---

## 🧰 Tecnologias Utilizadas

**Backend**
- Python 3.x  
- Flask 2.3.2  
- PyMongo 4.6.1  
- Flask-CORS 4.0.0  
- python-dotenv 1.0.0  

**Frontend**
- HTML5  
- CSS3  
- JavaScript Vanilla  
- Fetch API  

**Banco de Dados**
- MongoDB  

---

## 🔧 Troubleshooting

### Erro: "MongoDB connection refused"
Execute:

```bash
mongod
```

### Frontend não conecta ao backend
- Verifique se a API está em `http://localhost:5000`
- Limpe o cache do navegador: Ctrl+Shift+R
- Verifique o console (F12)

---

## ⚠️ Observações Importantes

1. **Segurança:** O sistema é apenas educacional.  
2. **Propósito:** Demonstra CRUD, agregações MongoDB e arquitetura REST.  
3. **Banco:** Consultas com `$lookup`, `$group`, `$match`, `$project`.  

---

## 👥 Equipe de Desenvolvimento

- Bernardo Lodi  
- João Guilherme  
- Luanna Moreira  
- Luiz Hélio  
- Pedro Sousa  
- Thomas Veiga  

---

## 📘 Licença

Projeto sob licença MIT — uso educacional.



