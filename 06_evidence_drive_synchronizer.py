import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://googleapis.com']
ID_PASTA_EDUARDO = "secret"
NOME_PASTA_RAIZ = "Projeto_5"

def obter_servico_drive():
    """Realiza o fluxo de autenticação OAuth2 e inicializa o cliente do Google Drive."""
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

service = obter_servico_drive()

def buscar_subpasta_por_nome(parent_id, nome):
    """Consulta a existência de uma subpasta específica sob um nó pai no Drive."""
    query = f"'{parent_id}' in parents and name = '{nome}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = resultados.get('files', [])
    return arquivos[0]['id'] if arquivos else None

def fazer_upload(caminho_arquivo, id_pasta_destino):
    """Executa o upload resiliente (resumable) de artefatos e evidências visuais para a nuvem."""
    nome_arquivo = os.path.basename(caminho_arquivo)
    file_metadata = {
        'name': nome_arquivo,
        'parents': [id_pasta_destino]
    }
    media = MediaFileUpload(caminho_arquivo, resumable=True)
    
    arquivo_enviado = service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id'
    ).execute()
    
    print(f"    [OK] Artefato '{nome_arquivo}' enviado com sucesso!")
    return arquivo_enviado.get('id')

# --- ORQUESTRACÃO DO PIPELINE DE SINCRONIZAÇÃO (TREE WALKING) ---
print(f"=== Iniciando Sincronização Local -> Drive para '{NOME_PASTA_RAIZ}' ===")

id_raiz_drive = buscar_subpasta_por_nome(ID_PASTA_EDUARDO, NOME_PASTA_RAIZ)
if not id_raiz_drive:
    print(f"[-] Erro: Nó raiz '{NOME_PASTA_RAIZ}' não localizado no repositório de destino.")
    exit()

# Mecanismo de Memoization/Caching: Reduz o overhead de I/O de rede mitigando Rate Limiting da API
mapa_pastas = {
    NOME_PASTA_RAIZ: id_raiz_drive
}

# Algoritmo de Tree Walking para mapeamento e reconciliação da topologia de diretórios
for root, dirs, files in os.walk(NOME_PASTA_RAIZ):
    id_pasta_atual_drive = mapa_pastas.get(root)
    
    if not id_pasta_atual_drive:
        continue
        
    print(f"\n[+] Acessando diretório: {root}")
    
    # Varredura horizontal da camada e hidratação dinâmica do cache em memória
    for d in dirs:
        caminho_local_subpasta = os.path.join(root, d)
        id_subpasta_drive = buscar_subpasta_por_nome(id_pasta_atual_drive, d)
        
        if id_subpasta_drive:
            mapa_pastas[caminho_local_subpasta] = id_subpasta_drive
        else:
            print(f"  [!] Aviso: Subpasta '{d}' divergente entre ambiente local e nuvem. Ignorando.")

    # Processamento e persistência das evidências de auditoria SAST
    for f in files:
        if f.startswith('.'): 
            continue
            
        caminho_arquivo = os.path.join(root, f)
        fazer_upload(caminho_arquivo, id_pasta_atual_drive)

print("\n=== Todos os envios foram concluídos! ===")
