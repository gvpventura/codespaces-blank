import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Facility - Gestão", page_icon="🏢", layout="centered")

# --- CSS PARA DEIXAR O SITE LIMPO (AGRESSIVO) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Esconde a marca d'água do Streamlit Cloud no canto inferior direito */
            div[data-testid="stStatusWidget"] {display:none;}
            .stApp [data-testid="stDecoration"] {display:none;}
            
            /* Remove o link 'Hosted with Streamlit' e o ícone de engrenagem */
            #viewer-badge {display: none !important;}
            .viewerBadge_container__1QSob {display: none !important;}
            [data-testid="bundle-theme-menu"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Conexão (Suas Chaves)
URL = "https://ihcrndrwarcywiixypyp.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloY3JuZHJ3YXJjeXdpaXh5cHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDMxMTcsImV4cCI6MjA4MjY3OTExN30.58Wd3azYScFkCW0VGkxhvZfgjFYPQgpdzypkoIIuFI4"
supabase = create_client(URL, KEY)

# --- ESTADOS DO SISTEMA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "dados_edicao" not in st.session_state:
    st.session_state.dados_edicao = None

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try:
            st.image("logo.png", width=250)
        except:
            st.title("Facility Soluções")
            
        st.markdown("### Acesso Restrito")
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Acessar Sistema", type="primary"):
                if usuario == "admin" and senha == "12345":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
    st.stop() # Mata a execução aqui se não logar (Evita mostrar o fundo)

# --- SISTEMA PRINCIPAL ---
st.title("📂 Gestão de Prontuários")

aba_consulta, aba_cadastro, aba_relatorio = st.tabs(["🔍 Consulta", "➕ Novo/Editar", "📊 Relatórios"])

# --- ABA 1: CONSULTA ---
with aba_consulta:
    st.subheader("Busca Rápida Facility")
    res_nomes = supabase.table("alunos").select("nome").order("nome").execute()
    lista_nomes = [aluno['nome'] for aluno in res_nomes.data] if res_nomes.data else []
    
    escolha = st.selectbox("Pesquise o aluno:", options=[""] + lista_nomes)

    if escolha:
        detalhes = supabase.table("alunos").select("*").eq("nome", escolha).execute()
        if detalhes.data:
            aluno = detalhes.data[0]
            
            col_msg, col_edit, col_del = st.columns([0.6, 0.2, 0.2])
            with col_msg:
                st.success(f"✅ Localizado: {aluno['nome']}")
            with col_edit:
                if st.button("📝 Editar"):
                    st.session_state.dados_edicao = aluno
                    st.info("Dados carregados! Vá para a aba 'Novo/Editar'")
            with col_del:
                if st.button("🗑️ Excluir"):
                    if st.checkbox("Confirmar exclusão?"):
                        supabase.table("alunos").delete().eq("id", aluno['id']).execute()
                        st.warning("Excluído!")
                        time.sleep(1)
                        st.rerun()
            
            c1, c2 = st.columns(2)
            c1.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
            dt_b = aluno.get('data_nascimento')
            dt_f = datetime.strptime(dt_b, '%Y-%m-%d').strftime('%d/%m/%Y') if dt_b else "-"
            c1.write(f"**Data Nasc.:** {dt_f}")
            c2.write(f"**Localização:** {aluno.get('localizacao', '-')}")
            c2.write(f"**Modalidade:** {aluno.get('ultima_modalidade', '-')}")

# --- ABA 2: CADASTRO / EDIÇÃO (RESOLVIDO DUPLICIDADE) ---
with aba_cadastro:
    editando = st.session_state.dados_edicao is not None
    st.subheader("📝 Editar Registro" if editando else "➕ Cadastrar Novo Aluno")
    
    # Criamos apenas UM formulário que muda de função
    with st.form("form_unico", clear_on_submit=not editando):
        aluno_ref = st.session_state.dados_edicao if editando else {}
        
        f_nome = st.text_input("Nome Completo", value=aluno_ref.get('nome', '')).upper()
        f_mae = st.text_input("Nome da Mãe", value=aluno_ref.get('nome_mae', '')).upper()
        
        d_val = datetime.strptime(aluno_ref['data_nascimento'], '%Y-%m-%d') if editando and aluno_ref.get('data_nascimento') else None
        f_nasc = st.date_input("Data de Nascimento", value=d_val, min_value=datetime(1900,1,1), format="DD/MM/YYYY")
        
        opcoes_mod = ["ENSINO FUNDAMENTAL - REGULAR", "ENSINO MEDIO - REGULAR", "PROFISSIONALIZANTE", "CURSO TECNICO", "EJA-ENS. FUNDAMENTAL", "EJA-ENS. MEDIO", "OUTROS"]
        idx_m = opcoes_mod.index(aluno_ref['ultima_modalidade']) if editando and aluno_ref.get('ultima_modalidade') in opcoes_mod else 0
        f_mod = st.selectbox("Modalidade:", opcoes_mod, index=idx_m)
        
        f_local = st.text_input("Localização", value=aluno_ref.get('localizacao', '')).upper()
        f_status = st.selectbox("Status", ["VIVO", "PERMANENTE"], index=1 if aluno_ref.get('status_arquivo') == "PERMANENTE" else 0)

        if st.form_submit_button("Atualizar" if editando else "Salvar"):
            dados = {"nome": f_nome, "nome_mae": f_mae, "data_nascimento": str(f_nasc), "ultima_modalidade": f_mod, "localizacao": f_local, "status_arquivo": f_status}
            if editando:
                supabase.table("alunos").update(dados).eq("id", aluno_ref['id']).execute()
                st.session_state.dados_edicao = None
            else:
                supabase.table("alunos").insert(dados).execute()
            
            st.success("Sucesso!")
            time.sleep(1)
            st.rerun()

    if editando:
        if st.button("❌ Cancelar Edição"):
            st.session_state.dados_edicao = None
            st.rerun()

# --- ABA 3: RELATÓRIOS ---
with aba_relatorio:
    st.subheader("Estatísticas do Acervo")
    res_rel = supabase.table("alunos").select("status_arquivo, ultima_modalidade").execute()
    if res_rel.data:
        df = pd.DataFrame(res_rel.data)
        c_r1, c_r2 = st.columns(2)
        c_r1.metric("Total de Alunos", len(df))
        c_r2.metric("Arquivos Vivos", len(df[df['status_arquivo'] == 'VIVO']))
        
        st.write("---")
        st.write("**Distribuição por Modalidade**")
        st.bar_chart(df['ultima_modalidade'].value_counts())
    else:
        st.info("Aguardando dados para gerar relatórios.")