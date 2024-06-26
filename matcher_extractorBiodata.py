import spacy
from spacy import displacy
from spacy.matcher import Matcher
from datetime import date

def setup_matcher(nlp):
    matcher = Matcher(nlp.vocab)

    # Para el nombre completo de la persona
    pattern = [
        {'POS': 'PROPN', 'DEP': 'nsubj'},
        {'POS': 'PROPN', 'OP': '*'},
        {'IS_PUNCT': True, 'TEXT': '('}
    ]
    matcher.add('nombre_completo', [pattern])

    # Para el lugar de nacimiento
    pattern = [
        {'IS_PUNCT': True, 'TEXT': '('},
        {'POS': 'PROPN', 'OP': '*'}, # Ciudad
        {'IS_PUNCT': True, 'OP': '?', 'TEXT': {'IN': [',', ';']}},
        {'POS': 'PROPN', 'OP': '*'}, # Provincia o estado
        {'IS_PUNCT': True, 'OP': '?', 'TEXT': {'IN': [',', ';']}},
        {'POS': 'PROPN', 'OP': '*'}, # País
        {'IS_PUNCT': True, 'TEXT': {'IN': [',', ';']}}
    ]
    matcher.add('lugar_de_nacimiento', [pattern])

    # Para el lugar de defunción
    pattern = [
        {'IS_PUNCT': True, 'TEXT': '-'},
        {'POS': 'PROPN', 'OP': '*'}, # Ciudad
        {'IS_PUNCT': True, 'OP': '?', 'TEXT': {'IN': [',', ';']}},
        {'POS': 'PROPN', 'OP': '*'}, # Provincia o estado
        {'IS_PUNCT': True, 'OP': '?', 'TEXT': {'IN': [',', ';']}},
        {'POS': 'PROPN', 'OP': '*'}, # País
    ]
    matcher.add('lugar_de_nacimiento', [pattern])

    # Para las fechas
    pattern = [
        {'POS': 'NUM'}, # Día
        {'POS': 'ADP', 'LOWER': 'de'},
        {'POS': 'NOUN'}, # Mes
        {'POS': 'ADP', 'LOWER': 'de'},
        {'POS': 'NUM'} # Año
    ]
    matcher.add('fecha', [pattern])

    return matcher

def string_to_date(fecha_string):
    fecha_split = fecha_string.split()
    day = int(fecha_split[0])
    year = int(fecha_split[4])
    
    meses = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')
    if fecha_split[2].lower() == 'setiembre':
        return 9
    else:
        try:
            month = meses.index(fecha_split[2].lower()) + 1
        except ValueError:
            return None
    
    return date(year, month, day)

def extraer_biodata(texto, nlp, matcher):
    persona = {
        'nombre_completo': '',
        'lugar_de_nacimiento': False,
        'fecha_de_nacimiento': False,
        'lugar_de_defunción': False,
        'fecha_de_defunción': False
    }

    doc = nlp(texto)
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        if string_id == 'nombre_completo':
            persona['nombre_completo'] = doc[start:end-1]
        elif string_id == 'lugar_de_nacimiento':
            persona['lugar_de_nacimiento'] = doc[start+1:end-1]
        elif string_id == 'lugar_de_defuncion':
            persona['lugar_de_defunción'] = doc[start+1:end]
        elif persona['fecha_de_nacimiento'] == False:
            persona['fecha_de_nacimiento'] = string_to_date(str(doc[start:end]))
        else:
            persona['fecha_de_defunción'] = string_to_date(str(doc[start:end]))
    
    return persona

def imprimir_biodata(persona):
    for key, value in persona.items():
        print(f'{key}: {value}')

def main():
    nlp = spacy.load("es_dep_news_trf")
    matcher = setup_matcher(nlp)

    # Ejemplos: Se toma solo la primera oración de la entrada de wikipedia en español
    texto = "Lionel Andrés Messi Cuccittini (Rosario, 24 de junio de 1987), conocido como Leo Messi, es un futbolista argentino que juega como delantero o centrocampista."
    lionel_messi = extraer_biodata(texto, nlp, matcher)
    imprimir_biodata(lionel_messi)

    texto = "María Elena Walsh (Villa Sarmiento, 1 de febrero de 1930 - Buenos Aires, 10 de enero de 2011) fue una poetisa, escritora, cantautora, dramaturga y compositora argentina, considerada como «mito viviente, prócer cultural y blasón de casi todas las infancias»."
    maria_elena_walsh = extraer_biodata(texto, nlp, matcher)
    imprimir_biodata(maria_elena_walsh)

    texto = "Rosa María Juana Martínez Suárez (Villa Cañás, Santa Fe; 23 de febrero de 1927), más conocida por su seudónimo Mirtha Legrand o por su apodo la Chiqui, es una actriz y conductora de televisión argentina."
    mirtha_legrand = extraer_biodata(texto, nlp, matcher)
    imprimir_biodata(mirtha_legrand)

    texto = "Shigeru Miyamoto (宮本 茂 Miyamoto Shigeru?) (Kioto, 16 de noviembre de 1952) es un diseñador y productor de videojuegos japonés que trabaja para Nintendo desde 1977."
    shigeru_miyamoto = extraer_biodata(texto, nlp, matcher)
    imprimir_biodata(shigeru_miyamoto)

    texto = "Britney Jean Spears (McComb, Misisipi, 2 de diciembre de 1981) es una cantante, bailarina, compositora, modelo, actriz, diseñadora de moda, autora y empresaria estadounidense."
    britney_spears = extraer_biodata(texto, nlp, matcher)
    imprimir_biodata(britney_spears)

    texto = "Michael Joseph Jackson (Gary, Indiana, 29 de agosto de 1958 - Los Ángeles, 25 de junio de 2009) fue un cantante, compositor, productor y bailarín estadounidense."
    michael_jackson = extraer_biodata(texto, nlp, matcher)
    imprimir_biodata(michael_jackson)
main()