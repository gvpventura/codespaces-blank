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

# --- ABA 1: CONSULTA (Busca Reativa Total) ---
    with aba_consulta:
        st.subheader("Busca Rápida Facility")
        
        # Usamos um campo de texto simples
        texto_busca = st.text_input("Digite o nome:", key="input_txt").upper()

        if len(texto_busca) >= 3:
            # Buscamos no banco
            res = supabase.table("alunos").select("*").ilike("nome", f"%{texto_busca}%").limit(15).execute()
            
            if res.data:
                # Criamos uma lista de nomes encontrados
                nomes_encontrados = [aluno['nome'] for aluno in res.data]
                
                # O PULO DO GATO: Um seletor que aparece assim que encontra os nomes
                escolha = st.selectbox("Selecione o aluno para ver detalhes:", ["-- Clique aqui --"] + nomes_encontrados)
                
                if escolha != "-- Clique aqui --":
                    # Filtra os dados do aluno escolhido
                    detalhes = next(a for a in res.data if a['nome'] == escolha)
                    st.success(f"✅ Prontuário de {detalhes['nome']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Mãe:** {detalhes.get('nome_mae', '-')}")
                    with col2:
                        st.write(f"**Localização:** {detalhes.get('localizacao', '-')}")
            else:
                st.warning("Nenhum registro com esse nome.")

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