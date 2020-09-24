from flask import current_app

def add_to_index(index, object):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in object.__searchable__:
        payload[field] = getattr(object, field)
    current_app.elasticsearch.index(index=index, id=object.id, body=payload)

def remove_from_index(index, object):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index, id=object.id)

def query_index(index, query, page,  per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(index=index, body={'track_total_hits': True, 'query':{'multi_match': {'query': query,
                                                                                        'fields': ['*']}},
                                                               'from': page-1, 'size':per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']
    # return ids, search