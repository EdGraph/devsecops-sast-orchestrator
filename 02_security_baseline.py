import os
import subprocess
import requests
import io
import time
import re
import csv
import shutil

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# --- CONFIGURAÇÕES DE TELEMETRIA E AUTENTICAÇÃO CLOUD ---
SONAR_URL = "https://sonarcloud.io"
SONAR_TOKEN = "secret" 
SONAR_ORG = "secret"

SCOPES = ['https://googleapis.com']
ID_PASTA_EDUARDO = "secret"

PASTAS_FUNCOES = [
    "FuncaoCritica_1(Confidencialidade)", 
    "FuncaoCritica_2(Integridade)", 
    "FuncaoCritica_3(Disponiblidade)"
]

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

def listar_arquivos_php(pasta_id):
    """Varre o diretório do Drive filtrando por scripts PHP ativos."""
    query = f"'{pasta_id}' in parents and name contains '.php' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id, name)").execute()
    return resultados.get('files', [])

# --- ENGINE DE ANÁLISE DE ESTADO INICIAL (BASELINE) ---

def executar_analise_src(id_arquivo, nome_arquivo, funcao):
    """
    Estabelece a linha de base de segurança injetando e isolando o código legado 
    original no workspace, disparando o Sonar-Scanner e gerando o relatório inicial.
    """
    print(f"\n[+] ANALISANDO ARQUIVO ORIGINAL: {nome_arquivo} da {funcao}")
    
    pasta_temp = f"./workspace_baseline/{funcao}/src"
    
    # Garantia de isolamento: Purga resíduos de execuções anteriores no workspace
    if os.path.exists(pasta_temp):
        shutil.rmtree(pasta_temp)

    os.makedirs(pasta_temp, exist_ok=True)
    caminho_local = os.path.join(pasta_temp, nome_arquivo)
    
    request = service.files().get_media(fileId=id_arquivo)
    with io.FileIO(caminho_local, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
            
    # Lógica Defensiva/Segurança: Higienização de parâmetros de CLI via Regex (Prevenção de Command Injection)
    project_key_raw = f"baseline_src3_{funcao.split('(')}"
    project_key = re.sub(r'[^a-zA-Z0-9\-_.]', '_', project_key_raw)
    
    comando_scanner = [
        "sonar-scanner",
        f"-Dsonar.organization={SONAR_ORG}",
        f"-Dsonar.projectKey={project_key}",
        f"-Dsonar.sources={pasta_temp}",
        f"-Dsonar.host.url={SONAR_URL}",
        f"-Dsonar.token={SONAR_TOKEN}",
        "-Dsonar.scm.disabled=true"
    ]
    
    print("      -> Rodando varredura na nuvem...")
    resultado = subprocess.run(comando_scanner, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print("      [!] ERRO FATAL DO SCANNER. Verifique o console.")
        print(resultado.stderr)
        return
        
    # Janela de compensação temporal para consistência eventual das métricas na API cloud
    print("      -> Scanner finalizado. Aguardando a nuvem (20s)...")
    time.sleep(20) 
    
    # Consumo de Endpoints REST: Coleta de métricas qualitativas para fins comparativos
    url_api = f"{SONAR_URL}/api/measures/component"
    parametros = {
        "component": project_key,
        "metricKeys": "bugs,vulnerabilities,security_hotspots,code_smells,blocker_violations,critical_violations"
    }
    
    resposta = requests.get(url_api, params=parametros, auth=(SONAR_TOKEN, ""))
    
    if resposta.status_code == 200:
        medidas = resposta.json().get('component', {}).get('measures', [])
        metricas = {m['metric']: m['value'] for m in medidas}
        
        print("      === RESULTADOS DA LINHA DE BASE ===")
        print(f"      Vulnerabilidades Clássicas: {metricas.get('vulnerabilities', '0')}")
        print(f"      Security Hotspots:          {metricas.get('security_hotspots', '0')}")
        print(f"      Bugs Totais:                {metricas.get('bugs', '0')}")
        print(f"      Falhas Blocker (Críticas):  {metricas.get('blocker_violations', '0')}")
        print(f"      Falhas Altas (Critical):    {metricas.get('critical_violations', '0')}")
        print("      ===================================")

        # Persistência histórica e incremental dos metadados da linha de base
        arquivo_csv = 'resultados_baseline.csv'
        cabecalho = ['Funcao', 'Arquivo', 'Vulnerabilidades', 'Security_Hotspots', 'Bugs', 'Blockers', 'Criticals']
        arquivo_existe = os.path.isfile(arquivo_csv)
        
        with open(arquivo_csv, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not arquivo_existe:
                writer.writerow(cabecalho)
                
            writer.writerow([
                funcao,
                nome_arquivo,
                metricas.get('vulnerabilities', '0'),
                metricas.get('security_hotspots', '0'),
                metricas.get('bugs', '0'),
                metricas.get('blocker_violations', '0'),
                metricas.get('critical_violations', '0')
            ])
        print(f"      [v] Resultados salvos no CSV: {arquivo_csv}")
    else:
        print(f"      [!] Erro ao buscar métricas: HTTP {resposta.status_code}")

# --- PIPELINE PRINCIPAL DE ORQUESTRAÇÃO DE BASELINE ---
print("=== Teste de Baseline (Apenas pasta SRC) no SonarCloud ===")

id_projeto_1 = buscar_subpasta_por_nome(ID_PASTA_EDUARDO, "Projeto_2")
if not id_projeto_1:
    print("Erro: Pasta 'Projeto_2' não encontrada na Web.")
    exit()

for funcao in PASTAS_FUNCOES:
    id_funcao = buscar_subpasta_por_nome(id_projeto_1, funcao)
    if not id_funcao: continue
    
    id_src = buscar_subpasta_por_nome(id_funcao, "src")
    if id_src:
        arquivos_php = listar_arquivos_php(id_src)
        if arquivos_php:
            arquivo_alvo = arquivos_php
            executar_analise_src(arquivo_alvo['id'], arquivo_alvo['name'], funcao)
        else:
            print(f"\n[-] Nenhum arquivo .php encontrado na pasta src de {funcao}")
