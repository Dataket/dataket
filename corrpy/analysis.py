"""Funciones para el análisis de los datos"""

# Se importan las librerías para el análisis de datos
import pandas as pd
import numpy as np
from scipy import stats

# Librerías para graficar
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objects as go
from .navigation import consultas, limpia_declaraciones

# Para ML
from sklearn.cluster import KMeans

# Se define la paleta de colores de Dataket 8)
colors = ["#264653", "#2a9d8f", "#e9C46a", "#F4A261", "#E76F51"]


def declaracion_personal(curp, variable_x="anio", variable_y="valor_neto"):
    """Se crean un par de arreglos a partir de las variables  indicadas

    Args:
        df_curp ([type]): [description]
        df_declaraciones ([type]): [description]
        curp ([type]): [description]
        variable_x (str, optional): [description]. Defaults to "anio".
        variable_y (str, optional): [description]. Defaults to "valor_neto".

    Returns:
        [type]: [description]
    """

    # Cargamos dataframes de navegación
    df_curp = consultas()
    df_declaraciones = limpia_declaraciones()

    # Se revisa que el curp exista en las declaraciones
    if len(df_curp.loc[curp]["Declaraciones"]) > 0:
        # Se construyen las listas
        valores = []
        anios = []
        for i in range(len(df_curp.loc[curp]["Declaraciones"])-1):
            anio = df_declaraciones.iloc[df_curp.loc[curp]
                                         ["Declaraciones"][i]][variable_x]
            valor = df_declaraciones.iloc[df_curp.loc[curp]
                                          ["Declaraciones"][i]][variable_y]

            anios.append(anio)
            valores.append(valor)
        return anios[:], valores[:]


def grafica_serie_temporal(anio, valor, cadena, path = 'html_viz/'):
    """Regresión lineal de una serie temporal

    Se crea la gráfica de un par de arreglos y se les hace un ajuste
    lineal por mínimos cuadrados y otro por el método de Theil-Sen

    Args:
        anio ([type]): [description]
        valor ([type]): [description]
        cadena ([type]): [description]
    """
    # Se revisa que el curp exista en las declaraciones
    if len(anio) == len(valor) and len(anio) > 1:
        auxiliar = pd.DataFrame({'Anio': np.array(anio),
                                 'Valor': np.array(valor)}).sort_values(by=['Anio']).reset_index()
        anio_minimo = auxiliar["Anio"].min()

        if len(auxiliar[auxiliar["Anio"] == anio_minimo]) > 1:
            auxiliar = auxiliar.drop(0)

        # Ajuste lineal
        ajuste = np.polyfit(auxiliar["Anio"]-anio_minimo,
                            auxiliar["Valor"], 1)  # Mínimos cuadrados
        recta = np.poly1d(ajuste)

        theil = stats.theilslopes(auxiliar["Valor"],
                                  auxiliar["Anio"]-anio_minimo, 0.10)  # Regresión de Theil-Sen

        # Se grafica la serie de tiempo
        fig = px.line(auxiliar, x="Anio", y="Valor",
                      color_discrete_sequence=[colors[1]],
                      title=f"Serie temporal del valor de {cadena}",
                      labels={"Anio": "Año", "Valor": f"Valor de {cadena} (MXN)"})

        # Se grafica la recta por mínimos cuadrados
        # Se evita que el ajuste no esté definido
        if (auxiliar["Valor"].diff()!=0).sum()>1:
            fig.add_trace(go.Line(x=auxiliar["Anio"],
                          y=recta(auxiliar["Anio"]-anio_minimo),
                          showlegend=False,
                          line=dict(color=colors[0], width=3)))
        # Se grafica la recta de Theil-Sen
        fig.add_trace(go.Line(x=auxiliar["Anio"],
                      y=theil[1]+theil[0]*(auxiliar["Anio"]-anio_minimo),
                      showlegend=False,
                      line=dict(color=colors[2], width=3)))

        # Se ajusta el tamaño de la letra
        fig.update_layout(font_size=15)

        # Se guarda el html para poder usarlo en la página web de Dataket 8)
        plotly.offline.plot(fig,
        filename=path+'scatter_'+cadena.replace(" ", "")+'.html')

        # Se muestra la imagen
        fig.show()

def declaracion_muestra(df_sobre_declaraciones, variable_x, variable_y):
    """Se realiza una muestra para hacer comparaciones entre las varianzas

    Args:
        df_sobre_declaraciones ([type]): [description]
        variable_x ([type]): [description]
        variable_y ([type]): [description]

    Returns:
        [type]: [description]
    """

    lista = []
    for curp in set(df_sobre_declaraciones["curp"]):

        anio, valor = declaracion_personal(curp, variable_x, variable_y)

        # Se eliminan los datos que repiten año
        auxiliar = pd.DataFrame({'Anio': np.array(anio),
                                 'Valor': np.array(valor)}).sort_values(by=['Anio']).reset_index()
        anio_minimo = auxiliar["Anio"].min()
        if len(auxiliar[auxiliar["Anio"] == anio_minimo]) > 1:
            auxiliar = auxiliar.drop(0).reset_index()

        # Aquí se realiza la revisión de la métrica a usar
        if len(valor) > 2:
            suma = 0
            for i in range(len(auxiliar["Valor"])-1):
                if auxiliar["Anio"][i+1] != auxiliar["Anio"][i]:
                    suma += abs((auxiliar["Valor"][i+1]-auxiliar["Valor"]
                                [i])/(auxiliar["Anio"][i+1]-auxiliar["Anio"][i]))
            if auxiliar["Valor"].mean() != 0:
                lista.append(abs(suma/auxiliar["Valor"].mean()))

    return np.array(lista[:])


def agrupacion(data_x, n_clusters):
    """Realiza clasificación de los datos en n_clusters grupos

    Args:
        data_x ([type]): [description]
        n_clusters ([type]): [description]
    """

    # Se prepara el algoritmo K-Means y el PCA
    kmeans = KMeans(n_clusters=n_clusters, n_init=10,
                    random_state=0, max_iter=10_000)

    # Se preparan los arrays
    X = data_x.copy()

    # Se ajusta el modelo de k-means minimizando el efecto de
    # los outliers al filtrarlos
    kmeansclus = kmeans.fit(X[X["valor_neto"].between(X["valor_neto"].quantile(.05),
                                                      X["valor_neto"].quantile(.95))])

    # Se hacen predicciones de los grupos
    y_kmeans = kmeansclus.predict(X)
    X["grupo"] = y_kmeans

    # Se grafica el pairplot
    sns.pairplot(hue="grupo", data=X)


def declaracion_pvalue(df_curp, curp, variable):
    """Se calcula el p-value del registro en la distribución de la variable dada

    Args:
        df_curp ([type]): [description]
        curp ([type]): [description]
        variable ([type]): [description]

    Returns:
        [type]: [description]
    """

    if curp in set(df_curp["curp"]):
        columna = df_curp[variable]
        registro = df_curp[df_curp["curp"]==curp][variable].iloc[0]
        # Se promedia el número de registros de la muestra superiores
        # al estadístico de prueba
        return len(columna[columna<registro])/len(columna), len(columna[columna>registro])/len(columna)
