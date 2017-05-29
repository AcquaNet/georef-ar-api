# -*- coding: utf-8 -*-
import os
import re
from elasticsearch import Elasticsearch


def query(address, params=None):
    es = Elasticsearch()
    query = {'query': {'bool': {'must': []}}}
    terms = query['query']['bool']['must']
    if params and (len(params)) > 1:
        terms.append(
            {'match_phrase_prefix': {'nombre': params.get('direccion')}})
        locality = params.get('localidad')
        state = params.get('provincia')
        if locality:
            terms.append({'match': {'localidad': locality}})
        if state:
            terms.append({'match': {'provincia': state}})
    else:
        terms.append({'match_phrase_prefix': {'nomenclatura': address}})

    results = es.search(index='sanluis', doc_type='calle', body=query)
    return [address['_source'] for address in results['hits']['hits']]


def build_dict_from(address, row):
    road = ' '.join(row[:2])
    place = ', '.join(row[4:])
    _, number = get_parts_from(address.split(',')[0])
    obs = 'Se procesó correctamente la dirección buscada.'
    if number and row[2] and row[3]:    # validates door number.
        if row[2] <= number and number <= row[3]:
            road += ' %s' % str(number)
        else:
            obs = 'La altura buscada está fuera del rango conocido.'
    elif number and not (row[2] or row[3]):
        obs = 'La calle no tiene numeración en la base de datos.'
    full_address = ', '.join([road, place])
    return {
        'nomenclatura': full_address,
        'tipo': row[0],
        'nombre': row[1],
        'altura_inicial': row[2],
        'altura_final': row[3],
        'localidad': row[4],
        'provincia': row[5],
        'observaciones': obs
    }


def get_parts_from(address):
    match = re.search(r'(\s[0-9]+?)$', address)
    number = int(match.group(1)) if match else None
    address = re.sub(r'(\s[0-9]+?)$', r'', address)
    return address.strip(), number
