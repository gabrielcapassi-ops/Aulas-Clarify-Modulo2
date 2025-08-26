from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random
import configuracoes as config
caminhobanco = config.DB_PATH

queryVerVingadores = config.consulta01
querryGrafico1 = config.consulta02
apagarVingadores = config.consulta03

#configura o plotly para abrir os arquivos no navegador por padrão
pio.renderers.default = "browser"

#carregar o arquivo drinks.csv
dfDrinks = pd.read_csv(r"C:\Users\integral\Desktop\Python 2 Gabriel\drinks.csv")
dfAvengers = pd.read_csv(r"C:\Users\integral\Desktop\Python 2 Gabriel\avengers.csv", encoding='latin1')
#outros encodings de exemplo: uft-16 , cp1252, iso8859-1

#criar o banco de dados em sql e popular com os dados do csv
conn = sqlite3.connect(caminhobanco)

#inserir as duas novas tabelas no banco de dados
dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)
dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

html_template = '''
    <h1>Dashboard - Consumo de Alcool</h1>
    <h2>Parte 01</h2>
    <ul>
        <li><a href="/grafico1">Top 10 paises em consumo de alcool</a></li>
        <li><a href="/grafico2">Media de consumo por tipo de bebida</a></li>
        <li><a href="/grafico3">Consumo total por regiao</a></li>
        <li><a href="/grafico4">Comparativo entre tipos de bebidas</a></li>
        <li><a href="/pais?nome=Brazil">Insights por pais (Brasil)</a></li>
    </ul>
    <h2>Parte 02</h2>
    <ul>
        <li><a href="/comparar">Comparar</a></li>
        <li><a href="/upload_avengers">Upload CSV</a></li>
        <li><a href="/apagar_avengers">Apagar tabela Avengers</a></li>
        <li><a href="/atribuir_paises_avengers">Atribuir Paises</a></li>
        <li><a href="/ver_vingadores">Ver Tabela Avengers</a></li>
        <li><a href="/consultar_avengers">Consultar detalhes do Vingador</a></li>
        <li><a href="/avengers_vs_drinks">V.A.A (Vingadores Alcoólicos Anonimos)</a></li>
    </ul>
'''


#iniciar o flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/grafico1')
def grafico1():
    with sqlite3.connect(caminhobanco) as conn:
        df = pd.read_sql_query(queryGrafico1, conn)
    figuraGrafico01 = px.bar(
        df, 
        x="country",
        y="total_litres_of_pure_alcohol",
        title="Top 10 paises com maior consumo de alcool"
    )
    return figuraGrafico01.to_html()

#media por ti´po global
@app.route('/grafico2')
def grafico2():
    with sqlite3.connect(caminhobanco) as conn:
        df = pd.read_sql_query("""
            SELECT AVG(beer_servings) AS cerveja, AVG(spirit_servings) AS destilados, AVG(wine_servings) AS vinhos FROM bebidas
        """, conn)
#transforma as colunas (cerveja, destilados, vinhos) em linhas criando duas colunas:
#uma chamada bebidas com os nomes originais das colunas
# e outra chama media de porções com os valores correspondentes
    df_melted = df.melt(var_name='Bebidas', value_name='Média de Porções')
    figuraGrafico02 = px.bar(
        df_melted,
        x="Bebidas",
        y="Média de Porções",
        title="Média de consumo global por tipo"
    )
    return figuraGrafico02.to_html()

#grafico 3: consumo por região
@app.route('/grafico3')
def grafico3():
    regioes = {
        "Europa":['France','Germany','Italy','Spain','Portugal'],
        "Asia":['China','Japan','India','Thailand'],
        "Africa":['Angola','Nigeria','Egypt','Algeria'],
        "Americas":['USA','Brazil','Canada','Argentina','Mexico']
    }
    dados=[]
    with sqlite3.connect(caminhobanco) as conn:
        # itera sobre o dicionario de regioes onde cada chave (região) tem uma lista de paises
        for regiao, paises in regioes.items():
            #criando a lista de placeholders para os paises dessa região no formato "pais1", pais2...
            #isso vai ser utilizado na consulta sql para filtrar os paises da região  
            placeholders = ",".join([f"'{p}'" for p in paises])
            query = f"""
                SELECT SUM(total_litres_of_pure_alcohol) AS total
                FROM bebidas
                WHERE country IN ({placeholders})
            """
            # como a consulta vai retornar um unico valor (soma) pegamos o primeiro valor usando o [0] se o resultado for none (sem dados) retornamos 0 para evitar erros
            total = pd.read_sql_query(query, conn).iloc[0,0]
            # adicionar o resultado ao dicionario 'dados', para cada região com o consumo total calculado
            dados.append({"Região": regiao, "Consumo Total": total})
    dfRegioes = pd.DataFrame(dados)
    figuraGrafico3 = px.pie(
        dfRegioes,
        names="Região",
        values="Consumo Total",
        title = "Consumo total por Região"
        )
    return figuraGrafico3.to_html() + "<br><a href='/'>Voltar</a>"

#grafico 4 comparativo entre os tipos de bebidas
@app.route('/grafico4')
def grafico4():
    with sqlite3.connect(caminhobanco) as conn:
        df = pd.read_sql_query("""
        SELECT beer_servings, spirit_servings, wine_servings FROM bebidas
        """,conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo','Média']
        figuraGrafico4 = px.pie(
            medias,
            names='Tipo',
            values='Média',
            title='Proporção média entre os tipos de bebidas'
        )
        return figuraGrafico4.to_html() + "<br><a href='/'>Voltar</a>"

@app.route("/comparar", methods=['GET','POST'])
def comparar():
    opcoes = ['beer_servings','spirit_servings','wine_servings', 'total_litres_of_pure_alcohol']

    if request.method == "POST":
        #logica para mostrar o grafico quando tem post ao acessar a página
        eixo_x = request.form.get('eixo_x')
        eixo_y = request.form.get('eixo_y')
        if eixo_x == eixo_y:
            return "<h3>Selecione campos diferentes!</h3>"
        
        conn = sqlite3.connect(caminhobanco)
        df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixo_x,eixo_y), conn)
        conn.close()
        figuraComparar = px.scatter(
            df,
            x = eixo_x,
            y = eixo_y,
            title= f'Comparação entre {eixo_x} e {eixo_y}'
        )
        figuraComparar.update_traces(textposition='top center')
        return figuraComparar.to_html() + "<br><a href='/'>Voltar</a>"

    #aqui é a pagina sem post, ou seja, a primeira vez que o usuario entrar na pagina
    return render_template_string('''
        <h2>Comparar Campos</h2>
        <form method="POST">
            <label>Eixo X:</label>
            <select name="eixo_x">
                {% for opcao in opcoes %}  
                    <option value="{{opcao}}">{{opcao}}</option> 
                {% endfor %}                  
            </select>
            <br><br>                 
            <label>Eixo Y:</label>
            <select name="eixo_y">
                {% for opcao in opcoes %}  
                    <option value="{{opcao}}">{{opcao}}</option> 
                {% endfor %}  
            </select>
            <br><br>
            <input type="submit" value="-- Comparar --">
        </form>
    ''', opcoes = opcoes)

@app.route("/upload_avengers", methods=['GET','POST'])
def upload_avengers():
    if request.method == "POST":
        #recebi um arquivo (temos o post), então vamos cadastrar no banco
        recebido = request.files['arquivo']
        if not recebido:
            return "<h3>Nenhum arquivo recebido</h3><br><a href='/upload_avengers'>Voltar</a>"
        dfAvengers = pd.read_csv(recebido, encoding='latin1')
        conn = sqlite3.connect(caminhobanco)
        dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        return "<h3>Arquivo inserido com sucesso! </h3><br><a href='/'>Voltar</a>"
    #acessar esta rota pela primeira vez (sem post) cai nesse html
    return '''
        <h2>Upload da tabela Avengers</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="arquivo" accept=".csv"><br>
            <input type="submit" value="-- Enviar --">
        </form>
    '''

@app.route('/ver vingadores')
def ver_vingadores():
    conn = sqlite3.connect(caminhobanco)
    try:
        dfAvengers = pd.read_sql_query(queryVerVingadores, conn)
    except Exception as erro:
        conn.close()
        return f"<h3> Erro ao consultar tabela: {str(erro)} </h3><br><a href='/'>Voltar</a>"
    if dfAvengers.empty:
        return "<h3> A tabela de Vigadores está vazia ou não existe </h3><br><a href='/'>Voltar</a>"
    return dfAvengers.to_html(index=False) + "<br><a href='/'>Voltar</a>"

@app.route('/apagar_avengers')
def apagar_avengers():
    conn = sqlite3.connect(caminhobanco)
    cursor = conn.cursor()
    try:
        cursor.execute(apagarVingadores)
        conn.commit()
        mensagem = "<h3>Tabela Vingadores apagada com sucesso!</h3>"
    except Exception as erro:
        mensagem = "<h3>Erro ao apagar a tabela!!</h3>"
    conn.close()
    return mensagem + "<br><a href= '/'>Voltar</a>"



#iniciar o servidor 
if __name__ == '__main__':
    app.run(debug=True)