import spacy
from spacy.matcher import DependencyMatcher
from spacy import displacy

# Sobre las subordinadas relativas con antecedente expreso
# https://www.rae.es/gtg/oraci%C3%B3n-subordinada-de-relativo

def setup_matcher(nlp):
    matcher = DependencyMatcher(nlp.vocab)

    pattern = [
        # Se posiciona en un posible antecedente
        {
            'RIGHT_ID': 'object',
            'RIGHT_ATTRS': {'POS': 'NOUN'}
        },
        # Busca el núcleo de la subordinada
        {
            'LEFT_ID': 'object',
            'REL_OP': '>',
            'RIGHT_ID': 'subordinate_root',
            'RIGHT_ATTRS': {'DEP': 'acl'}
        },
        # Busca el sujeto de la subordinada
        {
            'LEFT_ID': 'subordinate_root',
            'REL_OP': '>',
            'RIGHT_ID': 'subject',
            'RIGHT_ATTRS': {'LEMMA': {'NOT_IN': ['que', 'quien']}, 'DEP': 'nsubj'}
        }
    ]
    matcher.add('relativa_con_antecedente_objeto', [pattern])

    pattern = [
        # Se posiciona en un posible antecedente
        {
            'RIGHT_ID': 'subject',
            'RIGHT_ATTRS': {'POS': 'NOUN'}
        },
        # Busca el núcleo de la subordinada
        {
            'LEFT_ID': 'subject',
            'REL_OP': '>',
            'RIGHT_ID': 'subordinate_root',
            'RIGHT_ATTRS': {'DEP': 'acl'}
        },
        # Busca el sujeto de la subordinada
        {
            'LEFT_ID': 'subordinate_root',
            'REL_OP': '>',
            'RIGHT_ID': 'object',
            'RIGHT_ATTRS': {'LEMMA': {'NOT_IN': ['que', 'quien']}, 'DEP': 'obj'}
        }
    ]
    matcher.add('relativa_con_antecedente_sujeto', [pattern])

    return matcher

def get_relativa_reconstruida(texto, nlp, matcher):
    doc = nlp(texto)
    matches = matcher(doc)
    match_id, token_ids = matches[0]
    """ string_id = nlp.vocab.strings[match_id]
    print(f'Matcheó con {string_id}') """
    
    print(f'TEXTO: {texto}')
    if nlp.vocab.strings[match_id] == 'relativa_con_antecedente_objeto':
        print(f'RELATIVA RECONSTRUIDA: {doc[token_ids[2]].text} {doc[token_ids[1]].lemma_} {doc[token_ids[0]].text}')
        print(f'Donde "{doc[token_ids[2]].text}" es el sujeto, "{doc[token_ids[1]].lemma_}" es el núcleo y "{doc[token_ids[0]].text}" es el objeto')
    elif nlp.vocab.strings[match_id] == 'relativa_con_antecedente_sujeto':
        print(f'RELATIVA RECONSTRUIDA: {doc[token_ids[0]].text} {doc[token_ids[1]].lemma_} {doc[token_ids[2]].text}')
        print(f'Donde "{doc[token_ids[0]].text}" es el sujeto, "{doc[token_ids[1]].lemma_}" es el núcleo y "{doc[token_ids[2]].text}" es el objeto')
    else:
        print('No hubo coincidencias.')
    print()
    return None

def main():
    nlp = spacy.load("es_dep_news_trf")
    matcher = setup_matcher(nlp)

    # En este ejemplo la relativa se encuentra en el sujeto de la oración principal y el pronombre relativo (que) refiere al objeto de la subordinada
    texto = "La comida que preparó mi madre ya está servida."
    get_relativa_reconstruida(texto, nlp, matcher)

    # Ídem anterior pero el orden de sujeto y verbo en la subordinada está invertido
    texto = "La comida que mi madre preparó ya está servida."
    get_relativa_reconstruida(texto, nlp, matcher)

    # Ídem anterior pero con más elementos entre el sujeto y el verbo de la subordinada
    texto = "La comida que mi madre con tanto amor preparó ya está servida."
    get_relativa_reconstruida(texto, nlp, matcher)

    # En este ejemplo la relativa se encuentra en el objeto de la oración principal y el pronombre relativo (que) refiere al objeto de la subordinada
    texto = "Estoy muy contenta. Hoy voy a comer la comida que preparó mi madre."
    get_relativa_reconstruida(texto, nlp, matcher)

    # En este ejemplo la relativa se encuentra en el objeto de la oración principal y el pronombre relativo (que) refiere al sujeto de la subordinada
    texto = "Me presentó al periodista que había escrito el reportaje."
    get_relativa_reconstruida(texto, nlp, matcher)

main()