# www.asciiart.eu
# __     __  _         _    
# \ \   / / / \       / \   
#  \ \ / / / _ \     / _ \  
#   \ V / / ___ \ _ / ___ \ 
#    \_(_)_/   \_(_)_/   \_\
#Autor: Gabriel Capassi
#Versão: 0.0.1

#Caminho da pasta
DB_PATH = "C:/Users/integral/Desktop/Python 2 Gabriel/bancodados.db"

#Consultas SQL
#---------------------------------

#Selecioa e traz todos os dados da tabela vingadores
consulta01 = 'SELECT * FROM VINGADORES'

#Seleciona os dados para gerar grafico 1
consulta02 = """
            SELECT country, total_litres_of_pure_alcohol
            FROM bebidas
            ORDER BY total_litres_of_pure_alcohol DESC
            LIMIT 10
        """

#Exclui a tabela de vingadores se existir
consulta03 = "DROP TABLE IF EXISTS vingadores"