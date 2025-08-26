from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random

#configura o plotly para abrir os arquivos no navegador por padra-ão
pio.renderers.default = "browser"

#carregar o arquivo drinks.csv e  o arquivo avengers.csv
dfDrinks = pd.read_csv(r"C:\Users\integral\Desktop\Python 2 Gabriel\drinks.csv")

dfAvengers = pd.read_csv(r"C:\Users\integral\Desktop\Python 2 Gabriel\avengers.csv", encoding='latin1')
#outros encodings de exemplo: uft-16, cp1252, iso8859-1

#cria o banco de dados em sql e popular com os dados csv
conn = sqlite3.connect(r"C:\Users\integral\Desktop\Python 2 Gabriel\bancodados.db")

#Inserir as duas novas tabela npo banco de dados
dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)
dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)


html_template = '''
    <h1> Dashboard - Consumo de Alcool</h1>
    <h2>Parte 01</h2>
    <ul>
        <li><a href="/grafico1">Top 10 paises em consumo de alcool</a></li>
        <li><a href="/grafico2">Media de consumo por tipo de bebidas</a></li>
        <li><a href="/grafico3">Consumo total por regiao</a></li>
        <li><a href="/grafico4">Comparativo entre tipos de bebidas</a></li>
        <li><a href="/pais?nome=Brazil">Insights por pais</a></li>
    </ul>
    <h2>Parte 02</h2>
    <ul>
        <li><a href="/comparar">Comparar</a></li>
        <li><a href="/upload_avengers">Upload CSV</a></li>
        <li><a href="/apagar_avengers">Apagar tabela Avengers</a></li>
        <li><a href="/atribuir paises_avenger">Atribuir Paises</a></li>
         <li><a href="/ver_Tabela">Ver tabela Avengers</a></li>
        <li><a href="/consultar_avengers">Consultar detalhes do Vingador</a></li>
        <li><a href="/aevngers_vs_drinks">V.A.A(Vingadores Alcoolicos Anonimos</a></li>
    <ul>
'''

#iniciar o Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/grafico1')
def grafico1():
    with sqlite3.connect(r"C:\Users\integral\Desktop\Python 2 Gabriel\bancodados.db") as conn:
        df = pd.read_sql_query("""
            SELECT country, total_litres_of_pure_alcohol
            FROM bebidas
            ORDER BY total_litres_of_pure_alcohol DESC
            LIMIT 10                           
        """, conn)
    figuraGrafico01 = px.bar(
        df,
        x='country',
        y='total_litres_of_pure_alcohol',
        title='Top 10 paises com maior consumo de alcool'
    )
    return figuraGrafico01.to_html()

#media por tipo Global
@app.route('/grafico2')
def grafico2():
    with sqlite3.connect(r"C:\Users\integral\Desktop\Python 2 Gabriel\bancodados.db") as conn:
        df = pd.read_sql_query("""
            SELECT AVG(beer_servings) AS cerveja, AVG(spirit_servings) AS Destilados, AVG(wine_servings) AS vinhos FROM bebidas
         """, conn)
        
        #Melted transforma as colinas (cerveja, destilados, vinhos) em Linhas Criando duas colunas:
        #uma chamadas bebidas com os nomes originais das colunas
        #e a outra chama media de porcoes com os valores correspondentes
    df_melted = df.melt(var_name='Bebidas', value_name='Média de Porções')
    figuraGrafico02 = px.bar(
        df_melted,
        x = 'Bebidas',
        y = "Média de Porções",
        title='Media de consumo Global por tipo'
    )
    return figuraGrafico02.to_html()

#grafico 3: consumo por região
@app.route('/grafico3')
def grafico3():
    regioes = {
        "Europa":['France', 'Germany', 'Italy', 'Spain', 'Portugal'],
        "Asia":['China','Japan','India', 'Thailand'],
        "Africa":['Angola', 'Nigeria', 'Egypt', 'Algeria'],
        "Americas":['USA', 'Brazil', 'Canada', 'Argentina', 'Mexico']
    }
    dados=[]
    with sqlite3.connect(r"C:\Users\integral\Desktop\Python 2 Gabriel\bancodados.db") as conn:
# itera sobre o dicionario de regioes onde cada chave (regiao) tem um lista de paises
        for regiao, paises, in regioes.items():
        #criando a lista de placeholders par os paises dessa regiao no formato "oais1, pais2..."
        #isso vai ser utilizado na consulta sql para filtrar os paises da ragiao
            placeholders = ",".join([f"'{p}'" for p in paises])
            query = f"""
            SELECT SUM(total_litres_of_pure_alcohol) AS total
            FROM bebidas
            WHERE country IN ({placeholders})
        """
            #Como a consulta vai retornar um unico valor (soma) pegamos o primeiro valor usando o [0] se o resultado for none (sem dados) retornamos 0 para evitar erros
            total = pd.read_sql_query(query, conn).iloc[0]
            #Adicionar o resultado ao dicionario dados, para cada regiao com o consumo total calculado
            dados.append({"Regiao": regiao, "Consumo Total": total})
    dfRegioes = pd.DataFrame(dados)
    figuraGrafico3 = px.pie(
        dfRegioes,
        names="Regiao",
        values="Consumo Total",
        title="Consumo total por Região"
    )    
    return figuraGrafico3.to_html() + "<br><a href='/>Voltar</a>"

#grafico 4 comparativo entre os tipos de bebidas
@app.route('/grafico4')
def grafico4():
    with sqlite3.connect(r"C:\Users\integral\Desktop\Python 2 Gabriel\bancodados.db") as conn:
        df = pd.read_sql_query(" SELECT beer_servings, spirit_servings, wine_servings FROM bebidas", conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo','Média']
        figuraGrafico04 = px.pie(
            medias,
            names='Tipo',
            values='Média',
            title='Proporcao media'
        )
    return figuraGrafico04.to_html() + "<br><a href='/'Voltar<a/a>"

@app.route("/comparar", methods=['GET','POST'])
def comparar():
    opcoes = ['beer_servings','spirit_servings','wine_servings','total_litres_of_pure_alcohol']
    if request.method == "POST":
        #logica para mostrar o grafico quando um post ao acessar a pagina
        eixo_x = request.form.get('eixo_x')
        eixo_y = request.form.get('eixo_y')
        if eixo_x == eixo_y:
            return
    #aqui é a pagina sem post, ou seja, a primeira vez que o usuário entrar na pagina
    return render_template_string('''
        <h2>Comparar Campos </h2>
        <form method="POST>
            <label>Eixo X:</label>
            <select>
                {% for opcao in opcoes %}
                    <option value= {{opcao}}">{{opcao}}</option>
                {% endfor %}
            <select>
            <br> <br>
            <label> Eixo Y: </label>
            <select>
                {% for opcao in opcoes %}
                    <option value= {{opcao}}">{{opcao}}</option>
                {% endfor %}
            <select>
            <br><br>
            <input type='submit" value=" -- Comparar -- ">
        </form>
    ''', opcoes = opcoes)



#"iniciar o servidor"
if __name__ =='__main__':
    app.run(debug=True)


    ### Parei no return da linha 148