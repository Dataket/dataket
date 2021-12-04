'''Merge databases and search for CURPs'''

from os.path import exists

import json
import pandas as pd

def get_curp(curp, path='data/relations.pkl'):
    """
    Search for a CURP in the CURP database and returns the data.
    """
    if exists(path):
        curp_db =  pd.read_pickle(path)
    else:
        curp_dataframe()
        curp_db =  pd.read_pickle(path)

    if curp in curp_db.index:
        return curp_db.loc[curp]
    else:
        return None

def curp_dataframe(path='data/'):
    """
    Returns a pandas dataframe with all the data sorted by CURP.
    """

    # Si no existe el archivo, lo creamos
    if not exists(path='relations.pkl'):

        # Carga de la bases de datos
        with open(path + "SistemaS2.json", 'r', encoding='utf-8') as file:
            contratos = json.load(file)
        with open(path + "Sistema3Servidores.json", 'r', encoding='utf-8') as file:
            multas = json.load(file)
        with open(path + "declaraciones.json", 'r', encoding='utf-8') as file:
            declaraciones = json.load(file)

        # Obtenemos los CURPs de los archivos
        curps = []

        for multa in multas:
            curps.append(multa['servidorPublicoSancionado']['curp'])

        for contrato in contratos:
            curps.append(contrato['curp'])

        for declaracion in declaraciones:
            curps.append(declaracion['declaracion']['situacionPatrimonial']
            ['datosGenerales']['curp'])

        # Eliminamos duplicados
        curps = set(curps)

        # Creamos el dataframe
        aux = []
        for i in range(len(curps)):
            aux.append([[],[],[]])
        data = pd.DataFrame(aux, index = curps, columns = ['Multas', 'Declaraciones', 'Contratos'])

        # Agregamos los datos
        for curp in curps:
            for i, multa in enumerate(multas):
                if multa['servidorPublicoSancionado']['curp'] == curp:
                    data.at[curp, 'Multas'].append(i)

            for i, declaracion in enumerate(declaraciones):
                if (declaracion['declaracion']['situacionPatrimonial']
                ['datosGenerales']['curp']) == curp:
                    data.at[curp, 'Declaraciones'].append(i)

            for i, contrato in enumerate(contratos):
                if contrato['curp'] == curp:
                    data.at[curp, 'Contratos'].append(i)


        # Guardamos el archivo
        data.to_pickle(path + 'relations.pkl')

    else:
        data = pd.read_pickle(path + 'relations.pkl')
