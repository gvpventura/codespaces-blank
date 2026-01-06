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

    # --- ABA 1: CONSULTA ---
    with aba_consulta:
        st.subheader("Busca Rápida Facility")
        
        # Busca reativa por Selectbox (Zero Enter)
        res_nomes = supabase.table("alunos").select("nome").limit(2000).execute()
        lista_nomes = sorted([aluno['nome'] for aluno in res_nomes.data]) if res_nomes.data else []
        
        escolha = st.selectbox(
            "Digite o nome do aluno aqui:",
            options=[""] + lista_nomes,
            format_func=lambda x: "🔍 Comece a digitar para pesquisar..." if x == "" else x,
            key="busca_principal"
        )

        if escolha != "":
            detalhes = supabase.table("alunos").select("*").eq("nome", escolha).execute()
            if detalhes.data:
                aluno = detalhes.data[0]
                
                # Tratamento da Data Brasileira
                dt_banco = aluno.get('data_nascimento')
                dt_br = "-"
                if dt_banco:
                    try:
                        dt_br = datetime.strptime(dt_banco, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        dt_br = dt_banco

                st.success(f"✅ Prontuário Localizado: {aluno['nome']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
                    st.write(f"**Nascimento:** {dt_br}")
                with c2:
                    st.write(f"**Localização:** {aluno.get('localizacao', '-')}")
                    st.write(f"**Status:** {aluno.get('status_arquivo', '-')}")

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
                
                st.write("---")
                st.bar_chart(df['status_arquivo'].value_counts())
            else:
                st.info("Sem dados disponíveis.")