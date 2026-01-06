import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime  # <--- ESSA LINHA RESOLVE O ERRO DA IMAGEM

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Facility - Gestão", page_icon="🏢", layout="centered")

# Conexão (Verifique se suas chaves estão corretas abaixo)
URL = "https://ihcrndrwarcywiixypyp.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloY3JuZHJ3YXJjeXdpaXh5cHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDMxMTcsImV4cCI6MjA4MjY3OTExN30.58Wd3azYScFkCW0VGkxhvZfgjFYPQgpdzypkoIIuFI4"
supabase = create_client(URL, KEY)

# --- FUNÇÃO DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        try:
            st.image("logo.png", width=300)
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
    with st.sidebar:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.title("Facility")
        
        st.success("✅ Logado: Admin")
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()

    st.title("📂 Gestão de Prontuários")
    
    aba_consulta, aba_cadastro, aba_relatorio = st.tabs(["🔍 Consulta", "➕ Novo Aluno", "📊 Relatórios"])

from datetime import datetime

# --- ABA 1: CONSULTA ---
with aba_consulta:
    st.subheader("Busca Rápida Facility")
    
    # Buscamos os nomes para o seletor
    res_nomes = supabase.table("alunos").select("nome").limit(1000).execute()
    lista_nomes = [aluno['nome'] for aluno in res_nomes.data]
    
    escolha = st.selectbox(
        "Digite o nome do aluno aqui:",
        options=[""] + lista_nomes,
        format_func=lambda x: "🔍 Digite para pesquisar..." if x == "" else x,
        key="busca_totalmente_viva"
    )

    if escolha != "":
        detalhes = supabase.table("alunos").select("*").eq("nome", escolha).execute()
        if detalhes.data:
            aluno = detalhes.data[0]
            st.success(f"✅ Registro: {aluno['nome']}")
            
            # --- LÓGICA PARA FORMATAR A DATA ---
            data_origem = aluno.get('data_nascimento')
            data_formatada = "-"
            
            # Lógica para converter data do banco (2024-12-31) para Brasil (31/12/2024)
            data_banco = aluno.get('data_nascimento')
            if data_banco:
                try:
                    data_br = datetime.strptime(data_banco, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    data_br = data_banco # Mantém original se houver erro
            else:
                data_br = "-"

            st.write(f"**Nascimento:** {data_br}")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
                st.write(f"**Nascimento:** {data_formatada}") # Exibe a data no padrão DD/MM/AAAA
            with col2:
                st.write(f"**Localização:** {aluno.get('localizacao', '-')}")
                st.write(f"**Status:** {aluno.get('status_arquivo', '-')}")

    # --- ABA 2: CADASTRO ---
    with aba_cadastro:
        with st.form("novo_aluno"):
            st.subheader("Novo Registro")
            nome = st.text_input("Nome Completo")
            mae = st.text_input("Nome da Mãe")
            status = st.selectbox("Status", ["VIVO", "PERMANENTE"])
            modalidade = st.text_input("Modalidade")
            local = st.text_input("Localização")
            
            if st.form_submit_button("Salvar Registro"):
                if nome:
                    dados = {
                        "nome": nome.upper(),
                        "nome_mae": mae.upper(),
                        "status_arquivo": status,
                        "ultima_modalidade": modalidade.upper(),
                        "localizacao": local.upper()
                    }
                    supabase.table("alunos").insert(dados).execute()
                    st.success(f"{nome} cadastrado!")

    # --- ABA 3: RELATÓRIOS ---
    with aba_relatorio:
        if st.button("Atualizar Gráficos"):
            res = supabase.table("alunos").select("status_arquivo").execute()
            df = pd.DataFrame(res.data)
            if not df.empty:
                st.bar_chart(df['status_arquivo'].value_counts())
                st.metric("Total de Alunos", len(df))