'''Get relevant information from declarations.'''
import pandas as pd
import json

def create_table(path='data/'):
    '''Create a table of all declarations.'''

    with open(path + "declaraciones.json", 'r', encoding='utf-8') as file:
        declaraciones = json.load(file)

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
                    pass

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
                    pass

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
                        propiedades += (1+int(propiedad["porcentajeIncrementoDecremento"][:-1])/100
                                        )*propiedad["saldoInsolutoDiciembreAnterior"]["valor"]
                    except:
                        try:
                            propiedades += propiedad["saldoInsolutoSituacionActual"]["valor"]
                        except:
                            propiedades += propiedad["saldoInsolutoFechaConclusion"]["valor"]
                lista.append(propiedades)
            else:
                lista.append(0)
        except:
            lista.append(0)

        # TODO: Gastos totales = deltas de las propiedades.
        gastos = 0
        pass

        # TODO: Revisar que es préstamo o comodato

        # Se guarda el registro
        tabla.append(lista)

    df_declaraciones = pd.DataFrame(tabla, columns=["id", "anio", "curp", "nombre", "primerApellido",
                                                    "segundoApellido", "nivelEducativo",
                                                    "ordenGobierno", "entePublico", "pareja",
                                                    "numeroDependientes", "remuneracionCargo",
                                                    "ingresosAnuales", "bienesInmuebles",
                                                    "vehiculos", "bienesMuebles", "inversiones",
                                                    "adeudos"])

    return df_declaraciones
