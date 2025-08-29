#Mapa interativo de Custos (NY x RIO) com pontos e mapa de calor

import pandas as pd
import numpy as np
import plotly.graph_objs as go

#Utilização de padronização

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tentar detectar automaticamente as colunas latitude e longitude, custos e nome.
    Aceita varios nomes comum como lat/latitude custo, valor e etc preenche custos ausentes com a medina (ou 1 se tudo tiver ausente)
    """
    df = df.copy()

    lat_candidates = ['lat', 'latitude', 'Latitude','LAT', 'Lat''LATITUDE']
    lon_candidates = ['lon', 'longitude', 'Longitude', 'LON', 'Lon', 'LONGITUDE']
    cost_candidates =['custo','valor','preço', 'preco','cost','valor_total', 'price']
    name_candidates =['nome', 'descricao', 'titulo', 'name', 'title', 'local','place']

    def pick(colnames, candidates):

        # colnames: lista de nomes das colinas da tabela
        # candidates: lista de possiveis nomes de colunas a serem encontrados
        for c in candidates:
            # percorre cada candidato (c) dentro da lista de candidatos
            if c in colnames:
                #se o candidato for exatamente igual a um dos nomes colnames...
                return c
            #...retorna esse candidato imediatamente
        for c in candidates:
            #se nao encontrou  a correspondencia exata
            #percorre novamente cada candidato
            for col in colnames:
                #Aqui percorre cada nome de coluna
                if c.lower() in col.lower():
                    #faz igual o de cima, mas trabalhando em minisculos apenas
                    return col
        return None
    
        #se nao encontrou nada nem exato nem parcial retorna none (nenhum match encontrado)
    lat_col = pick(df.columns, lat_candidates)
    lon_col = pick(df.columns, lon_candidates)
    cost_col = pick(df.columns, cost_candidates)
    name_col = pick(df.columns, name_candidates)

    if lat_col is None or lon_col is None:
        raise ValueError(f"Não encontrei colunas de latitude e longitude {list(df.columns)}")
    
    out = pd.DataFrame()
    out['lat'] = pd.to_numeric(df[lat_col], errors='coerce')
    out['lon'] = pd.to_numeric(df[lon_col], errors='coerce')
    out['custo'] = pd.to_numeric(df[cost_col], errors='coerce') if cost_col is not None else np.nan
    out['nome'] = df[name_col].astype(str) if name_col is not None else [f"Ponto{i}" for i in range(len(df))]

    #remove linhas coordenadas
    out = out.dropna(subset=['lat','lon']).reset_index(drop=True)

    #preenche o custo ausente
    if out['custo'].notna():
        med = float(out['custo'].median())
        if not np.isfinite(med):
            med = 1.0
        out['custo'] = out['custo'].fillna(med)
    else: 
        out['custo'] = 1.0
    return out

def city_center(df: pd.DataFrame) -> dict:
    """
    define a funcao city_center
    - recebe como parametro um dataframe o pandas (df)
    - deve retornar um dicionario (-> dict)
    """
    return dict(
        #calcula a media da coluna
        lat = float(df['lat'].mean()),
        lon = float(df['lon'].mean())
    )

#--------------------------Traces------------------------------------
def make_point_trace(df:pd.DataFrame,name:str)->go.Scattermapbox:
    hover = ("<b>${customdata[0]}</b><br>"
             "Custo: %{customdata[1]}<br>"
             "Lat: %{lat:.5f}<br>Lon: %{lon:.5f}")
    # tamanho dos marcadores (normalizados pelo custo)
    c = df["custo"].astype(float).values
    c_min, c_max = float(np.min(c), np.max(c))

    #Caso Especial: se nao existitem valores numericos validos ou se todos os custos forem praticamente iguais (diferenca < 1e-9) cria um array de tamanhos fixos 10 para todos os pontos
    if not np.isfinite(c_min) or not np.isfinite(c_max) or abs(c_max - c_min) < 1e-9:
        size = np.full_like(c, 10.0, dtype=float)
    else:
    #Caso normal: normaliza os custos para o intervalo [0,1] e escala para variar entre 6 e 26 (20 de amplitude mais deslocsamento de 6)
    #pontos de custo baixo ~6, pontos de custo alto ~26
        size = (c - c_min) / (cmax - c_min) * 20 + 6
    #mesmo que os dados estejam fora da faixa de 6 a 26 ele evita sua apresentação, forçando a ficar entre o intervalo

    sizes = np.clip(size, 6, 26)

    custom = np.stack([df['nome'].values, df['custo'].values], axis=1)

    return go.Scattermapbox(
        lat = df['lat'],
        lon =df['lon'],
        mode = 'markers',
        marker = dict(
            size = sizes,
            color = df['custo'],
            colorscale = "Virids",
            colorbar = dict(title='Custo')
        ),
        name = f"{name} • Pontos",
        hovertemplate= hover,
        customdata = custom
    )

def make_density_trace(df: pd.DataFrame, name: str) -> go.Densitymapbox:
    return go.Densitymapbox(
        lat = df['lat'],
        lon = df['lon'],
        z = df['custo'],
        radius = 20,
        colorscale = "Inferno",
        name = f"{name} • Pontos",
        showscale = True,
        colorbar = dict(title='Custo')
    )

#-----------------------------------MAIN-------------------------------
def main():
    #carrega e padroniza os dados
    folder = "C:/Users/integral/Desktop/Python 2 Gabriel/Sistema/"
    ny = standardize_columns(pd.read_csv(f'{folder}ny.csv'))
    rj = standardize_columns(pd.read_csv(f'{folder}rj.csv'))

    #Cria os quatro traces (ny pontos / ny calor / rio pontos / rio calor)
    ny_point = make_point_trace(ny, "Nova York")
    ny_heat = make_density_trace(ny,"Nova York" )
    rj_point = make_point_trace(rj, "Rio de Janeiro")
    rj_heat = make_density_trace(rj,"Rio de Janeiro" )

    fig = go.Figure([ny_point, ny_heat, rj_point, rj_heat])

    def center_zoom(df, zoom):
        return dict(center=city_center(df), zoom=zoom)
    #dropdown simples com quatro opções (cidade x visualização)
    buttons =[
        dict(
            label = "Nova York • Pontos",
            method ="update",
            arg = [
                {"visible":[True, False, False, False]},
                {"mapbox": center_zoom(ny, 9)}
            ]
        ),
         dict(
            label = "Nova York • Calor",
            method ="update",
            arg = [
                {"visible":[False, True, False, False]},
                {"mapbox": center_zoom(ny, 9)}
            ]
        ),
         dict(
            label = "Rio de Janeiro • Pontos",
            method ="update",
            arg = [
                {"visible":[False, False, True, False]},
                {"mapbox": center_zoom(rj, 10)}
            ]
        ),
         dict(
            label = "Rio de Janeiro • Calor",
            method ="update",
            arg = [
                {"visible":[False, False, False, True]},
                {"mapbox": center_zoom(rj, 10)}
            ]
        )

    ]

    fig.update_layout(
        title = "Mapa Interativo de Custos - Pontos e Mapa de Calor",
        mapbox_style = "open-street-map",
        mapbox = dict(center=city_center(rj), zoom=10),
        margin = dict(l=10, r=10, t=50, b=10),
        updatemenus = [dict(
            buttons = buttons,
            direction = "down",
            x = 0.01,
            y = 0.99,
            xanchor = "left", 
            yanchor = "top",
            bgcolor = "white",
            bordercolor = "lightgray"

        )],
        legend = dict(
            orientation = "h",
            yanchor = "bottom",
            xanchor = "right",
            y = 0.01,
            x = 0.99
        )
    )

    #Salva HTML de apresentação
    fig.write_html(
        f"{folder}mapa_custos_interativo",
        include_plotlyjs = "cdn",
        full_html = True
    )
    print(f"Arquivo Gerado com Sucesso em {folder} mapa_custos_interativo.html")

# Inicia o servidor
if __name__ == '__main__':
    main()