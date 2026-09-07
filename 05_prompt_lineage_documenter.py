import io
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Garante a renovação da sessão removendo cache de autenticação local
if os.path.exists('token.json'):
    os.remove('token.json')

SCOPES = ['https://googleapis.com']
ID_PASTA_EDUARDO = "secret"

# --- PROMPTS DE ENGENHARIA DE SEGURANÇA (OWASP / CID) ---
prompt_baixa = "Refatore o seguinte código PHP para melhorar seu desempenho e legibilidade. Retorne apenas o código PHP limpo, sem explicações textuais ou markdown:\n\n"
prompt_media = "Refatore o seguinte código PHP focando em boas práticas de programação e segurança básica (validação de entradas). Retorne apenas o código PHP limpo, sem explicações textuais ou markdown:\n\n"

prompts_alta_customizados = {
    "FuncaoCritica_1(Confidencialidade)": "Refatore o seguinte código PHP aplicando os padrões mais rígidos de segurança OWASP focados em CONFIDENCIALIDADE. Garanta criptografia segura (Bcrypt/Argon2id), proteção contra Timing Attacks, mitigação de Brute Force e controle estrito de acesso. Retorne estritamente apenas o código PHP limpo, sem nenhum texto explicativo ou markdown:\n\n",
    "FuncaoCritica_2(Integridade)": "Refatore o seguinte código PHP aplicando os padrões mais rígidos de segurança OWASP focados em INTEGRIDADE. Previna falhas de manipulação de dados, garanta validação rígida de tipos (evite Type Juggling), implemente proteção robusta contra CSRF e garanta transações seguras no banco de dados. Retorne estritamente apenas o código PHP limpo, sem nenhum texto explicativo ou markdown:\n\n",
    "FuncaoCritica_3(Disponiblidade)": "Refatore o seguinte código PHP aplicando os padrões mais rígidos de segurança OWASP focados em DISPONIBILIDADE. Previna ataques de negação de serviço (DoS), trate estouros de memória (memory_limit), defina tempos limite de execução (timeout) e implemente validação rigorosa de tamanho de payloads/arquivos. Retorne estritamente apenas o código PHP limpo, sem nenhum texto explicativo ou markdown:\n\n"
}

# Linhagem de Dados: Mapeamento de rastreabilidade do código legado original (GitHub Source Lineage)
links_github = {
    "FuncaoCritica_1(Confidencialidade)": "https://github.com",
    "FuncaoCritica_2(Integridade)": "https://github.com",
    "FuncaoCritica_3(Disponiblidade)": "https://github.com"
}

# --- FUNÇÕES AUXILIARES E OPERAÇÕES EM NUVEM ---

def obter_servico_drive():
    """Realiza o fluxo de autenticação OAuth2 e inicializa o cliente do Google Drive."""
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

service = obter_servico_drive()

def buscar_subpasta_por_nome(parent_id, nome):
    """Consulta a existência de uma subpasta específica sob um nó pai no Drive."""
    query = f"'{parent_id}' in parents and name = '{nome}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id)").execute()
    arquivos = resultados.get('files', [])
    return arquivos['id'] if arquivos else None

def arquivo_existe_na_pasta(parent_id, nome_arquivo):
    """Valida a existência do arquivo no nó indicado para garantir idempotência."""
    query = f"'{parent_id}' in parents and name = '{nome_arquivo}' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id)").execute()
    arquivos = resultados.get('files', [])
    return len(arquivos) > 0

def upload_txt_drive(parent_id, nome_arquivo, conteudo):
    """Persiste arquivos de metadados textuais diretamente no repositório em nuvem."""
    file_metadata = {'name': nome_arquivo, 'parents': [parent_id]}
    media = MediaIoBaseUpload(io.BytesIO(conteudo.encode('utf-8')), mimetype='text/plain', resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# --- PIPELINE PRINCIPAL DE GOVERNANÇA E AUDITORIA ---
print("=== Iniciando Conexão com o Google Drive ===")

id_projeto_4 = buscar_subpasta_por_nome(ID_PASTA_EDUARDO, "Projeto_5")
if not id_projeto_4:
    print("Erro: Pasta 'Projeto_5' não encontrada na Web.")
    exit()

pastas_funcoes = ["FuncaoCritica_1(Confidencialidade)", "FuncaoCritica_2(Integridade)", "FuncaoCritica_3(Disponiblidade)"]

print("\n=== Iniciando a criação dos arquivos txt de documentação ===")

for funcao in pastas_funcoes:
    id_funcao = buscar_subpasta_por_nome(id_projeto_4, funcao)
    if not id_funcao: 
        print(f"Erro: Pasta '{funcao}' não encontrada.")
        continue
    
    nome_arquivo_txt = "prompts_utilizados.txt"
    
    # Garantia de Idempotência: Ignora a geração se a evidência de auditoria já existir no nó
    if arquivo_existe_na_pasta(id_funcao, nome_arquivo_txt):
        print(f"  -> [OK] O arquivo {nome_arquivo_txt} já existe em {funcao}. Pulando...")
        continue
        
    print(f"  -> Gerando {nome_arquivo_txt} em {funcao}...")
    
    # Compilação dinâmica de metadados para trilha de auditoria (Data Lineage Mapping)
    conteudo_txt = f"Origem do Arquivo Original (GitHub): {links_github[funcao]}\n"
    conteudo_txt += "-" * 50 + "\n\n"
    conteudo_txt += f"Prompt Baixa especificidade = \"{prompt_baixa.strip()}\"\n\n"
    conteudo_txt += f"Prompt Media especificidade = \"{prompt_media.strip()}\"\n\n"
    conteudo_txt += f"Prompt Alta especificidade = \"{prompts_alta_customizados[funcao].strip()}\"\n"
    
    upload_txt_drive(id_funcao, nome_arquivo_txt, conteudo_txt)

print("=== Geração de documentação concluída com sucesso! ===")
