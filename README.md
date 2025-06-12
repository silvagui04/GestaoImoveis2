# GestaoImoveis2

# 🏠 Gestão de Imóveis - Flask App

## 📌 Visão Geral
Esta aplicação Flask permite a gestão e visualização de imóveis e clientes, com dados armazenados em uma Google Sheet conectada via API. Inclui uma interface pública simplificada e uma área privada com filtros avançados.

---

## 🔧 Stack Tecnológica

- **Backend:** Python + Flask
- **Planilha:** Google Sheets
- **Bibliotecas:**  
  - `gspread` para integração com Sheets  
  - `pandas` para tratamento de dados  
  - `flask` para servidor web  
  - `dotenv` para variáveis de ambiente  

---

## 📁 Estrutura dos Dados

### 📄 Aba 1 — `Imoveis`

| Coluna              | Descrição                        |
|---------------------|----------------------------------|
| Nome                | Nome do imóvel                   |
| Cidade              | Localização                      |
| Rua                 | Morada                           |
| Tipo                | Tipologia (T1, T2, T3...)         |
| Classe Energética   | Eficiência energética             |
| Tem Jardim          | Sim/Não                          |
| Data Construção     | Data ou ano                      |
| Estrutura           | Tipo de construção (Madeira, etc)|
| Preço (€)           | Valor do imóvel                  |
| Latitude / Longitude| Para localização geográfica      |

### 📄 Aba 2 — `Clientes`

| Coluna           | Descrição                       |
|------------------|---------------------------------|
| Nome             | Nome do cliente                 |
| Email            | Contacto                        |
| Telefone         | Telemóvel                       |
| NIF              | Número de identificação fiscal  |
| Casa Atribuída   | Nome do imóvel associado        |

---

## 🌐 Rotas da Aplicação

| Rota         | Método | Descrição                                                                 |
|--------------|--------|---------------------------------------------------------------------------|
| `/`          | GET    | Página pública: lista resumida dos imóveis com Nome, Cidade, Rua e Estrutura |
| `/login`     | GET/POST | Login para área privada. Valida senha.                                 |
| `/privado`   | GET/POST | Área privada. Mostra imóveis + clientes. Filtros por localização, preço, nome, email, etc.|

---

## 🔐 Segurança

- **Autenticação Google Sheets:**  
  Feita com `gspread` usando `service_account.Credentials.from_service_account_info`.
  A variável de ambiente `GOOGLE_CREDENTIALS` deve conter o JSON das credenciais.

- **Senha de acesso privado:**  
  Definida no código (`1234`).

---

## 📦 Variáveis de Ambiente Necessárias

```env
GOOGLE_CREDENTIALS=<JSON string com as credenciais>
SHEET_ID=<ID da planilha Google Sheets>
```

---

## 📥 Requisitos de Instalação

```bash
pip install -r requirements.txt
```

---

## ▶️ Execução Local

```bash
python flask_gestao_imoveis.py
```

---

## 🔄 Funcionalidades Futuras (sugestões)

- Upload de novos imóveis via formulário
- Exportação em CSV/PDF
- Autenticação por utilizador (multiuser)
- Dashboard de reservas e histórico de clientes
