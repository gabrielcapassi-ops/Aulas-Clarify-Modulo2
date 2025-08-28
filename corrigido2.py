#   ___                   _       _        
#  / _ \ _   _  __ _ _ __| |_ ___| |_ ___  
# | | | | | | |/ _` | '__| __/ _ \ __/ _ \ 
# | |_| | |_| | (_| | |  | ||  __/ || (_) |
#  \__\_\\__,_|\__,_|_|   \__\___|\__\___/ 

#Linguagem: Quarteto
#Autor:
#Versão 28-08-2025
#Data: 28-08-2025

def interpretador(codigo):
    #quebra o código em linhas
    linhas = codigo.split('\n')

    #Um dicionário para armazenar as variáveis
    variaveis = {}

    for linha in linhas:
        linha = linha.strip() #Remove qualquer espaço desnecessário

        #Se for uma linha de definir
        if linha.startswith("definir"): 
            partes = linha[8:].strip().split(" como ") #pega o nome da variável e o valor
            nome = partes[0].strip()
            valor = partes[1].strip().strip('"') #remove as ""
            variaveis[nome] = valor #armazenando a variavel


        #Se for uma linha de mostrar
        elif linha.startswith("mostrar"):
            conteudo = linha[8:].strip().strip('"')
            print(conteudo)

        #Se for uma estrutura condicional (se)
        elif linha.startswith("se"):
            condicao = linha[3:].split(" então ")[0].strip()
            comando = linha.split(" então ")[1].strip()

            #Aqui podemos apenas checar se a condição é verdadeira ou falsa
            if condicao == "verdadeiro":
                interpretador(comando) #Executa o comando dentro da condição

        #Se for um laço "Enquanto"
        elif linha.startswith("enquanto"):
            condicao = linha[8:].split(" faça ")[0].strip()
            comando = linha.split(" faça ")[1].strip()

            #Verifica a condição do looping (por enquanto, consideramos verdadeiro ou falso)
            while condicao == 'verdadeiro':
                interpretador(comando) #executa o comando dentro do loop
                break #evita looks infinitos para esse exemplo

        else:
            print(f'Comando não foi reconhecido {linha}')

codigo = """
    definir como "lalala"
    mostrar o nome como é + nome
    se verdadeiro então mostrar "Isso é verdadeiro"
    enquanto verdadeiro faça mostrar "Dentro do lacço"
"""

interpretador(codigo)