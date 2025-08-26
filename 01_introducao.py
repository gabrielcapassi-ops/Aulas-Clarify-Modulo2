#Importa a biblioteca pandas
import pandas as pd

#armazena a string do caminho
caminho = 'C:/Users/integral/Desktop/Python 2 Gabriel/01_base_vendas.xlsx'

#carrega dos dados da planilha em um dataframe
df1 = pd.read_excel(caminho, sheet_name="Relatório de Vendas")
df2 = pd.read_excel(caminho, sheet_name="Relatório de Vendas1")

print('\n ----------------------')
print('Primeiro Relatório de Vendas')
print(df1.head())

print('\n ----------------------')
print('Se Relatório de Vendas')
print(df2.head())

#Juntar nos dois dataframes e, unico dataframe consolidado
#O Ignore index vai garantir que o indice seja reordenado apos a junção

dfConsolidado = pd.concat([df1,df2], ignore_index=True)

#Verifica quantos duplicados existem no relatório
print('\n ----------------------')
print('Duplicados no relatório de vendas')
print(dfConsolidado.duplicated().sum())

#Agrupar clientes por cidade
clientesPorCidade = dfConsolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('\n ----------------------')
print('Clientes po cidade')
print(clientesPorCidade)

#Conta o numero de vendas para cada tipo de plano vendido
vendasPorPLano = dfConsolidado['Plano Vendido'].value_counts()
print('\n ----------------------')
print('Numero de Vendas por Plano')
print(vendasPorPLano)

#Selecinonar as 3 maiores cidades em numeros de clientes distintos
topTresCidades = clientesPorCidade.head(3)
print('\n ----------------------')
print('Top 3 cidades em vendas')
print(topTresCidades)

#Cria uma nova coluna chamada status com base no plano vendido 
#Se o plano for "Enterprise" o status será "premium", caso contrario será padrão.
print('\n ----------------------')
dfConsolidado["Status"] = dfConsolidado["Plano Vendido"].apply (lambda x: 'Premium' if x == 'Enterprise' else 'Padrão')
#conta quantos registros tem cada tipo de status (premium e padrao)
statusDist = dfConsolidado['Status'].value_counts()
print('\n ----------------------')
print('\n Distribuicao de status do Plano')
print(statusDist)

#Salvar dados em csv e xlsx.
print('\n ----------------------')
try:
    #se quiser colocar o destino em que o arquivo sera salvo, inserir o endereco de saida(caminho) antes do nome do arquivo 'dados_saida.xlsx' ficaria assim: 'C:/Users/integral/Desktop/Python 2 Gabriel/dados_saida.clsx'
    dfConsolidado.to_excel('dados_saída.xlsx', index=False)
    dfConsolidado.to_csv('dados_saída.csv', index=False)
    print('\n Arquivos gerados com sucesso')
except:
    print('\n Erro ao gerar os arquivos, contate o administrador')

