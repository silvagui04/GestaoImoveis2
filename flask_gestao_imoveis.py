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

SHEET_ID = "13PIgTsoYnr4z5ihe0CR8zXghlXaAXc__BOxS8HigXqM"
sh = client.open_by_key(SHEET_ID)

app = Flask(__name__)
SENHA_PRIVADA = "1234"

TEMPLATE_BASE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>{{ titulo }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="max-w-6xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-blue-900 mb-4">{{ titulo }}</h1>
        <div class="mb-4 flex gap-2">
            {% if titulo != "Área Privada - Login" %}
                <a class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition" href="/">Início</a>
            {% endif %}
            {% if titulo == "Imóveis Disponíveis" %}
                <a class="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800 transition" href="/login">Área Privada</a>
            {% endif %}
        </div>
        <hr class="mb-6">
        {{ conteudo|safe }}
        <footer class="mt-12 text-center text-sm text-gray-500">
            <hr class="my-4">
            <p>
                <a class="text-blue-600 hover:underline" href="https://github.com/silvagui04/GestaoImoveis2/tree/main" target="_blank">GitHub</a> |
                <a class="text-blue-600 hover:underline" href="https://docs.google.com/document/d/1pRScDde4t2-orWBHa1JCA4LnXiDHR9qztdFvIv1YUl0/edit?usp=sharing" target="_blank">Relatório</a>
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
        classes='min-w-full divide-y divide-gray-300 table-auto border border-gray-300', index=False, border=0
    )
    conteudo = f"""
    <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold text-teal-600 mb-3">Lista de Imóveis</h2>
        <div class="overflow-x-auto max-h-[400px] overflow-y-auto">
            {tabela_html}
        </div>
        <a href="/mapa" class="inline-block mt-4 bg-teal-500 text-white px-4 py-2 rounded hover:bg-teal-600 transition">Ver Mapa dos Imóveis</a>
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
            return render_template_string(TEMPLATE_BASE, titulo="Login", conteudo="<p class='text-red-600'>Palavra passe incorreta!</p>")

    conteudo = """
    <form method="POST" class="max-w-md mt-6">
        <input type="password" name="senha" class="w-full border border-gray-300 p-2 rounded mb-2" placeholder="Digite a senha">
        <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">Entrar</button>
    </form>
    """
    return render_template_string(TEMPLATE_BASE, titulo="Login - Área Privada", conteudo=conteudo)

@app.route("/privado")
def privado():
    df_imoveis = pd.DataFrame(sh.worksheet("Imoveis").get_all_records())
    df_clientes = pd.DataFrame(sh.worksheet("Clientes").get_all_records())

    tabela_clientes = df_clientes.to_html(classes='min-w-full divide-y divide-gray-300 table-auto border border-gray-300', index=False)
    tabela_imoveis = df_imoveis.to_html(classes='min-w-full divide-y divide-gray-300 table-auto border border-gray-300', index=False)

    conteudo = f"""
    <div class="mb-6">
        <h2 class="text-xl font-semibold text-teal-600 mb-2">Clientes</h2>
        <div class="overflow-x-auto bg-white p-4 rounded shadow">
            {tabela_clientes}
        </div>
    </div>
    <div>
        <h2 class="text-xl font-semibold text-teal-600 mb-2">Imóveis - Detalhes</h2>
        <div class="overflow-x-auto bg-white p-4 rounded shadow">
            {tabela_imoveis}
        </div>
    </div>
    """
    return render_template_string(TEMPLATE_BASE, titulo="Área Privada", conteudo=conteudo)

@app.route("/mapa")
def mapa():
    df_imoveis = pd.DataFrame(sh.worksheet("Imoveis").get_all_records())

    if "Latitude" not in df_imoveis.columns or "Longitude" not in df_imoveis.columns:
        return render_template_string(TEMPLATE_BASE, titulo="Mapa de Imóveis", conteudo="<p class='text-red-600'>Colunas de localização ausentes.</p>")

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
    <h2 class="text-xl font-semibold text-teal-600 mb-2">Localização dos Imóveis</h2>
    <div class="bg-white p-4 rounded shadow">
        {mapa_html}
    </div>
    """
    return render_template_string(TEMPLATE_BASE, titulo="Mapa de Imóveis", conteudo=conteudo)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
