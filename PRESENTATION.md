# 🔮 Apresentação: DataVision AI - Análise Inteligente de Dados
### Aluno: Jackson Jhonatan Melo da Silva (jackson.victorius@gmail.com)
## 1. Framework Escolhida
### Streamlit 🚀
- Justificativa : Framework Python ideal para aplicações de ciência de dados
- Vantagens :
  - Desenvolvimento rápido de interfaces web interativas
  - Integração nativa com bibliotecas de dados (pandas, plotly)
  - Suporte a componentes customizados com CSS/HTML
  - Deploy simples e eficiente
  - Ideal para prototipagem e demonstrações de IA
### Tecnologias Complementares:
- Google AI (Gemini) : Para processamento de linguagem natural e análise inteligente
- Pandas : Manipulação e análise de dados
- Plotly : Visualizações interativas
- Python-dotenv : Gerenciamento de variáveis de ambiente

## 2. Estrutura da Solução
### Arquitetura Multi-Agente 🤖
```
DataVision AI
├── 🎯 CoordinatorAgent (Orquestrador Principal)
│   ├── 📊 CSVAgent (Processamento de Arquivos)
│   ├── 🔍 QueryAgent (Processamento de Consultas)
│   └── 💡 InsightAgent (Geração de Insights)
├── 🛠️ Services (Serviços de Negócio)
│   ├── DataService (Análise de Dados)
│   ├── ChartService (Visualizações)
│   └── FileService (Manipulação de Arquivos)
└── 🎨 UI/UX (Interface Moderna)
    ├── Dark Mode Support
    ├── Responsive Design
    └── Multilingual (PT-BR/EN)
```
### Fluxo de Funcionamento:
1. Upload → CSVAgent processa o arquivo
2. Análise → InsightAgent gera análise inicial automática
3. Consulta → QueryAgent processa perguntas em linguagem natural
4. Visualização → ChartService gera gráficos inteligentes
5. Resposta → CoordinatorAgent orquestra e retorna resultados

## 3. Demonstração com Perguntas e Respostas
### Pergunta 1: Análise Descritiva
Pergunta : "Quais são as estatísticas básicas dos dados?"

Resposta Esperada :

```
📊 Análise Estatística Básica:
- Total de registros: 1,250
- Colunas numéricas: 5
- Colunas categóricas: 3
- Valores ausentes: 2.3%
- Média geral: 45.67
- Desvio padrão: 12.34
```
### Pergunta 2: Análise de Padrões
Pergunta : "Existem correlações interessantes nos dados?"

Resposta Esperada :

```
🔍 Análise de Correlações:
- Forte correlação positiva (0.87) entre Vendas e Marketing
- Correlação negativa (-0.45) entre Preço e Volume
- Padrão sazonal identificado nos dados temporais
- 3 clusters principais detectados nos dados
```
### Pergunta 3: Detecção de Anomalias
Pergunta : "Há valores atípicos ou outliers nos dados?"

Resposta Esperada :

```
⚠️ Detecção de Outliers:
- 23 outliers identificados (1.8% dos dados)
- Concentrados principalmente na coluna 'Receita'
- Valores extremos: R$ 150.000 (3x acima da média)
- Recomendação: Investigar registros específicos
```
### Pergunta 4: Visualização Gráfica 📈
Pergunta : "Mostre a distribuição das vendas por região"

Resposta com Gráfico :

```
📊 Gráfico Gerado: Gráfico de Barras
- Região Sudeste: 45% das vendas
- Região Sul: 25% das vendas  
- Região Nordeste: 20% das vendas
- Região Norte: 10% das vendas

[Gráfico de barras interativo seria exibido aqui]
```
### Pergunta 5: Conclusões do Agente 🧠
Pergunta : "Qual sua opinião geral sobre este dataset?"

Resposta do Agente :

```
💡 Análise Técnica do Dataset:

Qualidade dos Dados: ⭐⭐⭐⭐⭐ (Excelente)
- Dados bem estruturados com baixo índice de valores 
ausentes
- Tipos de dados consistentes e apropriados
- Boa distribuição temporal dos registros

Insights Principais:
✅ Dataset adequado para análises preditivas
✅ Padrões claros de sazonalidade identificados
✅ Correlações significativas para modelagem
⚠️ Alguns outliers requerem investigação

Recomendações:
1. Implementar limpeza de outliers antes da modelagem
2. Explorar análise de séries temporais
3. Considerar segmentação por região para insights mais 
profundos
4. Dataset tem potencial para machine learning
```

## 4. Códigos Fonte Principais
### Arquivo Principal (app.py)
```python
import streamlit as st
from agents.coordinator import CoordinatorAgent
from services.data_service import DataService
from services.chart_service import ChartService

# Configuração da página
st.set_page_config(
    page_title="DataVision AI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização dos serviços
coordinator = CoordinatorAgent()
data_service = DataService()
chart_service = ChartService()
```
### Agente Coordenador (coordinator.py)
```python
class CoordinatorAgent:
    def __init__(self):
        self.csv_agent = CSVAgent()
        self.query_agent = QueryAgent()
        self.insight_agent = InsightAgent()
    
    def process_file(self, file):
        result = self.csv_agent.process(file)
        if isinstance(result, str):
            return result
        self.data = result
        self.insights = self.insight_agent.process(
            self.data, 
            operation="initial_analysis"
        )
        return self.data
```
### Processamento de Consultas (query_agent.py)
```python
class QueryAgent:
    def process(self, query, data_context):
        # Integração com Google AI (Gemini)
        response = self.gemini_client.generate_content(
            prompt=self._build_prompt(query, data_context)
        )
        return response.text
```
## 5. Funcionalidades Implementadas
### ✅ Recursos Principais:
- Upload e processamento automático de CSV
- Análise estatística inteligente
- Consultas em linguagem natural (PT-BR/EN)
- Geração automática de gráficos
- Interface moderna com dark mode
- Arquitetura multi-agente escalável
### ✅ Recursos Avançados:
- Detecção automática de padrões
- Análise de qualidade de dados
- Sampling inteligente para datasets grandes
- Validação contextual de perguntas
- Insights técnicos automatizados
## 6. Link de Acesso ao Agente
### 🌐 Acesso Local:
```
# Para executar a aplicação:
streamlit run app.py

# Acesso via navegador:
http://localhost:8501
```
### 📋 Pré-requisitos:
1. Python 3.8+
2. Instalar dependências: pip install -r requirements.txt
3. Configurar API Key do Google AI no arquivo .env
4. Executar: streamlit run app.py
### 🔗 URL de Demonstração:
- Local : http://localhost:8501
- Rede : http://[seu-ip]:8501
## 7. Diferenciais da Solução
### 🎨 Interface Moderna:
- Design responsivo com gradientes
- Suporte completo a dark mode
- Sidebar sempre visível
- Animações suaves
### 🤖 IA Avançada:
- Processamento de linguagem natural
- Análise contextual inteligente
- Geração automática de insights
- Sugestões de visualizações
### 🌍 Multilingual:
- Suporte completo PT-BR/EN
- Validação contextual de perguntas
- Interface adaptativa por idioma
## 8. Próximos Passos
### 🚀 Melhorias Planejadas:
- Integração com bancos de dados
- Exportação de relatórios em PDF
- Análise preditiva com ML
- Sistema de autenticação
- Deploy em nuvem

---

### 🔮 DataVision AI - Transformando Dados em Inteligência

Desenvolvido com Streamlit, Google AI (Gemini) e arquitetura multi-agente para análise inteligente de dados CSV com interface moderna e suporte multilingual.