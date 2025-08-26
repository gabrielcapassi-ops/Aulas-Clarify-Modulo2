# www.adorocinema.com
# Takvez precise instalar alguns
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

baseURL = 'https://www.adorocinema.com/filmes/melhores/'
filmes = [] # Lista que vai armazenar os dados coletados de cada filme
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
agora = datetime.datetime.now()
paginaLimite = 20 #Quantidade de paginas que vai analisar
card_temp_min = 1
card_temp_max = 3
pag_temp_min = 2
pag_temp_max = 5
bancoDados = "C:/Users/integral/Desktop/Python 2 Gabriel/banco_filmes.db"
saidaCSV = f"C:/Users/integral/Desktop/Python 2 Gabriel/filmes_adorocinema_{data_hoje}.csv"


for pagina in range(1,paginaLimite + 1):
    url = f"{baseURL}?page={pagina}" #Monta a URL numerada
    print(f'Coletando dados da pagina {pagina} : {url}')
    resposta = requests.get(url, headers=headers)
    soup = BeautifulSoup(resposta.text, 'html.parser')


    #Se o site não responder pula para a proxima pagina
    if resposta.status_code != 200:
        print(f'"erro ao carregar a pagina {pagina}. Código do erro é: {resposta.status_code}')
        continue
    #Cada filme aparece em uma div(card) com a classe abaixo.
    cards = soup.find_all("div", class_="card entity-card entity-card-list cf")
    #iteramos por cada card(div) de filme
    for card in cards:
        try:
            #capturar o título e link da pagina do filme
            titulo_tag = card.find("a", class_="meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "Https://www.adorocinema.com" + titulo_tag ['href'] if titulo_tag else None
            #capturar a nota do filme
            nota_tag = card.find("span", class_="stareval-note")
            nota = nota_tag.text.strip(). replace(",",".") if nota_tag else "N/A"
            #Caso exista link acessar a pagina individual do site
            if link:
                filme_resposta = requests.get(link, headers)
                filme_soup = BeautifulSoup(filme_resposta.text, "html.parser")
            #Captura do diretor
            diretor_tag = filme_soup.find("div", class_="meta-body-item meta-body-direction meta-body-online")
            if diretor_tag:
                #vamos higienizar o texto diretor
                diretor = diretor_tag.text.strip().replace ("Direção:","").replace(",","").replace("|","").strip()
            else:
                diretor ="N/A"
            diretor = diretor.replace("\n","").replace("\r","").strip()

            #captura dos generos
            genero_block = filme_soup.find("div", class_="meta-body-info")
            if genero_block :
                generos_links = genero_block.find_all("a")
                generos = [g.text.strip() for g in generos_links]
                categoria = ",".join(generos[:3] if generos else "N/A")
            else:
                categoria = "N/A"

            #Captura o ano de lancamento do filme
            ano_tag = genero_block.find("span", class_="date") if genero_block else None
            ano = nota_tag.text.strip() if nota_tag else "N/A"

            #só adiciona o filme se todos os dados principais existirem
            if titulo != "N/A" and link != "N/A" and nota != "N/A":
                filmes.append({
                    "Titulo": titulo,
                    "Direção": diretor,
                    "Nota" : nota,
                    "Link": link,
                    "Ano": ano,
                    "Categoria": categoria
                })
            else:
                print(f"Filme incompleto ou erro na coleta de dados {titulo}")

            #aguardar um tempo aleatorio entre os parametos escolhidos para nao sobrecarregar o site e nem revelerar que somos um bot
            tempo = random.uniform(card_temp_min, card_temp_max)
            time.sleep(tempo)
            tempo_ajustado = math.ceil(tempo)
            print(f"Tempo de espera {tempo_ajustado}seg")
        except Exception as e:
                print(f"Erro ao processar o filme {titulo}. Erro: {e}")
    #esperar um tempo entre uma pagina e outra
    tempo = random.uniform(pag_temp_min,pag_temp_max)
    time.sleep(tempo)
    

#converter os dados coletados para um dataframe do pandas
df = pd.DataFrame(filmes)
print(df.head())

#Salva os dados em CSV
df.to_csv(saidaCSV, index=False, encoding="utf-8-sig", quotechar="'", quoting=1)

#COnecta um banco de dados SQLite (cria se nao existir)
conn = sqlite3.connect(bancoDados)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS filmes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Titulo TEXT,
        Direcao TEXT,
        Nota REAL,
        Link TEXT,
        Ano TEXT,
        Categoria TEXT
               )
''')

#inserir cada filme coletado dentro da tabela do banco de dados
for filme in filmes:
    try:
        cursor.execute('''
            INSERT INTO filmes(Titulo, Direcao, Nota, Link, Ano, Categoria) VALUES(?,?,?,?,?,?)
''',(
        filme['Titulo'],
        filme['Direção'],
        float(filme['Nota']) if filme['Nota'] != 'N/A' else None,
        filme['Link'],
        filme['Ano'],
        filme['Categoria'],
    ))
    except Exception as e:
        print(f"Erro ao inserir filme {filme['Titulo']} no banco de dados. Código de identificação do erro: {e}.")
conn.commit()
conn.close()

print('Dados raspado salvo com sucesso')
print(f'\n Arquivo salvo em: {saidaCSV}\n')
print('Obrigado por usar o Sistema de Bot do Gabriel')
print(f'Finalizado em: {agora.strftime("%H:%M:%S")}')
print('-------------------------------')