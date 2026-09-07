import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
ID_PASTA_EDUARDO = "secret"

# Definição dos parâmetros estruturais da árvore lógica do projeto
PASTAS_FUNCOES = [
    "FuncaoCritica_1(Confidencialidade)", 
    "FuncaoCritica_2(Integridade)", 
    "FuncaoCritica_3(Disponiblidade)"
]
NIVEIS = ["Baixa", "Media", "Alta"]
TENTATIVAS = ["Tentativa_1", "Tentativa_2", "Tentativa_3"]

def obter_servico_drive():
    """Realiza o fluxo de autenticação OAuth2 e inicializa o cliente do Google Drive."""
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

service = obter_servico_drive()

def criar_pasta(nome, parent_id):
    """
    Provisiona um diretório de forma idempotente.
    Verifica preventivamente a existência do nó antes de realizar o disparo de criação.
    """
    query = f"'{parent_id}' in parents and name = '{nome}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id)").execute()
    arquivos = resultados.get('files', [])
    
    # Tratamento preventivo para mitigar duplicidade de volumes (Garantia de Idempotência)
    if arquivos:
        print(f"      [~] Nó de diretório já existente: {nome}")
        return arquivos[0]['id']
    
    metadata = {
        'name': nome,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    pasta = service.files().create(body=metadata, fields='id').execute()
    print(f"      [+] Nó criado com sucesso: {nome}")
    return pasta.get('id')

# --- INICIALIZAÇÃO DA ORQUESTRACÃO IAC ---
print("=== Reconstruindo Estrutura de Pastas ===")

id_projeto = criar_pasta("Projeto_5", ID_PASTA_EDUARDO)

for funcao in PASTAS_FUNCOES:
    print(f"\nMontando hierarquia para: {funcao}")
    id_funcao = criar_pasta(funcao, id_projeto)
    
    # Geração do repositório baseline para código legado
    criar_pasta("src", id_funcao)
    
    # Matriz tridimensional para estruturação dos experimentos de engenharia de prompt
    for nivel in NIVEIS:
        id_nivel = criar_pasta(nivel, id_funcao)
        
        for tentativa in TENTATIVAS:
            criar_pasta(tentativa, id_nivel)

print("\n=== Estrutura de Pastas Reconstruída com Sucesso! ===")
