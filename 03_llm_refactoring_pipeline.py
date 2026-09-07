import io
import os
import time
from google import genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Garante a renovação da sessão removendo cache de autenticação local
if os.path.exists('token.json'):
    os.remove('token.json')

SCOPES = ['https://www.googleapis.com/auth/drive']

def obter_servico_drive():
    """Realiza o fluxo de autenticação OAuth2 e inicializa o cliente do Google Drive."""
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

# Inicialização dos clientes de APIs Cloud
service = obter_servico_drive()
client_gemini = genai.Client(api_key="secret")

ID_PASTA_EDUARDO = "secret"
counter = 0

# --- PROMPTS DE ENGENHARIA DE SEGURANÇA (OWASP / CID) ---
prompt_baixa = "Refatore o seguinte código PHP para melhorar seu desempenho e legibilidade. Retorne apenas o código PHP limpo, sem explicações textuais ou markdown:\n\n"
prompt_media = "Refatore o seguinte código PHP focando em boas práticas de programação e segurança básica (validação de entradas). Retorne apenas o código PHP limpo, sem explicações textuais ou markdown:\n\n"

prompts_alta_customizados = {
    "FuncaoCritica_1(Confidencialidade)": "Refatore o seguinte código PHP aplicando os padrões mais rígidos de segurança OWASP focados em CONFIDENCIALIDADE. Garanta criptografia segura (Bcrypt/Argon2id), proteção contra Timing Attacks, mitigação de Brute Force e controle estrito de acesso. Retorne estritamente apenas o código PHP limpo, sem nenhum texto explicativo ou markdown:\n\n",
    "FuncaoCritica_2(Integridade)": "Refatore o seguinte código PHP aplicando os padrões mais rígidos de segurança OWASP focados em INTEGRIDADE. Previna falhas de manipulação de dados, garanta validação rígida de tipos (evite Type Juggling), implemente proteção robusta contra CSRF e garanta transações seguras no banco de dados. Retorne estritamente apenas o código PHP limpo, sem nenhum texto explicativo ou markdown:\n\n",
    "FuncaoCritica_3(Disponiblidade)": "Refatore o seguinte código PHP aplicando os padrões mais rígidos de segurança OWASP focados em DISPONIBILIDADE. Previna ataques de negação de serviço (DoS), trate estouros de memória (memory_limit), defina tempos limite de execução (timeout) e implemente validação rigorosa de tamanho de payloads/arquivos. Retorne estritamente apenas o código PHP limpo, sem nenhum texto explicativo ou markdown:\n\n"
}

# --- FUNÇÕES AUXILIARES E OPERAÇÕES EM NUVEM ---

def buscar_subpasta_por_nome(parent_id, nome):
    """Consulta a existência de uma subpasta específica sob um nó pai no Drive."""
    query = f"'{parent_id}' in parents and name = '{nome}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id)").execute()
    arquivos = resultados.get('files', [])
    return arquivos[0]['id'] if arquivos else None

def buscar_arquivos_php(parent_id):
    """Varre o diretório do Drive filtrando por scripts PHP ativos."""
    query = f"'{parent_id}' in parents and name contains '.php' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id, name)").execute()
    return resultados.get('files', [])

def arquivo_existe_na_pasta(parent_id, nome_arquivo):
    """Valida a existência do arquivo no nó indicado para garantir idempotência."""
    query = f"'{parent_id}' in parents and name = '{nome_arquivo}' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id)").execute()
    arquivos = resultados.get('files', [])
    return len(arquivos) > 0

def baixar_arquivo_drive(file_id):
    """Efetua o download do arquivo em nuvem e decodifica o payload para string UTF-8."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue().decode('utf-8')

def upload_arquivo_drive(parent_id, nome_arquivo, conteudo, max_tentativas=5):
    """Executa upload resiliente (resumable) com lógica de backoff progressivo em caso de falha."""
    file_metadata = {'name': nome_arquivo, 'parents': [parent_id]}
    media = MediaIoBaseUpload(io.BytesIO(conteudo.encode('utf-8')), mimetype='text/x-php', resumable=True)
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"     [V] Upload do arquivo {nome_arquivo} concluído no Drive.")
            return
        except Exception as e:
            print(f"     [!] Erro de conexão no upload do Drive (Tentativa {tentativa}/{max_tentativas}) -> Detalhe: {e}")
            if tentativa < max_tentativas:
                espera = 5 * tentativa
                print(f"     [!] Aguardando {espera} segundos antes de tentar o upload novamente...")
                time.sleep(espera)
            else:
                print(f"     [!] Falha definitiva ao fazer upload do arquivo {nome_arquivo} após {max_tentativas} tentativas.")

# --- PIPELINE PRINCIPAL DE PROCESSAMENTO ---
print("=== Iniciando Conexão com o Google Drive da Web ===")

id_projeto_2 = buscar_subpasta_por_nome(ID_PASTA_EDUARDO, "Projeto_4")
if not id_projeto_2:
    print("Erro: Pasta 'Projeto_4' não encontrada na Web.")
    exit()

pastas_funcoes = ["FuncaoCritica_1(Confidencialidade)", "FuncaoCritica_2(Integridade)", "FuncaoCritica_3(Disponiblidade)"]

for funcao in pastas_funcoes:
    id_funcao = buscar_subpasta_por_nome(id_projeto_2, funcao)
    if not id_funcao: continue
    
    id_src = buscar_subpasta_por_nome(id_funcao, "src")
    if not id_src: continue
    
    arquivos = buscar_arquivos_php(id_src)
    if not arquivos:
        print(f"Aviso: Nenhum arquivo PHP na pasta src de {funcao}")
        continue
        
    arquivo_original = arquivos[0]
    nome_arquivo = arquivo_original['name']
    print(f"\n[+] Processando arquivo Web: {nome_arquivo} em {funcao}")
    
    codigo_original = baixar_arquivo_drive(arquivo_original['id'])
    
    lista_niveis = {
        "Baixa": prompt_baixa,
        "Media": prompt_media,
        "Alta": prompts_alta_customizados[funcao]
    }
    
    for nivel, prompt_texto in lista_niveis.items():
        id_nivel = buscar_subpasta_por_nome(id_funcao, nivel)
        if not id_nivel: continue
        
        # Estratégia FinOps: Seleção dinâmica de modelos baseada em criticidade
        if nivel == "Alta":
            modelo_escolhido = 'gemini-3.1-pro-preview'
            tempo_de_pausa = 3
        else:
            modelo_escolhido = 'gemini-3.1-pro-preview'
            tempo_de_pausa = 3
        
        for tentativa in range(1, 4):
            nome_tentativa = f"Tentativa_{tentativa}"
            id_tentativa = buscar_subpasta_por_nome(id_nivel, nome_tentativa)
            if not id_tentativa: continue
            
            # Verificação preventiva de duplicidade (Garantia de Idempotência)
            if arquivo_existe_na_pasta(id_tentativa, nome_arquivo):
                print(f"  -> [OK] Arquivo já existe em {nome_tentativa}. Pulando...")
                continue 

            print(f"  -> Solicitando {modelo_escolhido} [{nivel}] - {nome_tentativa}...")
            
            sucesso_na_api = False
            tentativas_api = 0
            codigo_refatorado = ""
            
            # Lógica defensiva contra oscilações e Rate Limiting da API LLM
            while not sucesso_na_api and tentativas_api < 5:
                try:
                    resposta = client_gemini.models.generate_content(
                        model=modelo_escolhido, 
                        contents=f"{prompt_texto}{codigo_original}"
                    )
                    codigo_refatorado = resposta.text
                    sucesso_na_api = True
                except Exception as e:
                    tentativas_api += 1
