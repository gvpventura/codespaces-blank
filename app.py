import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import time


st.set_page_config(page_title="Facility - Gestão", page_icon="🏢", layout="centered")

# --- CSS PARA DEIXAR O SITE LIMPO (VISUAL PROFISSIONAL) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
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
if "aba_selecionada" not in st.session_state:
    st.session_state.aba_selecionada = 0
if "dados_edicao" not in st.session_state:
    st.session_state.dados_edicao = None


# Função para mudar de aba via código
def mudar_aba(index):
    st.session_state.aba_selecionada = index
    st.rerun()


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
            entrar = st.form_submit_button("Acessar Sistema", type="primary")
            if entrar:
                if usuario == "admin" and senha == "12345":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
    st.stop() # Interrompe a execução aqui para não mostrar as abas embaixo


# --- SISTEMA PRINCIPAL (SÓ EXECUTA SE AUTENTICADO) ---
st.title("📂 Gestão de Prontuários")


aba_consulta, aba_cadastro, aba_relatorio = st.tabs(["🔍 Consulta", "➕ Novo/Editar", "📊 Relatórios"])


# --- ABA 1: CONSULTA ---
with aba_consulta:
    st.subheader("Busca Rápida")
    res_nomes = supabase.table("alunos").select("nome").order("nome").execute()
    lista_nomes = [aluno['nome'] for aluno in res_nomes.data] if res_nomes.data else []
   
    escolha = st.selectbox("Pesquise o aluno:", options=[""] + lista_nomes, key="busca_final")


    if escolha:
        detalhes = supabase.table("alunos").select("*").eq("nome", escolha).execute()
        if detalhes.data:
            aluno = detalhes.data[0]
           
            # Tarja de sucesso e botões de ação
            col_msg, col_edit, col_del = st.columns([0.6, 0.2, 0.2])
            with col_msg:
                st.success(f"✅ Registro Localizado: {aluno['nome']}")
           
            with col_edit:
                if st.button("📝 Editar"):
                    st.session_state.dados_edicao = aluno
                    # Mudar de aba programaticamente requer que o usuário clique na aba
                    # ou use uma lógica de rádio/botão lateral, no Streamlit nativo
                    # a aba 'selecionada' visualmente não muda sozinha via index em st.tabs.
                    # Por enquanto, avisamos para clicar ao lado:
                    st.info("Clique na aba 'Novo/Editar'")
           
            with col_del:
                if st.button("🗑️ Excluir"):
                    st.session_state.confirmar_exclusao = aluno['id']
           
            # Confirmação de exclusão caso clicado
            if "confirmar_exclusao" in st.session_state and st.session_state.confirmar_exclusao == aluno['id']:
                st.warning(f"Tem certeza que deseja excluir o prontuário de {aluno['nome']}?")
                col_sim, col_nao = st.columns(2)
                if col_sim.button("Sim, Excluir"):
                    supabase.table("alunos").delete().eq("id", aluno['id']).execute()
                    st.success("Excluído com sucesso!")
                    del st.session_state.confirmar_exclusao
                    time.sleep(1)
                    st.rerun()
                if col_nao.button("Não, Cancelar"):
                    del st.session_state.confirmar_exclusao
                    st.rerun()


            # Exibição dos dados
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
                dt_b = aluno.get('data_nascimento')
                dt_exibir = datetime.strptime(dt_b, '%Y-%m-%d').strftime('%d/%m/%Y') if dt_b else "-"
                st.write(f"**Data Nasc.:** {dt_exibir}")
            with c2:
                st.write(f"**Localização:** {aluno.get('localizacao', '-')}")
                st.write(f"**Modalidade:** {aluno.get('ultima_modalidade', '-')}")
                st.write(f"**Status:** {aluno.get('status_arquivo', '-')}")


# --- ABA 2: CADASTRO / EDIÇÃO (CÓDIGO ÚNICO) ---
with aba_cadastro:
    editando = st.session_state.dados_edicao is not None
    st.subheader("📝 Editar Registro" if editando else "➕ Cadastrar Novo Aluno")
   
    with st.form("form_unico", clear_on_submit=not editando):
        aluno_ref = st.session_state.dados_edicao if editando else {}
       
        f_nome = st.text_input("Nome Completo", value=aluno_ref.get('nome', '')).upper()
        f_mae = st.text_input("Nome da Mãe", value=aluno_ref.get('nome_mae', '')).upper()
       
        # Data
        d_val = None
        if editando and aluno_ref.get('data_nascimento'):
            d_val = datetime.strptime(aluno_ref['data_nascimento'], '%Y-%m-%d')
       
        f_nasc = st.date_input("Data de Nascimento", value=d_val,
                               min_value=datetime(1900,1,1), format="DD/MM/YYYY")
       
        opcoes_mod = ["ENSINO FUNDAMENTAL - REGULAR", "ENSINO MEDIO - REGULAR", "PROFISSIONALIZANTE",
                      "CURSO TECNICO", "EJA-ENS. FUNDAMENTAL", "EJA-ENS. MEDIO", "OUTROS"]
       
        # Achar índice da modalidade para o selectbox
        idx_m = 0
        if editando and aluno_ref.get('ultima_modalidade') in opcoes_mod:
            idx_m = opcoes_mod.index(aluno_ref['ultima_modalidade'])
           
        f_mod = st.selectbox("Modalidade:", opcoes_mod, index=idx_m)
        f_local = st.text_input("Localização (Gaveta/Pasta)", value=aluno_ref.get('localizacao', '')).upper()
       
        idx_s = 1 if editando and aluno_ref.get('status_arquivo') == "PERMANENTE" else 0
        f_status = st.selectbox("Status", ["VIVO", "PERMANENTE"], index=idx_s)


        if st.form_submit_button("Atualizar Dados" if editando else "Salvar no Banco"):
            if f_nome:
                dados = {
                    "nome": f_nome, "nome_mae": f_mae, "data_nascimento": str(f_nasc) if f_nasc else None,
                    "ultima_modalidade": f_mod, "localizacao": f_local, "status_arquivo": f_status
                }
                try:
                    if editando:
                        supabase.table("alunos").update(dados).eq("id", aluno_ref['id']).execute()
                        st.success("Atualizado com sucesso!")
                        st.session_state.dados_edicao = None
                    else:
                        supabase.table("alunos").insert(dados).execute()
                        st.success("Cadastrado com sucesso!")
                   
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("O nome é obrigatório.")


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

