# DevSecOps Orchestration, SAST Audit, and Self-Healing Framework

## 🎯 About the Project
This tools ecosystem was developed as part of my Graduation Thesis (TCC) at **PUCPR**. The primary objective is to analyze the impact of Large Language Models (LLMs) in mitigating security vulnerabilities within legacy code (PHP), evaluating the effectiveness, compliance, and data lineage across different levels of prompt engineering specificity.

### 💡 Motivation & Platform Engineering Approach
The original academic scope did not require automation. However, aiming for operational efficiency and the feasibility of scaling tests across **multiple simultaneous projects**, the architecture was independently conceived to function as an end-to-end automated data engineering framework. The solution autonomously covers the entire lifecycle of infrastructure provisioning, AI-driven refactoring, Static Application Security Testing (SAST), and governance.

## 🏗️ System Architecture & Modules
The framework is composed of 6 fully integrated Python modules with native support for idempotency:

### 1. Environment Provisioning Module (`01_environment_provisioner.py`)
Focuses on *Infrastructure as Code* (IaC) and *Disaster Recovery*.
- Automates the creation and replication of complex hierarchical directory architectures within Google Drive Cloud.
- Implements built-in defensive logic that checks node existence before execution to prevent volume duplication or logical tree corruption.

### 2. Security Baseline Module (`02_security_baseline.py`)
Establishes the initial risk state (*Security Baseline Testing*).
- Isolates the original legacy source code located in the root folder (`src`), executing isolated cloud-based scans.
- Persists an incremental CSV report (`resultados_baseline.csv`) containing raw original metrics (Bugs, Vulnerabilities, and Hotspots) to enable comparative statistics on mitigation effectiveness.

### 3. Ingestion & Intelligent Refactoring Pipeline (`03_llm_refactoring_pipeline.py`)
Orchestrates code downloads from GitHub and manages secure, dynamic consumption of the **Google Gemini API**.
- Applies three progressive levels of prompt engineering specificity focused on mitigating vulnerabilities within the CIA triad (OWASP).
- Implements intelligent model routing (*FinOps*) based on the complexity of the requested business rule.

### 4. SAST Audit & Mining Engine (`04_sast_audit_engine.py`)
Automates and isolates Static Application Security Testing (SAST) execution on AI-generated code.
- Sanitizes command-line interface (CLI) parameters using regular expressions (**Regex**) to mitigate command injection risks.
- Consumes **SonarCloud REST API** endpoints to extract quality metrics and mine specific Common Weakness Enumeration identifiers (**CWE**), exporting structured CSV reports.

### 5. Data Lineage & Traceability Module (`05_prompt_lineage_documenter.py`)
Ensures IT governance and audit compliance.
- Maps original repository source URLs from GitHub to guarantee software lifecycle traceability (*GitHub Source Lineage*).
- Automatically generates metadata files containing the structured history of prompts utilized for each critical function.

### 6. Evidence Cloud Synchronizer (`06_evidence_drive_synchronizer.py`)
Manages visual reports and dashboard print traffic between the local workspace and the cloud.
- Implements a *Tree Walking* algorithm optimized with in-memory caching via Python dictionaries to reduce API request overhead (*Memoization*).
- Leverages `resumable` uploads to guarantee data streaming resilience against network connection drops.

## 🛡️ Engineering & Resilience Highlights
To ensure data pipeline autonomy during large-scale executions, the system implements rigorous exception handling and fault-tolerance patterns:
*   **Defensive External API Handling:** Manual implementation of control mechanisms and request throttling.
*   **Drop-off Logic (Adapted Circuit Breaker):** The framework monitors the stability of Gemini API responses. If a specific prompt fails consecutively for 5 attempts, the system triggers a drop-off logic (`counter += 1`), skips to the next instruction without breaking the execution flow, and compiles a failure report at runtime termination for manual auditing.

## 🛠️ Tech Stack & Concepts
- **Core Language:** Python 3
- **Cloud APIs:** Google GenAI SDK (Gemini Pro), Google Drive API v3, SonarCloud REST API
- **Security & Quality:** SonarCloud (SAST), OWASP Guidelines, CWE Catalog
- **Engineering Concepts:** Infrastructure as Code (IaC), Disaster Recovery, Idempotency, Progressive Backoff, Caching (Memoization), and FinOps.

---

## 🚀 Getting Started

### Prerequisites
Before running the pipeline, ensure you have **Python 3.10+** installed along with the required cloud credentials:
1. A Google Cloud Project with the **Google Drive API v3** enabled. Download your OAuth2 credentials file and save it as `credentials.json` in the root folder.
2. A **SonarCloud Token** and your **Organization Key** generated from your SonarCloud account.
3. A **Google Gemini API Key** configured in your environment variables or credentials manager.

### Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com
cd devsecops-sast-orchestrator
pip install -r requirements.txt
```

*Note: Ensure your `requirements.txt` contains: `google-genai`, `google-auth-oauthlib`, `google-api-python-client`, and `requests`.*

### Execution Order
Run the modules sequentially to complete the data engineering and DevSecOps pipeline:

```bash
# 1. Provision the Google Drive cloud directory structure
python 01_environment_provisioner.py

# 2. Establish the security baseline metrics for the legacy code
python 02_security_baseline.py

# 3. Execute the AI refactoring pipeline using Gemini Pro
python 03_llm_refactoring_pipeline.py

# 4. Trigger SAST auditing and extract data mining reports (CSV/CWEs)
python 04_sast_audit_engine.py

# 5. Document prompt engineering metadata and source data lineage
python 05_prompt_lineage_documenter.py

# 6. Synchronize local evidence and dashboard captures back to Cloud Storage
python 06_evidence_drive_synchronizer.py
```


# Framework de Orquestração, Auditoria SAST e Auto-recuperação DevSecOps

## 🎯 Sobre o Projeto
Este ecossistema de ferramentas foi desenvolvido como parte do meu Trabalho de Conclusão de Curso (TCC) na **PUCPR**. O objetivo principal é analisar o impacto do uso de Modelos de Linguagem Larga (LLMs) na mitigação de vulnerabilidades de segurança em códigos legados (PHP), avaliando a eficácia, conformidade e rastreabilidade de diferentes níveis de engenharia de prompt.

### 💡 Motivação e Engenharia de Plataforma
O escopo acadêmico original não exigia automação. Contudo, visando a eficiência operacional e a viabilidade de escalar os testes para **múltiplos projetos simultâneos**, a arquitetura foi concebida por iniciativa própria para funcionar como um framework automatizado de engenharia de dados de ponta a ponta. A solução cobre de forma autônoma todo o ciclo de provisionamento, refatoração com IA, análise estática de segurança (SAST) e governança.

## 🏗️ Arquitetura e Módulos do Sistema
O framework é composto por 6 módulos em Python totalmente integrados e com suporte nativo à idempotência:

### 1. Módulo de Provisionamento de Ambiente (`01_environment_provisioner.py`)
Módulo focado em *Infrastructure as Code* (IaC) e *Disaster Recovery*. 
- Automatiza a criação e a replicação de arquiteturas hierárquicas complexas de diretórios no Google Drive Cloud.
- Possui lógica defensiva integrada que consulta a existência de nós antes da criação para evitar duplicidade de volumes ou corrupção da árvore lógica.

### 2. Módulo de Linha de Base de Segurança (`02_security_baseline.py`)
Módulo voltado para o estabelecimento do estado de criticidade inicial (*Security Baseline Testing*).
- Isola o código-fonte legado original contido na pasta raiz (`src`), executando varreduras isoladas na nuvem.
- Persiste um relatório incremental em formato CSV (`resultados_baseline.csv`) contendo as métricas brutas originais (Bugs, Vulnerabilidades e Hotspots) para viabilizar cálculos comparativos de eficácia estatística.

### 3. Módulo de Ingestão e Refatoração Inteligente (`03_llm_refactoring_pipeline.py`)
Orquestra o download de códigos do GitHub e gerencia o consumo dinâmico e seguro da **API do Google Gemini**.
- Aplica três níveis progressivos de especificidade de prompts focados em mitigar vulnerabilidades da tríade CID (OWASP).
- Implementa roteamento inteligente de modelos (*FinOps*) baseado na complexidade da regra de negócio solicitada.

### 4. Módulo de Auditoria e Mineração SAST (`04_sast_audit_engine.py`)
Automatiza e isola a execução de testes estáticos de segurança (SAST) em códigos gerados por IA.
- Higieniza parâmetros de linha de comando por meio de expressões regulares (**Regex**).
- Consome endpoints de **APIs REST do SonarCloud** para extrair métricas de qualidade e minerar identificadores específicos de falhas (**CWE**), exportando relatórios em CSV.

### 5. Módulo de Linhagem de Dados e Rastreabilidade (`05_prompt_lineage_documenter.py`)
Garante a governança e o compliance de auditoria.
- Mapeia as URLs de origem originais dos repositórios do GitHub para garantir a rastreabilidade do ciclo de vida do software (*GitHub Source Lineage*).
- Gera automaticamente arquivos de metadados textuais contendo o histórico estruturado dos prompts utilizados para cada função crítica.

### 6. Módulo de Sincronização de Evidências (`06_evidence_drive_synchronizer.py`)
Gerencia o tráfego de relatórios visuais entre o ambiente local e a nuvem.
- Implementa algoritmo de *Tree Walking* com cache em memória via dicionários Python para mitigar o consumo de taxas de requisição das APIs (*Memoization*).
- Utiliza uploads do tipo `resumable` para garantir resiliência contra oscilações de conexão de rede.


## 🛡️ Destaques de Engenharia & Resiliência
Para garantir a autonomia do pipeline de dados em execuções de larga escala, o sistema implementa lógicas rigorosas de tratamento de exceções e tolerância a falhas:
*   **Tratamento Defensivo de APIs Extensivas:** Implementação manual de mecanismos de controle e descarte de requisições. 
*   **Lógica de Desistência (Circuit Breaker adaptado):** O framework monitora a estabilidade das respostas da API do Gemini. Caso um prompt específico falhe consecutivamente por 5 tentativas, o sistema aciona uma lógica de descarte (`counter += 1`), pula para a próxima instrução sem corromper o fluxo e compila um relatório de falhas ao término da execução para auditoria manual.

## 🛠️ Tecnologias e Ferramentas Utilizadas
- **Linguagem Principal:** Python 3
- **APIs Cloud:** Google GenAI SDK (Gemini Pro), Google Drive API v3, SonarCloud REST API
- **Segurança e Qualidade:** SonarCloud (SAST), Diretrizes OWASP, Catálogo CWE
- **Conceitos de Engenharia:** Infrastructure as Code (IaC), Disaster Recovery, Idempotência, Backoff Progressivo, Caching e FinOps.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Antes de rodar o pipeline, certifique-se de ter o **Python 3.10+** instalado em sua máquina, além das seguintes credenciais configuradas:
1. Um projeto no Google Cloud com a **Google Drive API v3** ativada. Baixe o arquivo de credenciais OAuth2 e salve-o como `credentials.json` na pasta raiz do projeto.
2. Um **Token do SonarCloud** e a **Chave da Organização** gerados em sua conta do SonarCloud.
3. Uma **Chave de API do Google Gemini** configurada nas suas variáveis de ambiente ou gerenciador de credenciais.

### Instalação
Clone o repositório e instale as dependências necessárias:
```bash
git clone https://github.com
cd devsecops-sast-orchestrator
pip install -r requirements.txt
```

*Nota: Certifique-se de que seu arquivo `requirements.txt` inclua os pacotes: `google-genai`, `google-auth-oauthlib`, `google-api-python-client` e `requests`.*

### Ordem de Execução
Execute os módulos sequencialmente para rodar a esteira completa de engenharia de dados e DevSecOps:

```bash
# 1. Provisiona a estrutura hierárquica de pastas no Google Drive Cloud
python 01_environment_provisioner.py

# 2. Estabelece as métricas da linha de base de segurança usando o código legado original
python 02_security_baseline.py

# 3. Executa o pipeline de refatoração com IA consumindo a API do Gemini Pro
python 03_llm_refactoring_pipeline.py

# 4. Dispara a auditoria automatizada de segurança (SAST) e extrai os relatórios (CSV/CWEs)
python 04_sast_audit_engine.py

# 5. Documenta os metadados da engenharia de prompts e a linhagem de dados de origem
python 05_prompt_lineage_documenter.py

# 6. Sincroniza as evidências locais e capturas do dashboard de volta para o Google Drive
python 06_evidence_drive_synchronizer.py
```


