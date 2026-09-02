# XP CHallenge - Agente de IA para recomendação de investimentos.
## 1. Introdução
A XP tem cerca de 20 mil assessores atendendo até 300 clientes cada. Para a base "middle market" (Clientes com patrimônio menor que 1.000.000R$), não é viável dar atenção individual mensal a cada cliente. Por isso o desafio pede um agente de IA que gera automaticamente uma carta mensal cobrindo três frentes: (1) desempenho do portfólio, (2) cenário macroeconômico relevante, e (3) recomendações alinhadas ao perfil de risco do cliente.

Este repositório contém a versão 2 de um agente que já existia. Essa versão mantém o mesmo objetivo, mas foca em resolver os problemas da versão 1 na área de **lógica de recomendação de compra/venda**, com uma calculadora de rentabilidade real como pré-requisito.

### Dependências
```bash
pip install openai python-docx
```

### Como rodar
`Windows:`
`$env:OPENAI_API_KEY = "sua_key_aqui"`

`Mac/Linux:`
`export OPENAI_API_KEY="sua_key_aqui`

`python main.py`

É também necessário que exista uma pasta `'data'` com os dados sobre o portfolio e perfil de risco do cliente e um `.csv` e os dados sobre o cenário `macro` da economia atual. Além disso, é necessário uma pasta `output` para a carta ser gerada. A key nunca é lida de um arquivo do repositório, apenas da variável de ambiente.

Para inspecionar os cálculos e as decisões sem gastar chamada de API:
```bash
python profitability.py
python recommend.py
```

## 2. A versão 1 do agente e seus problemas
A versão 1 segue um fluxo simples, ela lê os 3 documentos 'macro.txt', 'portfolio.txt' e 'risk_profile.txt' (Relatório macro, carteira e perfil de risco), pede pra um GPT resumir cada um separadamente e depois pede para um GPT final juntar os três resumos em uma carta.

### Problemas identificados
- **O CSV de rentabilidade ('profitability_calc_wisp.csv') nunca é usado.** Nenhum nó no workflow o lê, e isso nos faz entender porque a carta final da versão 1 cita "retorno total de 3,5%" e "0,2pp acima do benchmark", números que não existem em nenhum dos inputs, foram inventados pelo LLM ao tentar resumir o texto bruto da carta.

- **Prompt do perfil de risco pede dados inexistentes.** No PDF real do perfil de risco do cliente não há dados como idade, renda, liquidez etc, dados esses que são pedidos pelo prompt, ou seja, foi escrito de forma genérica sem checar o input real.

- **Nenhuma lógica de recomendação de compra/venda.** Como foi dito, a versão 1 não utiliza o arquivo CSV de rentabilidade que possui informações valiosas para recomendações e indicações pro perfil do cliente, logo, a versão não indica nenhuma recomendação de compra/venda mesmo existindo ativos que iriam satisfazer o cliente muito mais.

- **Output é texto puro**. Não há geração automática de documento formatado.

## 3. Soluções propostas
A decisão central da arquitetura é separar cálculo/decisão de narrativa (LLM). O LLM nunca decide números nem recomendações, ele só transforma decisões já tomadas em texto fluente. Isso elimina a causa raiz do problema de não utilizar o CSV de rentabilidade. 

Sendo assim, os módulos resolvem o seguinte problema:
`portfolio_data.py`: Estrutura e aloca todos os dados que utilizaremos para a decisão determinística.

`profitability.py`: Calcula e retorna a rentabilidade de cada ativo e fundo não só da carteira do cliente como das potenciais substituições nas vendas que ele poderá fazer, sendo feito a partir do CSV.

`recommend.py`: É o motor de regras, vende/monitora ações fora do perfil + com prejuízo acumulado; sugere comprar a partir do universo contido no CSV.

`narrative.py`: Chama a OpenAI API só para frasear números e decisões já calculados, nunca para decidi-los.

`build_letter.py`: Responsável direto para estruturação e formatação da carta na forma correta para o cliente, formatada em .docx.

Foi utilizado o fato de que apenas 4 dos 12 ativos que estão no CSV estão na carteira do cliente do problema para guiar o design da lógica de compra/venda. Os outros 8 são blue chips pagadores de dividendos que batem exatamente com o critério de ações do perfil "Moderado" do Albert. 

Outro ponto é que o retorno "acumulado desde a compra" (do extrato) e o retorno "mensal" (do CSV) são métricas diferentes e não podem ser confundidas, nossa versão calcula e rotula as duas separadamente, em vez de misturar elas como a versão 1 fazia.

## 4. Resultados
Exemplo de carta gerada para o cliente Albert na versão 2:
> **Desempenho do portfólio**: No mês em análise, o retorno total ponderado da carteira foi de +11,89%, refletindo um desempenho robusto em diversas classes de ativos. As ações apresentaram um retorno de 7,74%, enquanto os fundos se destacaram com um retorno de 13,07%. É importante ressaltar que a renda fixa não apresentou variação, mantendo um retorno de 0,0%.[...]
>**Recomendações**:Considerando o perfil de risco moderado e a necessidade de equilibrar segurança e retornos, é prudente monitorar as ações LREN3 e MRFG3, que, apesar de apresentarem características que podem atrair investidores, não se alinham totalmente ao seu perfil. [...]

Toda decisão e números citados no exemplo acima é rastreável a um input real, diferente da versão 1, cujos números não tinham fonte verificável.