import logging
import psycopg2
from common.const import default_cache_dir
from indexer.index import milvus_client, create_table, insert_vectors, delete_table, search_vectors, create_index
from diskcache import Cache
from encoder.encode import smiles_to_vec
from common.config import DEFAULT_TABLE, PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE, PG_TABLE
from service.load import connect_postgres

def query_smi_from_ids(vids):
    res = []
    # cache = Cache(default_cache_dir)
    # print("cache:",cache)
    # for i in vids:
    #     if i in cache:
    #         res.append(cache[i])
    conn = connect_postgres()
    for i in vids:
        cur = conn.cursor()
        sql = "select name from {} where ids={}".format(PG_TABLE,i)
        name = cur.excute(sql)
        res.append(name)
    conn.close()

    return res


def do_search(table_name, molecular_name, top_k):
    try:
        feats = []
        index_client = milvus_client()
        feat = smiles_to_vec(molecular_name)
        feats.append(feat)
        _, vectors = search_vectors(index_client, table_name, feats, top_k)
        vids = [x.id for x in vectors[0]]
        # print(vids)

        res_smi = [x.decode('utf-8') for x in query_smi_from_ids(vids)]
        # print("vids:",vids)
        res_distance = [x.distance for x in vectors[0]]
        res_ids = [x.id for x in vectors[0]]
        # print(res_distance,res_smi)

        return res_smi,res_distance, res_ids
    except Exception as e:
        logging.error(e)
        return "Fail with error {}".format(e)