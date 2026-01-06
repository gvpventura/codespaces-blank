import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

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
    
    # As três abas configuradas corretamente
    aba_consulta, aba_cadastro, aba_relatorio = st.tabs(["🔍 Consulta", "➕ Novo Aluno", "📊 Relatórios"])

   # --- ABA 1: CONSULTA (Com Filtro de Precisão) ---
    with aba_consulta:
        st.subheader("Busca Rápida")
        
        # Primeiro, um campo de texto simples para você digitar
        texto_busca = st.text_input("Comece a digitar o nome:", key="txt_input").upper()
        
        if len(texto_busca) >= 3:
            # Buscamos no banco apenas nomes que CONTÉM o que você digitou
            res = supabase.table("alunos").select("nome").ilike("nome", f"%{texto_busca}%").limit(50).execute()
            
            # Criamos a lista filtrada apenas com o que o banco retornou
            opcoes = [aluno['nome'] for aluno in res.data]
            
            if opcoes:
                escolha = st.selectbox("Selecione o aluno exato na lista:", [""] + opcoes)
                
                if escolha:
                    # Aqui ele busca os dados do aluno selecionado
                    detalhes = supabase.table("alunos").select("*").eq("nome", escolha).execute()
                    # ... (resto do código de exibição dos dados)
            else:
                st.warning("Nenhum nome encontrado com esses termos.")

    # --- ABA 2: CADASTRO ---
    with aba_cadastro:
        with st.form("novo_aluno"):
            st.subheader("Cadastrar Novo Aluno")
            n_nome = st.text_input("Nome Completo").upper()
            n_mae = st.text_input("Nome da Mãe").upper()
            n_nasc = st.date_input("Data de Nascimento", value=None)
            n_status = st.selectbox("Status", ["VIVO", "PERMANENTE"])
            n_local = st.text_input("Localização (Gaveta/Pasta)").upper()
            
            if st.form_submit_button("Salvar no Banco"):
                if n_nome:
                    novo_dados = {
                        "nome": n_nome,
                        "nome_mae": n_mae,
                        "data_nascimento": str(n_nasc) if n_nasc else None,
                        "status_arquivo": n_status,
                        "localizacao": n_local
                    }
                    supabase.table("alunos").insert(novo_dados).execute()
                    st.success(f"{n_nome} cadastrado com sucesso!")

    # --- ABA 3: RELATÓRIOS ---
    with aba_relatorio:
        st.subheader("Estatísticas do Acervo")
        if st.button("Atualizar Dados do Relatório"):
            res_rel = supabase.table("alunos").select("status_arquivo").execute()
            df = pd.DataFrame(res_rel.data)
            
            if not df.empty:
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.metric("Total Geral", len(df))
                with col_r2:
                    ativos = len(df[df['status_arquivo'] == 'VIVO'])
                    st.metric("Arquivos Vivos", ativos)
                with col_r3:
                    ativos = len(df[df['status_arquivo'] == 'PERMANENTE'])
                    st.metric("Arquivos Permanentes", ativos)
                
                st.write("---")
                st.bar_chart(df['status_arquivo'].value_counts())
            else:
                st.info("Sem dados disponíveis.")