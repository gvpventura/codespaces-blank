import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, date
import time
import unicodedata

# --- FUNÇÕES DE APOIO ---
def remover_acentos(texto):
    if not texto:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper().strip()

@st.cache_data(ttl=300)
def buscar_lista_nomes():
    try:
        res = supabase.table("alunos").select("nome").order("nome").execute()
        return [aluno['nome'] for aluno in res.data] if res.data else []
    except:
        return []

def registrar_log(acao, aluno, detalhes=""):
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

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Facility - Gestão", layout="centered")

# --- LIMPEZA TOTAL E DEFINITIVA DA INTERFACE ---
st.markdown("""
    <style>
    /* Esconde a barra de ferramentas superior e rodapé padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* REMOVE A BARRA INFERIOR DIREITA (Manage App / Ferramentas da Nuvem) */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* ESCONDE O BOTÃO DE DEPLOY/SHARE QUE PODE SOBRAR */
    .stAppDeployButton {
        display: none !important;
    }

    /* REMOVE O ESPAÇO EXTRA QUE ESSAS BARRAS OCUPAM */
    .stAppViewBlockContainer {
        padding-bottom: 0px !important;
    }
    
    /* TIRA O FOCO DO BOTÃO FLUTUANTE QUE APARECE AO PASSAR O MOUSE */
    button[title="View profile"], 
    button[aria-label="Manage app"],
    [data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Coloque isso logo abaixo do st.set_page_config
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #stDecoration {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Conexão
URL = "https://ihcrndrwarcywiixypyp.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloY3JuZHJ3YXJjeXdpaXh5cHlwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDMxMTcsImV4cCI6MjA4MjY3OTExN30.58Wd3azYScFkCW0VGkxhvZfgjFYPQgpdzypkoIIuFI4"
supabase = create_client(URL, KEY)

# --- ESTADOS DO SISTEMA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""
if "dados_edicao" not in st.session_state:
    st.session_state.dados_edicao = None
if "pagina_ativa" not in st.session_state:
    st.session_state.pagina_ativa = "🔍 Consulta"

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try:
            st.image("logo.png", width=250)
        except:
            st.title("Facility Soluções")
            
        st.markdown("### 🔒 Acesso Restrito")
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário")
            senha = st.text_input("🔑 Senha", type="password")
            entrar = st.form_submit_button("Acessar Sistema", type="primary")

            if entrar:
                res_user = supabase.table("usuarios").select("nome").eq("login", usuario).eq("senha", senha).execute()
                if res_user.data:
                    st.session_state.autenticado = True
                    st.session_state.nome_usuario = res_user.data[0]['nome']
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
    st.stop()

# --- SISTEMA PRINCIPAL (SIDEBAR) ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.title("Facility Soluções")
    st.markdown("---")
    st.markdown(f"### 👤 Usuário\n**{st.session_state.nome_usuario}**")
    if st.button("🚪 Encerrar Sessão", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.nome_usuario = ""
        st.rerun()

# --- NAVEGAÇÃO ---
st.title("📂 Gestão de Prontuários")
c_m1, c_m2, c_m3 = st.columns(3)
if c_m1.button("🔍 Consulta", use_container_width=True): 
    st.session_state.pagina_ativa = "🔍 Consulta"; st.rerun()
if c_m2.button("➕ Novo/Editar", use_container_width=True): 
    st.session_state.pagina_ativa = "➕ Novo/Editar"; st.rerun()
if c_m3.button("📊 Relatórios", use_container_width=True): 
    st.session_state.pagina_ativa = "📊 Relatórios"; st.rerun()

st.markdown("---")

# --- PÁGINA 1: CONSULTA ---
# --- PÁGINA 1: CONSULTA ---
if st.session_state.pagina_ativa == "🔍 Consulta":
    # 1. Crie o espaço reservado
    espaco_busca = st.empty()
    
    # 2. Se a variável de reset não existir, inicializa
    if "reset_busca" not in st.session_state: 
        st.session_state.reset_busca = 0

    # 3. Faz a busca silenciosamente (o usuário não verá o nome da função)
    lista_nomes = buscar_lista_nomes()

    # 4. Preenche o espaço reservado de uma vez só
    with espaco_busca.container():
        st.subheader("🔍 Busca Rápida")
        escolha = st.selectbox(
            "Pesquise o aluno:", 
            options=[""] + lista_nomes, 
            key=f"busca_{st.session_state.reset_busca}"
        )
            
            with col_msg: st.success("✅ Registro Localizado!")
            with col_edit:
                if st.button("📝 Editar", use_container_width=True):
                    st.session_state.dados_edicao = aluno
                    st.session_state.pagina_ativa = "➕ Novo/Editar"
                    st.rerun()
            with col_del:
                if st.button("🗑️ Excluir", use_container_width=True):
                    st.session_state.confirmar_exclusao_id = aluno['id']
            with col_clear:
                if st.button("🧹 Limpar", use_container_width=True):
                    st.session_state.reset_busca += 1
                    st.session_state.dados_edicao = None
                    st.rerun()

            if "confirmar_exclusao_id" in st.session_state and st.session_state.confirmar_exclusao_id == aluno['id']:
                st.warning(f"⚠️ Confirmar exclusão de {aluno['nome']}?")
                cs, cn = st.columns(2)
                if cs.button("✔️ SIM, EXCLUIR", type="primary"):
                    supabase.table("alunos").delete().eq("id", aluno['id']).execute()
                    st.session_state.reset_busca += 1
                    del st.session_state.confirmar_exclusao_id
                    st.rerun()
                if cn.button("✖️ NÃO"): 
                    del st.session_state.confirmar_exclusao_id
                    st.rerun()

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"👩 **Mãe:** {aluno.get('nome_mae', '-')}")
                dt_b = aluno.get('data_nascimento')
                dt_exibir = datetime.strptime(dt_b, '%Y-%m-%d').strftime('%d/%m/%Y') if dt_b else "-"
                st.write(f"📅 **Data Nasc.:** {dt_exibir}")
            with c2:
                loc = aluno.get('localizacao', '-')
                st.markdown(f'<div style="background-color:#f8f9fa;padding:15px;border-radius:10px;border-left:6px solid #d9534f;"><b>📍 LOCALIZAÇÃO:</b><br><span style="color:#d9534f;font-size:26px;font-weight:bold;">{loc}</span></div>', unsafe_allow_html=True)
                st.write(f"🎓 **Modalidade:** {aluno.get('ultima_modalidade', '-')}")
                st.write(f"📌 **Status:** {aluno.get('status_arquivo', '-')}")

# --- PÁGINA 2: NOVO/EDITAR ---
elif st.session_state.pagina_ativa == "➕ Novo/Editar":
    editando = st.session_state.dados_edicao is not None
    st.subheader("📝 Editar Registro" if editando else "➕ Cadastrar Novo Aluno")
    aluno_ref = st.session_state.dados_edicao if editando else {}

    if editando and aluno_ref.get('data_nascimento'):
        try: 
            d_padrao = datetime.strptime(aluno_ref['data_nascimento'], '%Y-%m-%d').date()
        except: 
            d_padrao = None
    else: 
        d_padrao = None 

    with st.form("form_unico", clear_on_submit=not editando):
        f_nome = st.text_input("Nome Completo", value=aluno_ref.get('nome', '')).upper()
        f_mae = st.text_input("Nome da Mãe", value=aluno_ref.get('nome_mae', '')).upper()
        
        f_nasc = st.date_input(
            "Data de Nascimento", 
            value=d_padrao, 
            min_value=date(1920, 1, 1), 
            max_value=date.today(),
            format="DD/MM/YYYY"
        )
        
        opcoes_mod = ["", "ENSINO FUNDAMENTAL - REGULAR", "ENSINO MEDIO - REGULAR", "PROFISSIONALIZANTE", "CURSO TECNICO", "EJA-ENS. FUNDAMENTAL", "EJA-ENS. MEDIO", "OUTROS"]
        idx_m = opcoes_mod.index(aluno_ref['ultima_modalidade']) if editando and aluno_ref.get('ultima_modalidade') in opcoes_mod else 0
        f_mod = st.selectbox("Modalidade:", opcoes_mod, index=idx_m)
        
        f_local = st.text_input("Localização (Gaveta/Pasta)", value=aluno_ref.get('localizacao', '')).upper()
        
        opcoes_status = ["", "VIVO", "PERMANENTE"]
        idx_s = opcoes_status.index(aluno_ref.get('status_arquivo')) if editando and aluno_ref.get('status_arquivo') in opcoes_status else 0
        f_status = st.selectbox("Status", opcoes_status, index=idx_s)

        enviar = st.form_submit_button("💾 Atualizar Dados" if editando else "💾 Salvar no Banco")

        if enviar:
            # Validação rigorosa de todos os campos
            if f_nome and f_mae and f_nasc is not None and f_mod != "" and f_local and f_status != "":
                dados = {
                    "nome": remover_acentos(f_nome),
                    "nome_mae": remover_acentos(f_mae),
                    "data_nascimento": str(f_nasc),
                    "ultima_modalidade": f_mod,
                    "localizacao": remover_acentos(f_local),
                    "status_arquivo": f_status
                }
                
                try:
                    if editando:
                        supabase.table("alunos").update(dados).eq("id", aluno_ref.get('id')).execute()
                        registrar_log("EDIÇÃO", f_nome)
                        st.session_state.dados_edicao = None
                    else:
                        supabase.table("alunos").insert(dados).execute()
                        registrar_log("CADASTRO", f_nome)
                    
                    # --- ESSA É A LINHA QUE RESOLVE O PROBLEMA ---
                    st.cache_data.clear() # Limpa a memória para buscar a lista atualizada
                    
                    st.success("✅ Salvo com sucesso!")
                    st.session_state.pagina_ativa = "🔍 Consulta"
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro no banco: {e}")
            else:
                st.error("🚨 ERRO: Todos os campos (Nome, Mãe, Data, Modalidade, Localização e Status) devem estar preenchidos!")

    if st.button("❌ Cancelar Operação", key="btn_cancelar_cadastro"):
        st.session_state.dados_edicao = None
        st.session_state.pagina_ativa = "🔍 Consulta"
        st.rerun()

# --- PÁGINA 3: RELATÓRIOS ---
elif st.session_state.pagina_ativa == "📊 Relatórios":
    st.subheader("📊 Estatísticas do Acervo")
    res_rel = supabase.table("alunos").select("status_arquivo, ultima_modalidade").execute()
   
    if res_rel.data:
        df = pd.DataFrame(res_rel.data)
        c_r1, c_r2, c_r3 = st.columns(3)
        c_r1.metric("Total de Alunos", len(df))
        c_r2.metric("📁 Arquivos Vivos", len(df[df['status_arquivo'] == 'VIVO']))
        c_r3.metric("🗄️ Arquivos Permanentes", len(df[df['status_arquivo'] == 'PERMANENTE']))
       
        st.markdown("---")
        st.write("### 📈 Distribuição por Modalidade")
        st.bar_chart(df['ultima_modalidade'].value_counts())
    else:
        st.info("Nenhum registro encontrado no banco de dados.")