import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Facility - Gestão", page_icon="🏢", layout="centered")

# Conexão (Suas Chaves)
URL = "https://ihcrndrwarcywiixypyp.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloY3JuZHJ3YXJjeXdpaXh5cHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDMxMTcsImV4cCI6MjA4MjY3OTExN30.58Wd3azYScFkCW0VGkxhvZfgjFYPQgpdzypkoIIuFI4"
supabase = create_client(URL, KEY)

# --- FUNÇÃO DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # Tenta mostrar a logo, se ela não existir, mostra só texto
        try:
            st.image("logo.png", width=300) # Ajuste a largura conforme necessário
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
    # Menu Lateral com Logo
    with st.sidebar:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.title("Facility")
        
        st.success("✅ Logado: Admin")
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()

    # Conteúdo Principal
    st.title("📂 Gestão de Prontuários")
    
    aba_consulta, aba_cadastro, aba_relatorio = st.tabs(["🔍 Consulta", "➕ Novo Aluno", "📊 Relatórios"])

    # ABA 1: Consulta
    with aba_consulta:
        busca = st.text_input("Pesquisar aluno:", placeholder="Nome completo...")
        if busca:
            res = supabase.table("alunos").select("*").ilike("nome", f"%{busca}%").limit(50).execute()
            if res.data:
                for aluno in res.data:
                    with st.expander(f"👤 {aluno['nome']}"):
                        st.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
                        st.write(f"**Status:** {aluno.get('status_arquivo', '-')}")
                        st.write(f"**Local:** {aluno.get('localizacao', '-')}")
            else:
                st.warning("Nada encontrado.")

    # ABA 2: Cadastro
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

    # ABA 3: Relatórios
    with aba_relatorio:
        if st.button("Atualizar Gráficos"):
            df = pd.DataFrame(supabase.table("alunos").select("status_arquivo").execute().data)
            if not df.empty:
                st.bar_chart(df['status_arquivo'].value_counts())
                st.metric("Total de Alunos", len(df))