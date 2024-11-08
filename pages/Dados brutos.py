import streamlit as st
import requests
import pandas as pd
import time 


@st.cache_data 
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo Baixado Com Sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()


st.title('DADOS BRUTOS')
    
url = 'https://labdados.com/produtos'

response = requests.get(url) 
dados = pd.DataFrame.from_dict(response.json()) 
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')


with st.expander('Colunas'):
    colunas = st.multiselect('Selecionando As Colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome Do Produto'):
    produtos = st.multiselect('Selecione Os Produtos', dados['Produto'].unique(), dados['Produto'].unique()) 

with st.sidebar.expander('Categoria Do Produto'):
    categoria = st.multiselect('Selecione As Categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Preço Do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000)) 

with st.sidebar.expander('Freta Da Venda'):
    frete = st.slider('Frete', 0, 250, (0, 250)) 

with st.sidebar.expander('Data Da Compra'):
    data_compra = st.date_input('Selecione a Data', (dados['Data da Compra'].min(), dados['Data da Compra'].max())) 

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione Os Vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local Da Compra'):
    local_compra = st.multiselect('Selecione o Local Da Compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação Da Compra'):
    avaliacao = st.slider('Avaliação', dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max(), (dados['Avaliação da compra'].min(), dados['Avaliação da compra'].max())) 
with st.sidebar.expander('Tipo De Pagamento'):
    tipo_pagamento = st.multiselect('Selecione o Tipo De Pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade De Parcelas'):
    qtd_parcelas = st.slider('Selecione a Quantidade De Parcelas', 1, 24, (1, 24))



query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]


st.dataframe(dados_filtrados)

st.markdown(f'A Tabela Possui :blue[{dados_filtrados.shape[0]}] Linhas e :blue[{dados_filtrados.shape[1]}] Colunas')

st.markdown('Escreva Um Nome Para o Arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o Download Da Tabela Em CSV', data = converte_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
