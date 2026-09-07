import os
import subprocess
import requests
import csv
import io
import time
import shutil
import re
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
NIVEIS = ["Baixa", "Media", "Alta"]
TENTATIVAS = ["Tentativa_1", "Tentativa_2", "Tentativa_3"]

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
    return arquivos[0]['id'] if arquivos else None

def listar_arquivos_php(pasta_id):
    """Varre o diretório do Drive filtrando por scripts PHP ativos."""
    query = f"'{pasta_id}' in parents and name contains '.php' and trashed = false"
    resultados = service.files().list(q=query, fields="files(id, name)").execute()
    return resultados.get('files', [])

# --- CORE ENGINE: EXECUÇÃO SAST E MINERAÇÃO DE DADOS ---

def executar_analise(id_arquivo, nome_arquivo, funcao, nivel, tentativa, writer):
    """
    Isola o código-fonte em um workspace temporário, orquestra a execução da CLI do
    Sonar-Scanner na nuvem e consome APIs REST para extrair métricas de qualidade e CWEs.
    """
    print(f"    [+] PROCESSANDO: {nome_arquivo} ({nivel} - {tentativa})")
    
    pasta_temp = f"./workspace_sonar/{funcao}/{nivel}/{tentativa}"
    
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
            status, done = downloader.next_chunk()
            
    # Lógica Defensiva/Segurança: Higienização de parâmetros de CLI via Regex (Prevenção de Command Injection)
    project_key_raw = f"Proj4_{funcao.split('(')[0]}_{nivel}_{tentativa}"
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
    
    print("      -> Rodando varredura de segurança na nuvem...")
    resultado = subprocess.run(comando_scanner, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print(f"      [!] ERRO FATAL DO SCANNER. Detalhes:\n")
        print(resultado.stderr)
        print(resultado.stdout)
        return
        
    # Janela de compensação temporal para consistência eventual das métricas na API cloud
    print("      -> Scanner finalizado. Aguardando processamento da nuvem (20s)...")
    time.sleep(20)
    
    # Consumo de Endpoints REST: Coleta de métricas qualitativas de Qualidade e Segurança
    url_api = f"{SONAR_URL}/api/measures/component"
    parametros = {
        "component": project_key,
        "metricKeys": "bugs,vulnerabilities,security_hotspots,code_smells,blocker_violations,critical_violations,major_violations,minor_violations,info_violations,sqale_index,cognitive_complexity,ncloc,duplicated_lines_density,security_rating,reliability_rating,sqale_rating"
    }
    
    resposta = requests.get(url_api, params=parametros, auth=(SONAR_TOKEN, ""))
    
    if resposta.status_code == 200:
        medidas = resposta.json().get('component', {}).get('measures', [])
        metricas = {m['metric']: m['value'] for m in medidas}
        
        bugs = metricas.get('bugs', '0')
        vulns = metricas.get('vulnerabilities', '0')
        hotspots = metricas.get('security_hotspots', '0')
        smells = metricas.get('code_smells', '0')

        blocker = metricas.get('blocker_violations', '0')
        critical = metricas.get('critical_violations', '0')
        major = metricas.get('major_violations', '0')
        minor = metricas.get('minor_violations', '0')
        info = metricas.get('info_violations', '0')
        
        tech_debt = metricas.get('sqale_index', '0') 
        complexidade = metricas.get('cognitive_complexity', '0')
        linhas = metricas.get('ncloc', '0')
        duplicacao = metricas.get('duplicated_lines_density', '0')
        
        sec_rating = metricas.get('security_rating', '0')
        rel_rating = metricas.get('reliability_rating', '0')
        maint_rating = metricas.get('sqale_rating', '0')

        # Data Mining: Mineração e agrupamento de vulnerabilidades por identificadores CWE (via Facets)
        url_issues = f"{SONAR_URL}/api/issues/search"
        parametros_issues = {
            "componentKeys": project_key,
            "resolved": "false",
            "facets": "cwe", 
            "ps": 1 
        }
        
        resposta_issues = requests.get(url_issues, params=parametros_issues, auth=(SONAR_TOKEN, ""))
        lista_cwes = [] 
        
        if resposta_issues.status_code == 200:
            facets = resposta_issues.json().get('facets', [])
            for facet in facets:
                if facet.get('property') == 'cwe':
                    for valor in facet.get('values', []):
                        if valor.get('count', 0) > 0:
                            cwe_val = str(valor.get('val'))
                            if not cwe_val.upper().startswith("CWE-"):
                                cwe_val = f"CWE-{cwe_val}"
                            lista_cwes.append(cwe_val.upper())
        
        cwes_str = ", ".join(lista_cwes) if lista_cwes else "Nenhum"
        print(f"      -> [SUCESSO] Vulns: {vulns} | Blocker: {blocker} | CWEs: {cwes_str}")
        
        # Persistência estruturada dos resultados analíticos
        writer.writerow([
            funcao, nivel, tentativa, nome_arquivo, 
            bugs, vulns, hotspots, smells, 
            blocker, critical, major, minor, info,
            linhas, complexidade, tech_debt, duplicacao,
            sec_rating, rel_rating, maint_rating, cwes_str
        ])
    else:
        print(f"      -> [!] Erro ao buscar métricas: HTTP {resposta.status_code} - {resposta.text}")

# --- PIPELINE PRINCIPAL DE ORQUESTRAÇÃO SAST ---
print("=== Iniciando Pipeline de Análise Estática (SAST) no SonarCloud ===")

id_projeto_2 = buscar_subpasta_por_nome(ID_PASTA_EDUARDO, "Projeto_4")

arquivo_csv = 'resultados_pesquisa_sast.csv'
with open(arquivo_csv, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([
        'Funcao_Critica', 'Nivel_Refatoracao', 'Tentativa', 'Arquivo', 
        'Bugs', 'Vulnerabilidades', 'Security_Hotspots', 'Code_Smells',
        'Blocker', 'Critical/Alta', 'Major/Media', 'Minor/Baixa', 'Info',
        'Linhas_Codigo', 'Complexidade', 'Divida_Tecnica_Minutos', 'Duplicacao_Pct',
        'Nota_Seguranca', 'Nota_Confiabilidade', 'Nota_Mantibilidade', 'CWEs_Encontrados'
    ])

    for funcao in PASTAS_FUNCOES:
        id_funcao = buscar_subpasta_por_nome(id_projeto_2, funcao)
        if not id_funcao: continue
        print(f"\n[OK] Entrou na pasta '{funcao}'")
        
        id_src = buscar_subpasta_por_nome(id_funcao, "src")
        if id_src:
            arquivos_php = listar_arquivos_php(id_src)
            if arquivos_php:
                arquivo_alvo = arquivos_php[0]
                executar_analise(arquivo_alvo['id'], arquivo_alvo['name'], funcao, "Original(src)", "Original", writer)
            else:
                print("  [-] Nenhum .php encontrado na pasta src")
                
        for nivel in NIVEIS:
            id_nivel = buscar_subpasta_por_nome(id_funcao, nivel)
            if not id_nivel: continue
            
            for tentativa in TENTATIVAS:
                id_tentativa = buscar_subpasta_por_nome(id_nivel, tentativa)
                if not id_tentativa: continue
                
                arquivos_php = listar_arquivos_php(id_tentativa)
                if arquivos_php:
                    arquivo_alvo = arquivos_php[0]
                    executar_analise(arquivo_alvo['id'], arquivo_alvo['name'], funcao, nivel, tentativa, writer)
                else:
                    print(f"  [-] Nenhum .php encontrado em {nivel}/{tentativa}")

print(f"\n=== Análise Concluída! Verifique o arquivo {arquivo_csv} ===")
