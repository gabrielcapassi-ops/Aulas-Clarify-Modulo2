#   ___                   _       _        
#  / _ \ _   _  __ _ _ __| |_ ___| |_ ___  
# | | | | | | |/ _` | '__| __/ _ \ __/ _ \ 
# | |_| | |_| | (_| | |  | ||  __/ || (_) |
#  \__\_\\__,_|\__,_|_|   \__\___|\__\___/ 
#Linguagem: Quarteto
#Autor:
#Versão 28-08-2025
#Data: 28-08-2025

def interpretador(codigo, variaveis=None):
    #quebra o código em linhas
    if variaveis is None:
        #Um dicionário para armazenar as variáveis
        variaveis = {}

    def eval_texto(expr):
        partes = [p.strip() for p in expr.split("+")]
        out = ""
        for p in partes:
            if len(p) >= 2 and p[0] == '"':
                out += p[1:-1] #trecho entre as aspas
            else:
                out += str(variaveis.get(p,p)) # variavel (literal se nao existir)
        return out
    linhas = codigo.split('\n')
    for linha in linhas:
        linha = linha.strip() #Remove qualquer espaço desnecessário
        if not linha: #ignora linhas vazias
            continue

        #Se for uma linha de definir
        if linha.startswith("definir"): 
            resto = linha[7:].strip()
            if " como " not in resto:
                print(f"Erro de sintaxe: {linha}") #pega o nome da variável e o valor
                continue
            nome, valor = resto.split(" como ", 1)
            nome = nome.strip()
            valor = valor.strip()
            if len(valor) >= 2 and valor [0] == '"' and valor[1] == '"':
                valor = valor [1:-1]
            variaveis[nome] = valor           

        #Se for uma linha de mostrar
        elif linha.startswith("mostrar"):
            conteudo = linha[7:].strip()
            print(eval_texto(conteudo))

        #Se for uma estrutura condicional (se)
        elif linha.startswith("se"):
            resto = linha[3:].strip()
            if " então " not in resto:
                print(f"Erro de sintaxe: {linha}") #pega o nome da variável e o valor
                continue
            condicao, comando = resto.split(" então ", 1)                
            #Aqui podemos apenas checar se a condição é verdadeira ou falsa
            if condicao.strip() == "verdadeiro":
                interpretador(comando.strip(), variaveis) #Executa o comando dentro da condição

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
    definir nome como "lalala"
    mostrar "O nome é" + nome
    se verdadeiro então mostrar "Isso é verdadeiro"
    enquanto verdadeiro faça mostrar "Dentro do laço"
"""

interpretador(codigo)