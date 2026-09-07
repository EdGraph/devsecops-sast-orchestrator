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
