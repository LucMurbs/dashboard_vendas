import streamlit as st
import requests
import pandas as pd
import plotly.express as px 
#Obs: Lembrando que sempre que eu sair tenho que executar o venv novamente!!! com o comando .\venv\Scripts\activate!
#Obs; A partir do terminal do computador, é possível checar as bibliotecas instaladas no ambiente virtual usando o comando pip freeze. 
#Obs: Precisa ser um arquivo de texto com o nome específico: requirements.txt  para pode fazer o deploy






st.set_page_config(layout='wide') #Para ajudar a não sobrepor um gráfico com o outro de outra coluna








def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo}  {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo}  {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

##Filtros
###Por região
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados De Todo o Período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao' : regiao.lower(), 'ano':ano}



##Usando o requests para pegar a url!
response = requests.get(url, params=query_string) #Usei o params para passar o filtro que eu fiz usando a própria url
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

###Filtro Por vendedores, coloquei aqui porque precisei de ler os dados primeiro, esse filtro foi feito sem ser pela url e sim pelos dados já lido!
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]






##Tabelas
###Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on= 'Local da compra', 
                                                                                                            right_index=True).sort_values('Preço', ascending=False) 
#Aqui eu substitui a primeira variável criada anteriormente, usei uma função para remover todas as linhas que tem informação duplicada, 
# vamos manter apenas os valores únicos de sigla de estado, o subset é usado para informar que queremos remover as duplicadas com base na informação que passarmos para ele,
#depois selecionamos as colunas que queremos manter nessa tabela, e depois usamos o merge para agrupar essa tabela que criamos com o drop_duplicates com a que criamos anteriormente,
#left_on é a coluna base, a qual usamos para começar a fazer o agrupamento, e o right_index para pegar a mesma variável que é 'Local da compra" na tabela que eu criei com o drop
#duplicates!

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))[['Preço']].sum().reset_index() #O Grouper é usado para agrupar os meses separadamente um do outro`
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

###Tabelas de Quantidade De Vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, 
                                                                                                           left_on = 'Local da compra', 
                                                                                                           right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

###Tabelas Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))








#Gráficos
###Gráficos Receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço', #esse daqui define o tamanho do círculo
                                  template = 'seaborn', #aqui é para manter o padrão do seaborn
                                  hover_name = 'Local da compra', #essa serve para quando eu passar o mouse em cima ver o nome do estado que é aquela bolha
                                  hover_data = {'lat' : False, 'lon' : False}, #aqui é para tirar a informação de latitude e longitude, deixar só o estado e o preço!
                                  title = 'Receita Por Estado')

fig_receita_mensal = px.line(receita_mensal, 
                             x = 'Mês',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano', #altera o formato da linha conforme o ano
                             title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True, #Esse parâmetro indica que vamos colocar o valor da receita em cima de cada uma das colunas de forma automática!
                             title = 'Top Estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True, #Aqui não precisamos passar o x e o y porque como só tem duas informações o plotly vai identificar automaticamente
                                title='Receita Por Categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


###Gráficos Quantidade De Vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')






## Visualização Streamlit
aba1 , aba2, aba3 = st.tabs(['Receita', 'Quantidade De Vendas', 'Vendedores'])
with aba1:
    coluna1 , coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita Total', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)
with aba2:
    coluna1 , coluna2 = st.columns(2)
    with coluna1:
        st.metric('Quantidade De Vendas Total', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
    with coluna2:
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5) 
    coluna1 , coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita Total', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores), #O head foi usado para agrupar os 5 vendedores da qtd que passamos ali em cima 
                                        x='sum',
                                        y=vendedores[['sum']].sort_values(['sum'], ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')

    st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade De Vendas Total', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores), #O head foi usado para agrupar os 5 vendedores da qtd que passamos ali em cima 
                                        x='count',
                                        y=vendedores[['count']].sort_values(['count'], ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')

    st.plotly_chart(fig_vendas_vendedores)

 




