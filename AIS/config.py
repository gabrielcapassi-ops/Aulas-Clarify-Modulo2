#   ____ ___  _   _ _____ ___ ____ 
#  / ___/ _ \| \ | |  ___|_ _/ ___|
# | |  | | | |  \| | |_   | | |  _ 
# | |__| |_| | |\  |  _|  | | |_| |
#  \____\___/|_| \_|_|   |___\____|
'''
Autor: Gabriel Capassi
Data 27-08-2025
V: 1.0
'''

DB_PATH = "bancodedadosAIS.db"
FLASK_DEBUG = True
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000

ROTAS = [
    '/',
    '/upload',
    '/consultar',
    '/graficos',
    '/editar_inadimplencia',
    '/correlacao',
    '/grafico3d',
    '/editar_selic'
    ]