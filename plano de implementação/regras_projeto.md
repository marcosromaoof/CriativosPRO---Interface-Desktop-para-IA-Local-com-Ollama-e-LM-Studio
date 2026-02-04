# 🚫 Regras de Organização de Arquivos e Engenharia

Este documento define as regras estritas para organização de arquivos e, PRINCIPALMENTE, as diretrizes inegociáveis de engenharia e conduta técnica do projeto.

## 1. Regras para a Raiz do Projeto (`/`)
*   **PROIBIDO:** Criar scripts utilitários, de teste ou automação na raiz.
*   **PROIBIDO:** Criar arquivos de documentação, anotações ou "lixo" na raiz.
*   **PERMITIDO APENAS:** Arquivos essenciais da estrutura do projeto (ex: `start_dev.bat`) e pastas do sistema (`backend`, `frontend`, `bin`).

## 2. Regras para Scripts e Documentação
Todos os documentos auxiliares, scripts de manutenção, planos e checklists devem ser salvos exclusivamente dentro da pasta:
📂 **`/plano de implementação/`**

*   Se houver scripts, eles devem ser organizados em subpastas dentro desta diretoria (ex: `/plano de implementação/scripts/`).
*   Se houver documentos, eles devem ser organizados em subpastas ou na raiz desta diretoria.

## 3. Integridade do Código Fonte
*   As pastas do código fonte (`core/`, `frontend/`) devem conter **apenas** código da aplicação. Não misture anotações ou scripts temporários nestas pastas.

---

## 4. Regras Fundamentais de Engenharia (Anti-Gambiarra & Boas Práticas)
*Estas regras têm prioridade MÁXIMA e devem ser seguidas sem exceção.*

### 4.1. Zero Improviso / Zero Gambiarra
*   **PROIBIDO:** Implementar "soluções rápidas" que desrespeitem a arquitetura.
*   **PROIBIDO:** Buscar alternativas irregulares apenas para "fazer funcionar" no curto prazo.
*   **PROIBIDO:** Inventar soluções não solicitadas ou baseadas em suposições (achismos).
*   Se não sabe como fazer corretamente respeitando o padrão: **PARE E PERGUNTE**.

### 4.2. Preservação e Análise
*   **Análise Obrigatória:** Antes de qualquer linha de código, analise o impacto no sistema existente.
*   **Não Quebre Nada:** É proibido alterar comportamentos estáveis ou simplificar soluções já complexas e funcionais.

### 4.3. Responsabilidade de Produção
*   Trate este código como software crítico em produção comercial.
*   Segurança e Performance não são opcionais.
*   Toda modificação exige **Auditoria Lógica** antes de ser entregue.

### 4.4. Contexto e Clareza
*   Se o pedido for ambíguo: **Solicite Esclarecimento**.
*   Nunca prossiga no escuro.

### 4.5. Auditoria de Alterações
Toda vez que criar, editar ou refatorar código, você deve garantir:
1.  Que nada foi quebrado.
2.  Que não há regressões.
3.  Que a implementação segue as **Boas Práticas de Engenharia de Software**.

##  4.6 regra de espostas
responder sempre em portugues do brasil

#implementação
toda imprementação, manutenção ou alteração no código deve seguir as regras abaixo:
1-  deve ser feito por etapas
2-  dever ter aprovação do usuario antes de cada etapa
3- deve ser criado um plano de implementação detalhado antes de qualquer alteração
4- deve ser criado um ckek list de tarefas a serem feitas antes de qualquer alteração 
5- deve ler e obedecer as regras do @rules: GEMINI.md
