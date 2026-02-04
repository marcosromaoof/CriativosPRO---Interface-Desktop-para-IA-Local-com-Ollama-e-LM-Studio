# 📅 Fase 7: Dashboard e Telemetria "Glassmorphism"

**Estado Atual**: Placeholder "Dashboard em desenvolvimento..." no frontend.
**Objetivo**: Transformar o Dashboard em uma central de comando visual com métricas em tempo real, mantendo a estética premium.

---

## 1. Backend: Coleta e Agregação de Métricas
*(Arquivos alvo: `metrics_manager.py`, `database.py`)*

*   [ ] **Criar Tabela `metrics`**:
    *   Campos: `session_id`, `provider`, `model`, `input_tokens`, `output_tokens`, `latency`, `timestamp`.
*   [ ] **Serviço de Agregação**:
    *   Implementar endpoints (via Socket) para retornar:
        *   Métricas da sessão atual.
        *   Métricas globais (Total Tokens, Custo Total Estimado).
        *   Performance por Provedor (Gráfico comparativo de TPS).

## 2. Frontend: Dashboard Interativo
*(Arquivos alvo: `DashboardView.tsx`, `components/charts/*`)*

*   [ ] **Componente `StatCard`**:
    *   Cartões de vidro (glass) exibindo números grandes (ex: "1.2M Tokens Processados").
*   [ ] **Gráficos de Performance**:
    *   Usar `recharts` ou SVG nativo para desenhar gráficos de linha (TPS ao longo do tempo).
*   [ ] **Distribuição de Modelos**:
    *   Gráfico de rosca mostrando quais modelos são mais usados.
*   [ ] **Logs de Sistema**:
    *   Console visual mostrando eventos do sistema em tempo real (Connect, Generate, Error) com estilo "Cyberpunk/Sci-Fi".

## 3. Integração e Polimento
*   [ ] Conectar o `DashboardView` ao Socket.IO.
*   [ ] Garantir animações suaves na entrada de dados.
*   [ ] Adicionar botão de "Limpar Métricas" nas configurações.

---

## ✅ Critérios de Aceite
1.  Ao clicar no ícone de "Dashboard" (CPU), não deve mais aparecer "Em desenvolvimento".
2.  Deve exibir pelo menos 3 cards de métricas (Tokens, Sessões, Custo).
3.  Deve ter pelo menos 1 gráfico visual.
