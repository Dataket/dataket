"""Funciones para navegación y limpieza de los datos"""

# Para hacer lectura de archivos json
import json
# Para revisar si los archivos existen en la dirección indicada
from os.path import exists

# Se importan las librerías para el análisis de datos
import pandas as pd
import numpy as np

# Se define la paleta de colores de Dataket 8)
colors = ["#264653", "#2a9d8f", "#e9C46a", "#F4A261", "#E76F51"]

# Se define una función para leer un json a partir de una direccion


def leer_json(direccion):
    """[summary]

    Args:
        direccion ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Se lee el archivo desde su dirección y se guarda en un diccionario
    with open(direccion, 'r') as file:
        data = json.loads(file.read())
    return data


declaraciones = leer_json("data/declaraciones.json")
contratos = leer_json("data/SistemaS2.json")
multas = leer_json("data/Sistema3Servidores.json")


def consultas(path='bin/relations.pkl'):
    """Crea dataframe con listas de id's de declaraciones y contratos para un mismo curp

    Args:
        path (str, optional): [description]. Defaults to 'bin/relations.pkl'.

    Returns:
        [type]: [description]
    """
    if not exists(path):
        # Obtenemos curps individuales (numero de servidores públicos)

        curps = []

        for multa in multas:
            curps.append(multa['servidorPublicoSancionado']['curp'])

        for contrato in contratos:
            curps.append(contrato['curp'])

        for declaracion in declaraciones:
            curps.append(
                declaracion['declaracion']['situacionPatrimonial']['datosGenerales']['curp'])

        curps = set(curps)

        print(f"Tenemos registros de {len(curps)} personas.")

        # Dataframe para indices por persona.

        aux = []
        for i in range(len(curps)):
            aux.append([[], [], []])

        df_curps = pd.DataFrame(aux, index=curps, columns=[
                                'Multas', 'Declaraciones', 'Contratos'])

        for curp in curps:
            for i, multa in enumerate(multas):
                if multa['servidorPublicoSancionado']['curp'] == curp:
                    df_curps.at[curp, 'Multas'].append(i)

            for i, declaracion in enumerate(declaraciones):
                if declaracion['declaracion']['situacionPatrimonial']['datosGenerales']['curp'] == curp:
                    df_curps.at[curp, 'Declaraciones'].append(i)

            for i, contrato in enumerate(contratos):
                if contrato['curp'] == curp:
                    df_curps.at[curp, 'Contratos'].append(i)

        df_curps.to_pickle(path)
        return df_curps

    else:
        df_curps = pd.read_pickle(path)
        return df_curps


def limpia_declaraciones(path='bin/declaraciones.pkl'):
    """Crea dataframe de declaraciones con valores de interés.

    Args:
        path (str, optional): [description]. Defaults to 'bin/declaraciones.pkl'.

    Returns:
        [type]: [description]
    """
    # DataFrame para consultas por CURP
    df = consultas()

    if not exists(path):

        # Se obtienen las columnas más importantes de las Declaraciones para facilitar
        # las consultas
        tabla = []
        for declaracion in declaraciones:
            # En esta lista se guardaran los datos relevantes del registro actual
            lista = []

            # id
            lista.append(declaracion["id"])
            # Año
            lista.append(int(declaracion["metadata"]["actualizacion"][:4]))
            # CURP
            lista.append(declaracion["declaracion"]
                        ["situacionPatrimonial"]["datosGenerales"]["curp"])

            # Nombre y apellidos
            lista.append(declaracion["declaracion"]
                        ["situacionPatrimonial"]["datosGenerales"]["nombre"])
            lista.append(declaracion["declaracion"]
                        ["situacionPatrimonial"]["datosGenerales"]["primerApellido"])
            lista.append(declaracion["declaracion"]
                        ["situacionPatrimonial"]["datosGenerales"]["segundoApellido"])

            # Nivel de escolaridad
            lista.append(declaracion["declaracion"]["situacionPatrimonial"]
                        ["datosCurricularesDeclarante"]["escolaridad"][-1]["nivel"]["clave"])
            # Nivel de orden de gobierno
            lista.append(declaracion["declaracion"]["situacionPatrimonial"]
                        ["datosEmpleoCargoComision"]["nivelOrdenGobierno"])
            # Nombre del ente público
            lista.append(declaracion["declaracion"]["situacionPatrimonial"]
                        ["datosEmpleoCargoComision"]["nombreEntePublico"])

            # Tiene pareja
            try:
                try:
                    # Ojo: dice "nunguno" en lugar de "ninguno"
                    if not declaracion["declaracion"]["situacionPatrimonial"]["datosPareja"]["nunguno"]:
                        lista.append(1)  # Sí tiene pareja
                    else:
                        lista.append(0)  # No tiene pareja
                except:
                    # Ojo: dice "nunguno" en lugar de "ninguno"
                    if not declaracion["declaracion"]["situacionPatrimonial"]["datosPareja"]["ninguno"]:
                        lista.append(1)  # Sí tiene pareja
                    else:
                        lista.append(0)  # No tiene pareja
            except:
                lista.append(0)

            # Número de dependientes económicos
            try:
                try:
                    # Ojo: dice "nunguno" en lugar de "ninguno"
                    if not declaracion["declaracion"]["situacionPatrimonial"]["datosDependienteEconomico"]["nunguno"]:
                        lista.append(len(declaracion["declaracion"]["situacionPatrimonial"]
                                    ["datosDependienteEconomico"]["dependienteEconomico"]))  # Sí tiene dependientes
                    else:
                        lista.append(0)  # No tiene dependientes
                except:
                    # Ojo: dice "nunguno" en lugar de "ninguno"
                    if not declaracion["declaracion"]["situacionPatrimonial"]["datosDependienteEconomico"]["ninguno"]:
                        lista.append(len(declaracion["declaracion"]["situacionPatrimonial"]
                                    ["datosDependienteEconomico"]["dependienteEconomico"]))  # Sí tiene dependientes
                    else:
                        lista.append(0)
            except:
                lista.append(0)

            # Remuneración del cargo público
            try:
                valor = declaracion["declaracion"]["situacionPatrimonial"]["ingresos"]["remuneracionMensualCargoPublico"]["valor"]
                lista.append(12*valor)
            except:
                try:
                    valor = declaracion["declaracion"]["situacionPatrimonial"][
                        "ingresos"]["remuneracionConclusionCargoPublico"]["valor"]
                    lista.append(valor)
                except:
                    try:
                        valor = declaracion["declaracion"]["situacionPatrimonial"][
                            "ingresos"]["remuneracionAnualCargoPublico"]["valor"]
                        lista.append(valor)
                    except:
                        lista.append(0)

            # Ingreso anual promedio
            try:
                valor = declaracion["declaracion"]["situacionPatrimonial"]["ingresos"]["totalIngresosMensualesNetos"]["valor"]
                lista.append(12*valor)
            except:
                try:
                    valor = declaracion["declaracion"]["situacionPatrimonial"]["ingresos"]["totalIngresosAnualesNetos"]["valor"]
                    lista.append(valor)
                except:
                    try:
                        valor = declaracion["declaracion"]["situacionPatrimonial"]["ingresos"]["ingresoAnualNetoDeclarante"]["valor"]
                        lista.append(valor)
                    except:
                        valor = declaracion["declaracion"]["situacionPatrimonial"][
                            "ingresos"]["totalIngresosConclusionNetos"]["valor"]
                        lista.append(valor)

            # Valor total de bienes inmuebles.
            try:
                if not declaracion["declaracion"]["situacionPatrimonial"]["bienesInmuebles"]["ninguno"]:
                    propiedades = 0
                    for propiedad in declaracion["declaracion"]["situacionPatrimonial"]["bienesInmuebles"]["bienInmueble"]:
                        try:
                            propiedades += propiedad["valorAdquisicion"]["valor"]
                        except:
                            propiedades += propiedad["valorAdquisicion"]
                    lista.append(propiedades)
                else:
                    lista.append(0)
            except:
                lista.append(0)

            # Valor total de adquisición de vehículos.
            try:
                if not declaracion["declaracion"]["situacionPatrimonial"]["vehiculos"]["ninguno"]:
                    propiedades = 0
                    for propiedad in declaracion["declaracion"]["situacionPatrimonial"]["vehiculos"]["vehiculo"]:
                        try:
                            propiedades += propiedad["valorAdquisicion"]["valor"]
                        except:
                            propiedades += propiedad["valorAdquisicion"]
                    lista.append(propiedades)
                else:
                    lista.append(0)
            except:
                lista.append(0)

            # Valor total de bienes muebles
            try:
                if not declaracion["declaracion"]["situacionPatrimonial"]["bienesMuebles"]["ninguno"]:
                    propiedades = 0
                    for propiedad in declaracion["declaracion"]["situacionPatrimonial"]["bienesMuebles"]["bienMueble"]:
                        try:
                            propiedades += propiedad["valorAdquisicion"]["valor"]
                        except:
                            propiedades += propiedad["valorAdquisicion"]
                    lista.append(propiedades)
                else:
                    lista.append(0)
            except:
                lista.append(0)

            # Valor total de inversiones (saldo diciembre anterior*rendimiento).
            try:
                if not declaracion["declaracion"]["situacionPatrimonial"]["inversiones"]["ninguno"]:
                    propiedades = 0
                    for propiedad in declaracion["declaracion"]["situacionPatrimonial"]["inversiones"]["inversion"]:
                        try:
                            propiedades += (1+int(propiedad["porcentajeIncrementoDecremento"]
                                            [:-1])/100)*propiedad["saldoDiciembreAnterior"]["valor"]
                        except:
                            try:
                                propiedades += propiedad["saldoSituacionActual"]["valor"]
                            except:
                                propiedades += propiedad["saldoFechaConclusion"]["valor"]
                    lista.append(propiedades)
                else:
                    lista.append(0)
            except:
                lista.append(0)

            # Valor total de deudas (saldo diciembre anterior*rendimiento)
            try:
                if not declaracion["declaracion"]["situacionPatrimonial"]["adeudos"]["ninguno"]:
                    propiedades = 0
                    for propiedad in declaracion["declaracion"]["situacionPatrimonial"]["adeudos"]["adeudo"]:
                        try:
                            variable = (1+int(propiedad["porcentajeIncrementoDecremento"][:-1]) /
                                        100)*propiedad["saldoInsolutoDiciembreAnterior"]["valor"]
                            propiedades += variable
                        except:
                            try:
                                variable = propiedad["saldoInsolutoSituacionActual"]["valor"]
                                propiedades += variable
                            except:
                                variable = propiedad["saldoInsolutoFechaConclusion"]["valor"]
                                propiedades += variable

                    lista.append(propiedades)
                else:
                    lista.append(0)
            except:
                lista.append(0)

            # Valor de propiedades
            lista.append(lista[-3]+lista[-4]+lista[-5])

            # Valor con inversiones
            lista.append(lista[-1]+lista[-3])

            # Valor neto (Valor con inversiones menos deudas)
            lista.append(lista[-1]-lista[-3])

            # Ha tenido sanciones
            if len(df.loc[lista[2]]["Multas"]) == 0:
                lista.append(0)  # No se le ha sancionado
            else:
                lista.append(1)  # Se le ha sancionado

            # Se guarda el registro
            tabla.append(lista)

        df_declaraciones = pd.DataFrame(tabla, columns=["id", "anio", "curp", "nombre", "primerApellido",
                                                        "segundoApellido", "nivelEducativo",
                                                        "ordenGobierno", "entePublico", "pareja",
                                                        "numeroDependientes", "remuneracionCargo",
                                                        "ingresosAnuales", "bienesInmuebles",
                                                        "vehiculos", "bienesMuebles", "inversiones",
                                                        "adeudos", "propiedades", "propiedades_inversiones",
                                                        "valor_neto", "multas"])

        df_declaraciones.to_pickle(path)
        return df_declaraciones

    else:
        # Si ya se ha creado el dataframe, se regresa el mismo
        df_declaraciones = pd.read_pickle(path)
        return df_declaraciones


def agrupar_curp(path='bin/curp.pkl'):
    """Crea dataframe de información condensada por CURP.

    Args:
        path (str, optional): [description]. Defaults to 'bin/curp.pkl'.

    Returns:
        [type]: [description]
    """
    df = consultas()
    df_declaraciones = limpia_declaraciones()

    if not exists(path):

        # Se agrupan las columnas más importantes de las Declaraciones para facilitar
        # las consultas por persona

        tabla = []
        for curp in df.index:
            if curp in set(df_declaraciones["curp"]):
                # Los registros a analizar
                registros = df_declaraciones[df_declaraciones["curp"] == curp].sort_values(by=[
                    'anio']).reset_index()
                anio_minimo = registros["anio"].min()
                if len(registros[registros["anio"] == anio_minimo]) > 1:
                    registros = registros.drop(0).reset_index()
                numero = len(registros)

                # curp
                lista = [curp]

                # Nivel educativo promedio
                sublista = []
                for nivel in registros["nivelEducativo"]:
                    if nivel == "LIC":
                        sublista.append(1)
                    elif nivel == "ESP":
                        sublista.append(2)
                    elif nivel == "MAE":
                        sublista.append(3)
                    else:
                        sublista.append(4)
                lista.append(np.array(sublista).mean())

                # Orden de gobierno promedio
                sublista = []
                for nivel in registros["ordenGobierno"]:
                    if nivel == "MUNICIPAL_ALCALDIA":
                        sublista.append(1)
                    elif nivel == "ESTATAL":
                        sublista.append(2)
                    else:
                        sublista.append(3)
                lista.append(np.array(sublista).mean())

                # Número de pareja promedio
                sublista = registros["pareja"]
                lista.append(np.array(sublista).mean())

                # Número de dependientes promedio
                sublista = registros["numeroDependientes"]
                lista.append(np.array(sublista).mean())

                if numero >= 3:
                    # Variación de los ingresos anuales
                    sublista = registros["ingresosAnuales"].iloc[:]
                    lista.append(sublista.std()/sublista.mean())
                    subvalor = np.array(sublista).mean()
                    # Remuneración del cargo más reciente normalizada al ingreso anual promedio
                    lista.append(
                        registros["remuneracionCargo"].iloc[-1]/subvalor)
                else:
                    # Variación de los ingresos anuales
                    subvalor = registros["ingresosAnuales"].iloc[-1]
                    lista.append(0)
                    # Remuneración del cargo más reciente normalizada al ingreso anual promedio
                    lista.append(
                        registros["remuneracionCargo"].iloc[-1]/subvalor)

                # Variación estandarizada del valor de los bienes inmuebles
                try:
                    sublista = registros["bienesInmuebles"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de los vehículos
                try:
                    sublista = registros["vehiculos"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de los bienes muebles
                try:
                    sublista = registros["bienesMuebles"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de las inversiones
                try:
                    sublista = registros["inversiones"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de los adeudos
                try:
                    sublista = registros["adeudos"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de las propiedades
                try:
                    sublista = registros["propiedades"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de las propiedades e inversiones
                try:
                    sublista = registros["propiedades_inversiones"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Variación estandarizada del valor de las propiedades e inversiones menos adeudos
                try:
                    sublista = registros["valor_neto"].iloc[:]
                    if len(sublista) > 2:
                        lista.append(sublista.std()/sublista.mean())
                    else:
                        lista.append(0)
                except:
                    lista.append(0)

                # Multas
                lista.append(registros["multas"].iloc[0])

                # Se guarda el registro
                tabla.append(lista)

        df_curp = pd.DataFrame(tabla, columns=["curp", "nivelEducativo",
                                               "ordenGobierno", "pareja",
                                               "numeroDependientes", "ingresosAnuales",
                                               "remuneracionCargo", "bienesInmuebles",
                                               "vehiculos", "bienesMuebles", "inversiones",
                                               "adeudos", "propiedades", "propiedades_inversiones",
                                               "valor_neto", "multas"])

        df_curp.to_pickle(path)
        return df_curp

    else:
        df_curp = pd.read_pickle(path)
        return df_curp
