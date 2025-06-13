# -*- coding: utf-8 -*-
from flask import Flask, request, render_template_string, redirect, url_for
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import folium
import json
import os

# Autenticação Google
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
service_account_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(credentials)

# ID da planilha
SHEET_ID = "13PIgTsoYnr4z5ihe0CR8zXghlXaAXc__BOxS8HigXqM"
sh = client.open_by_key(SHEET_ID)

# Flask
app = Flask(__name__)
SENHA_PRIVADA = "1234"

TEMPLATE_BASE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>{{ titulo }}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { margin: 20px; }
        .table th, .table td { text-align: center; vertical-align: middle; }
        .nav-buttons { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ titulo }}</h1>
        <div class="nav-buttons">
            {% if titulo != "Área Privada - Login" %}
                <a class="btn btn-primary" href="/">Início</a>
            {% endif %}
            {% if titulo == "Imóveis Disponíveis" %}
                <a class="btn btn-secondary" href="/login">Área Privada</a>
            {% endif %}
        </div>
        <hr>
        {{ conteudo|safe }}
        <footer class="mt-4 text-center">
            <hr>
            <p>
                <a href="https://github.com/silvagui04/GestaoImoveis2/tree/main" target="_blank">GitHub</a> |
                <a href="https://docs.google.com/document/d/1pRScDde4t2-orWBHa1JCA4LnXiDHR9qztdFvIv1YUl0/edit?usp=sharing" target="_blank">Relatório</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    df_imoveis = pd.DataFrame(sh.worksheet("Imoveis").get_all_records())
    tabela_html = df_imoveis[["Nome", "Cidade", "Rua", "Estrutura"]].to_html(
        classes='table table-bordered table-hover', index=False, border=0
    )
    conteudo = f"""
    <div class="tabela-wrapper">
        <h2>Lista de Imóveis</h2>
        <div style="max-height: 400px; overflow-y: auto;">
            {tabela_html}
        </div>
        <a href="/mapa" class="btn btn-info mt-3">Ver Mapa dos Imóveis</a>
    </div>
    """
    return render_template_string(TEMPLATE_BASE, titulo="Imóveis Disponíveis", conteudo=conteudo)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == SENHA_PRIVADA:
            return redirect(url_for("privado"))
        else:
            return render_template_string(TEMPLATE_BASE, titulo="Login", conteudo="<p>Senha incorreta!</p>")

    conteudo = """
    <form method="POST" class="mt-4">
        <input type="password" name="senha" class="form-control mb-2" placeholder="Digite a senha">
        <button type="submit" class="btn btn-primary">Entrar</button>
    </form>
    """
    return render_template_string(TEMPLATE_BASE, titulo="Login - Área Privada", conteudo=conteudo)

@app.route("/privado")
def privado():
    df_imoveis = pd.DataFrame(sh.worksheet("Imoveis").get_all_records())
    df_clientes = pd.DataFrame(sh.worksheet("Clientes").get_all_records())

    tabela_clientes = df_clientes.to_html(classes='table table-striped', index=False)
    tabela_imoveis = df_imoveis.to_html(classes='table table-striped', index=False)

    conteudo = f"""
    <h2>Clientes</h2>
    {tabela_clientes}
    <h2>Imóveis - Detalhes</h2>
    {tabela_imoveis}
    """
    return render_template_string(TEMPLATE_BASE, titulo="Área Privada", conteudo=conteudo)

@app.route("/mapa")
def mapa():
    df_imoveis = pd.DataFrame(sh.worksheet("Imoveis").get_all_records())

    if "Latitude" not in df_imoveis.columns or "Longitude" not in df_imoveis.columns:
        return render_template_string(TEMPLATE_BASE, titulo="Mapa de Imóveis", conteudo="<p>Colunas de localização ausentes.</p>")

    mapa = folium.Map(location=[39.5, -8.0], zoom_start=6)

    for _, row in df_imoveis.iterrows():
        if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=row.get("Nome", "Imóvel"),
                tooltip=row.get("Cidade", "")
            ).add_to(mapa)

    mapa_html = mapa._repr_html_()

    conteudo = f"""
    <h2>Localização dos Imóveis</h2>
    <div style="height: 500px;">
        {mapa_html}
    </div>
    """
    return render_template_string(TEMPLATE_BASE, titulo="Mapa de Imóveis", conteudo=conteudo)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
