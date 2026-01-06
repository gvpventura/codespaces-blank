import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime  # <--- ESSA LINHA É A QUE RESOLVE O ERRO DA IMAGEM

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Facility - Gestão", page_icon="🏢", layout="centered")

# Conexão (Chaves do seu banco)
URL = "https://ihcrndrwarcywiixypyp.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloY3JuZHJ3YXJjeXdpaXh5cHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDMxMTcsImV4cCI6MjA4MjY3OTExN30.58Wd3azYScFkCW0VGkxhvZfgjFYPQgpdzypkoIIuFI4"
supabase = create_client(URL, KEY)

# --- FUNÇÃO DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        try:
            st.image("logo.png", width=250)
        except:
            st.title("Facility Soluções")
            
        st.markdown("### Acesso Restrito")
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Acessar Sistema", type="primary")
            if entrar:
                if usuario == "admin" and senha == "12345":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
        return False
    return True

# --- SISTEMA PRINCIPAL ---
if login():
    st.title("📂 Gestão de Prontuários")
    aba_consulta, aba_cadastro = st.tabs(["🔍 Consulta", "➕ Novo Aluno"])

    with aba_consulta:
        st.subheader("Busca Rápida Facility")
        
        # 1. Busca os nomes para o seletor (limitado para ser rápido)
        res_nomes = supabase.table("alunos").select("nome").limit(2000).execute()
        lista_nomes = sorted([aluno['nome'] for aluno in res_nomes.data]) if res_nomes.data else []
        
        # Seletor que filtra enquanto você digita
        escolha = st.selectbox(
            "Digite o nome do aluno aqui:",
            options=[""] + lista_nomes,
            format_func=lambda x: "🔍 Comece a digitar para pesquisar..." if x == "" else x,
            key="busca_total"
        )

        if escolha != "":
            detalhes = supabase.table("alunos").select("*").eq("nome", escolha).execute()
            if detalhes.data:
                aluno = detalhes.data[0]
                
                # --- LÓGICA DE DATA BRASILEIRA ---
                data_banco = aluno.get('data_nascimento')
                data_br = "-"
                if data_banco:
                    try:
                        # Converte de 2024-12-31 para 31/12/2024
                        data_br = datetime.strptime(data_banco, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        data_br = data_banco

                st.success(f"✅ Prontuário Localizado: {aluno['nome']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
                    st.write(f"**Nascimento:** {data_br}")
                with col2:
                    st.write(f"**Localização:** {aluno.get('localizacao', '-')}")
                    st.write(f"**Status:** {aluno.get('status_arquivo', '-')}")

    with aba_cadastro:
        with st.form("novo_aluno"):
            st.subheader("Cadastrar Novo Aluno")
            n_nome = st.text_input("Nome Completo").upper()
            n_mae = st.text_input("Nome da Mãe").upper()
            n_nasc = st.date_input("Data de Nascimento", value=None)
            n_local = st.text_input("Localização (Gaveta/Pasta)").upper()
            
            if st.form_submit_button("Salvar no Banco de Dados"):
                if n_nome:
                    novo_aluno = {
                        "nome": n_nome,
                        "nome_mae": n_mae,
                        "data_nascimento": str(n_nasc) if n_nasc else None,
                        "localizacao": n_local
                    }
                    supabase.table("alunos").insert(novo_aluno).execute()
                    st.success("Aluno cadastrado com sucesso!")
                else:
                    st.warning("O nome é obrigatório.")