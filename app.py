import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Facility - Gestão", page_icon="🏢", layout="centered")

# Conexão (Suas Chaves)
URL = "https://ihcrndrwarcywiixypyp.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloY3JuZHJ3YXJjeXdpaXh5cHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDMxMTcsImV4cCI6MjA4MjY3OTExN30.58Wd3azYScFkCW0VGkxhvZfgjFYPQgpdzypkoIIuFI4"
supabase = create_client(URL, KEY)

# --- FUNÇÕES DE APOIO ---
def registrar_log(acao, aluno, detalhes=""):
    """Grava a auditoria na tabela logs_alteracao"""
    try:
        log_dados = {
            "usuario_nome": st.session_state.nome_usuario,
            "acao": acao,
            "aluno_afetado": aluno,
            "detalhes": detalhes
        }
        supabase.table("logs_alteracao").insert(log_dados).execute()
    except:
        pass

# --- ESTADOS DO SISTEMA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""
if "aba_selecionada" not in st.session_state:
    st.session_state.aba_selecionada = 0
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
            entrar = st.form_submit_button("Acessar Sistema", type="primary")

            if entrar:
                res_user = supabase.table("usuarios").select("nome").eq("login", usuario).eq("senha", senha).execute()
                if res_user.data:
                    st.session_state.autenticado = True
                    st.session_state.nome_usuario = res_user.data[0]['nome']
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()


# --- SISTEMA PRINCIPAL (SÓ EXECUTA SE AUTENTICADO) ---

# 1. MENU LATERAL (SIDEBAR)
with st.sidebar:
    try:
        # A logo fica no topo da lateral, centralizada automaticamente pelo Streamlit
        st.image("logo.png", use_container_width=True)
    except:
        st.title("Facility Soluções")
    
    st.markdown("---")
    
    # Informações do Usuário de forma elegante
    st.markdown(f"### 👤 Usuário\n**{st.session_state.nome_usuario}**")
    
    # Botão Sair - Na lateral ele pode ocupar a largura total sem ficar feio
    if st.button("🚪 Encerrar Sessão", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.nome_usuario = ""
        st.rerun()
    
    st.markdown("---")
    st.caption("Facility - Gestão de Prontuários v1.0")

# 2. CONTEÚDO PRINCIPAL (OCUPA O RESTO DA TELA)
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
            
            col_msg, col_edit, col_del = st.columns([0.6, 0.2, 0.2])
            with col_msg:
                st.success(f"✅ Registro Localizado: {aluno['nome']}")
            
            with col_edit:
                if st.button("📝 Editar"):
                    st.session_state.dados_edicao = aluno
                    st.info("Clique na aba 'Novo/Editar'")
            
            with col_del:
                if st.button("🗑️ Excluir"):
                    st.session_state.confirmar_exclusao = aluno['id']
            
            # Confirmação de exclusão
            if "confirmar_exclusao" in st.session_state and st.session_state.confirmar_exclusao == aluno['id']:
                st.warning(f"Tem certeza que deseja excluir o prontuário de {aluno['nome']}?")
                col_sim, col_nao = st.columns(2)
                
                if col_sim.button("Sim, Excluir"):
                    supabase.table("alunos").delete().eq("id", aluno['id']).execute()
                    registrar_log("EXCLUSÃO", aluno['nome'], f"ID {aluno['id']} excluído.")
                    st.success("Excluído com sucesso!")
                    time.sleep(1)
                    del st.session_state.confirmar_exclusao
                    st.rerun()
                
                if col_nao.button("Não, Cancelar"):
                    del st.session_state.confirmar_exclusao
                    st.rerun()

            # Exibição dos dados
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Mãe:** {aluno.get('nome_mae', '-')}")
                dt_b = aluno.get('data_nascimento')
                dt_exibir = datetime.strptime(dt_b, '%Y-%m-%d').strftime('%d/%m/%Y') if dt_b else "-"
                st.write(f"**Data Nasc.:** {dt_exibir}")
            with c2:
                st.write(f"**Localização:** {aluno.get('localizacao', '-')}")
                # Importante: Garantindo o uso da coluna correta conforme solicitado
                st.write(f"**Modalidade:** {aluno.get('ultima_modalidade', '-')}")
                st.write(f"**Status:** {aluno.get('status_arquivo', '-')}")

# --- ABA 2: CADASTRO / EDIÇÃO ---
with aba_cadastro:
    editando = st.session_state.dados_edicao is not None
    st.subheader("📝 Editar Registro" if editando else "➕ Cadastrar Novo Aluno")
    
    with st.form("form_unico", clear_on_submit=not editando):
        aluno_ref = st.session_state.dados_edicao if editando else {}
        
        f_nome = st.text_input("Nome Completo", value=aluno_ref.get('nome', '')).upper()
        f_mae = st.text_input("Nome da Mãe", value=aluno_ref.get('nome_mae', '')).upper()
        
        if editando and aluno_ref.get('data_nascimento'):
            d_val = datetime.strptime(aluno_ref['data_nascimento'], '%Y-%m-%d')
        else:
            d_val = datetime(2000, 1, 1)
        
        f_nasc = st.date_input(
    "Data de Nascimento", 
    value=None,  # Isso deixa o campo vazio
    min_value=datetime(1900, 1, 1), 
    format="DD/MM/YYYY"
)
        
       # 1. MODALIDADE: Adicionamos "" no início da lista
        opcoes_mod = ["", "ENSINO FUNDAMENTAL - REGULAR", "ENSINO MEDIO - REGULAR", "PROFISSIONALIZANTE", "CURSO TECNICO", "EJA-ENS. FUNDAMENTAL", "EJA-ENS. MEDIO", "OUTROS"]
        
        # Se estiver editando, busca o índice da modalidade atual. Se for novo, index é 0 (vazio).
        idx_m = opcoes_mod.index(aluno_ref['ultima_modalidade']) if editando and aluno_ref.get('ultima_modalidade') in opcoes_mod else 0
        f_mod = st.selectbox("Modalidade:", opcoes_mod, index=idx_m)
        
        f_local = st.text_input("Localização (Gaveta/Pasta)", value=aluno_ref.get('localizacao', '')).upper()
        
        # 2. STATUS: Criamos a lista com "" no início
        opcoes_status = ["", "VIVO", "PERMANENTE"]
        
        # Se for edição, identifica se é VIVO (1) ou PERMANENTE (2). Se for novo, é 0 (vazio).
        if editando:
            idx_s = opcoes_status.index(aluno_ref.get('status_arquivo')) if aluno_ref.get('status_arquivo') in opcoes_status else 0
        else:
            idx_s = 0
            
        f_status = st.selectbox("Status", opcoes_status, index=idx_s)

        if st.form_submit_button("Atualizar Dados" if editando else "Salvar no Banco"):
            # 3. VALIDAÇÃO: Impedir de salvar se os campos estiverem vazios
            if f_nome and f_mod != "" and f_status != "":
                dados = {
                    "nome": f_nome, 
                    "nome_mae": f_mae, 
                    "data_nascimento": str(f_nasc) if f_nasc else None,
                    "ultima_modalidade": f_mod, 
                    "localizacao": f_local, 
                    "status_arquivo": f_status
                }
                try:
                    if editando:
                        supabase.table("alunos").update(dados).eq("id", aluno_ref['id']).execute()
                        registrar_log("EDIÇÃO", f_nome)
                        st.session_state.dados_edicao = None
                    else:
                        supabase.table("alunos").insert(dados).execute()
                        registrar_log("CADASTRO", f_nome)
                    
                    st.success("Sucesso!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("O Nome, Modalidade e Status são obrigatórios.")

# --- ABA 3: RELATÓRIOS ---
with aba_relatorio:
    st.subheader("Estatísticas do Acervo")
    res_rel = supabase.table("alunos").select("status_arquivo, ultima_modalidade").execute()
    
    if res_rel.data:
        df = pd.DataFrame(res_rel.data)
        
        # Criamos 3 colunas em vez de 2 para acomodar a nova métrica
        c_r1, c_r2, c_r3 = st.columns(3)
        
        c_r1.metric("Total de Alunos", len(df))
        c_r2.metric("Arquivos Vivos", len(df[df['status_arquivo'] == 'VIVO']))
        
        # Nova métrica para Arquivos Permanentes
        c_r3.metric("Arquivos Permanentes", len(df[df['status_arquivo'] == 'PERMANENTE']))
        
        st.markdown("---")
        st.write("### Distribuição por Modalidade")
        st.bar_chart(df['ultima_modalidade'].value_counts())
    else:
        st.info("Sem dados para exibir.")