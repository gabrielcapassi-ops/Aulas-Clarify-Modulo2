import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sqlite3
import datetime
import math

# BeautifulSoup biblioteca para analisar HTML e extrair informações

#Headers é para enganar dizendo qe vc esta usando um browser
headers = {
    'User-Agent': 'Mozilla/5.0 NT 10.0; Win; x64) AppleWebKit537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

baseURL = 'https://www.sampaingressos.com.br/espetaculos/shows/ajax/lista_espetaculo.php'
shows = [] # Lista que vai armazenar os dados coletados de cada filme
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
agora = datetime.datetime.now()
paginaLimite = 2 #Quantidade de paginas que vai analisar
card_temp_min = 1
card_temp_max = 3
pag_temp_min = 2
pag_temp_max = 5
bancoDados = "C:/Users/integral/Desktop/Python 2 Gabriel/banco_shows.db"
saidaCSV = f"C:/Users/integral/Desktop/Python 2 Gabriel/shows_sampaingressos_{data_hoje}.csv"

for pagina in range(1,paginaLimite + 1):
    url = f"{baseURL}?pagina={pagina}&tipoEspetaculo=shows"
    print(f'Coletando dados da pagina {pagina} : {url}')
    resposta = requests.get(url, headers=headers)
    soup = BeautifulSoup(resposta.text, 'html.parser')

    
    if resposta.status_code != 200:
        print(f'"erro ao carregar a pagina {pagina}. Código do erro é: {resposta.status_code}')
        continue
  
    cards = soup.find_all("div", id="box_espetaculo")

    for card in cards:
        try:
            
            show_tag = card.find("b", class_="titulo")
            show = show_tag.text.strip() if show_tag else "N/A"
            
            diaShow_tag = card.find("span", class_="temporada")
            diaShow = diaShow_tag.text.strip(). replace(",",".") if diaShow_tag else "N/A"

            local_tag = card.find("span", class_="local")
            local = local_tag.text.strip(). replace(",",".") if local_tag else "N/A"

            horario_tag = card.find("span", class_="horario")
            horario = horario_tag.text.strip(). replace(",",".") if horario_tag else "N/A"

        

            if show != "N/A":
                    shows.append({
                        "Show": show,
                        "Data": diaShow,
                        "Local" : local,
                        "Horario": horario
                    })
            else:
                    print(f"Show incompleto ou erro na coleta de dados {show}")


        except Exception as e:
                print(f"Erro ao processar o show {show}. Erro: {e}")

    tempo = random.uniform(pag_temp_min,pag_temp_max)
    time.sleep(tempo)

#converter os dados coletados para um dataframe do pandas
df = pd.DataFrame(shows)
print(df.head())

#Salva os dados em CSV
df.to_csv(saidaCSV, index=False, encoding="utf-8-sig", quotechar="'", quoting=1)

#COnecta um banco de dados SQLite (cria se nao existir)
conn = sqlite3.connect(bancoDados)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS filmes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Show TEXT,
        Data TEXT,
        Local TEXT,
        Horario TEXT
               )
''')

#inserir cada filme coletado dentro da tabela do banco de dados
for shows in show:
    try:
        cursor.execute('''
            INSERT INTO filmes(Show, Data, Local, Horario) VALUES(?,?,?,?,?,?)
''',(
        show['Show'],
        show['Data'],
        show['Local'],
        show['Horario'],
 
    ))
    except Exception as e:
        print(f"Erro ao inserir o espetaculo {['Show']} no banco de dados. Código de identificação do erro: {e}.")
conn.commit()
conn.close()

print('Dados raspado salvo com sucesso')
print(f'\n Arquivo salvo em: {saidaCSV}\n')
print('Obrigado por usar o Sistema de Bot do Gabriel')
print(f'Finalizado em: {agora.strftime("%H:%M:%S")}')
print('-------------------------------')