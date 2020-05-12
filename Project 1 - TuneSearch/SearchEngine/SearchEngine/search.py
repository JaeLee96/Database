#!/usr/bin/python3

import psycopg2
import re
import string
import sys

_PUNCTUATION = frozenset(string.punctuation)

def _remove_punc(token):
    """Removes punctuation from start/end of token."""
    i = 0
    j = len(token) - 1
    idone = False
    jdone = False
    while i <= j and not (idone and jdone):
        if token[i] in _PUNCTUATION and not idone:
            i += 1
        else:
            idone = True
        if token[j] in _PUNCTUATION and not jdone:
            j -= 1
        else:
            jdone = True
    return "" if i > j else token[i:(j+1)]

def _get_tokens(query):
    rewritten_query = []
    tokens = re.split('[ \n\r]+', query)
    for token in tokens:
        cleaned_token = _remove_punc(token)
        if cleaned_token:
            if "'" in cleaned_token:
                cleaned_token = cleaned_token.replace("'", "''")
            rewritten_query.append(cleaned_token)
    return rewritten_query



def search(query, query_type, offset):
    
    rewritten_query = _get_tokens(query)
    con = None
    rows = []
    result_len = 0
    
    try:
        con = psycopg2.connect('dbname=searchengine host=localhost user=cs143 password=cs143')
        cur = con.cursor()  
        
        if offset == 1:
            cur.execute("DROP MATERIALIZED VIEW IF EXISTS results;")
        
        offset = offset - 1
        
        terms = list(set([query.strip().lower() for query in query.split()]))
        nterms = len(terms)

        ## pagination
        combination = '(' + ','.join('%s' for _ in terms) + ')'
        sql_query = f"""CREATE MATERIALIZED VIEW IF NOT EXISTS results AS 
                            SELECT song_name, artist_name, tfidf FROM ranking r 
                            WHERE token IN {combination}
                            ORDER BY tfidf DESC;""" 

        ## create materialized view
        cur.execute(sql_query, terms)
        
        if query_type.upper() == 'OR':
            cur.execute("""SELECT song_name, artist_name FROM (
                                SELECT song_name, artist_name, SUM(tfidf) AS tfidf_sum FROM results
                                GROUP BY song_name, artist_name 
                            ) R ORDER BY tfidf_sum DESC
                            LIMIT 20 OFFSET %s;""", [offset])
            
            for result in cur.fetchall():
                rows.append(result)

            cur.execute("""SELECT Count(*) FROM ( 
                                SELECT song_name, artist_name FROM results
                             ) R;""")
        else:
            new_query = """SELECT song_name, artist_name FROM (
                                SELECT song_name, artist_name, SUM(tfidf) AS tfidf_sum FROM results
                                 GROUP BY song_name, artist_name
                                 HAVING Count(*) = %s
                               ) R ORDER BY tfidf_sum DESC
                                 LIMIT 20 OFFSET %s;"""

            cur.execute(new_query, [nterms, offset])

            for result in cur.fetchall():
                rows.append(result);

            cur.execute("""SELECT Count(*) FROM ( SELECT song_name, artist_name FROM results 
                             GROUP BY song_name, artist_name
                             HAVING Count(*) = %s ) R;""", [nterms])

        ## save and return the number of total rows
        result_len = int(cur.fetchone()[0])
        cur.close()
        
    except(Except, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.commit()
            con.close()
    
    return (rows, result_len)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

