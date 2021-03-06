import logging
import time
import psycopg2
import csv
import os
from common.config import DEFAULT_TABLE, PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE, PG_TABLE
from common.const import default_cache_dir
from encoder.encode import feature_extract
from diskcache import Cache
from indexer.index import milvus_client, create_table, insert_vectors, delete_table, search_vectors, create_index,has_table

def connect_postgres():
    try:
        conn = psycopg2.connect(host=PG_HOST,port=PG_PORT,user=PG_USER,password=PG_PASSWORD,database=PG_DATABASE)
        print('connect postgres successfully')
    except:
        print('connect postgres failed')    
    return conn

def create_pg_table():
    conn = connect_postgres
    cur = conn.cursor()
    sql = "create {} (ids bigint,name text)".format(PG_TABLE)
    cur.excute(sql)
    print('create table successfully')
    conn.close()
    

def copy_data_to_postgres():
    conn = connect_postgres()
    cur = conn.cursor()
    current_path = os.path.abspath(__file__)
    father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
    ffather_path = os.path.abspath(os.path.dirname(father_path) + os.path.sep + ".")
    path = ffather_path + '/tmp/id_name.csv'
    sql = "copy {} from {}".format(PG_TABLE,path)
    cur.excute(sql)
    print('import data successfully')
    conn.close()

def create_pg_index():
    conn = connect_postgres()
    cur = conn.cursor()
    sql = "create index ids_index on {} (ids)".format(PG_TABLE)
    cur.excute(sql)
    print('create index successfully')
    conn.close()

def delete_pg_table():
    conn = connect_postgres()
    cur = conn.cursor()
    sql = "drop table {}".format(PG_TABLE)
    cur.excute(sql)
    print('drop table successfully')
    conn.close()

def do_load(table_name, database_path):
    if not table_name:
        table_name = DEFAULT_TABLE
    cache = Cache(default_cache_dir)
    try:
        vectors, names = feature_extract(table_name, database_path)
        print("start connetc to milvus")
        index_client = milvus_client()
        status, ok = has_table(index_client, table_name)
        if not ok:
            print("create table.")
            create_table(index_client, table_name=table_name)
        print("insert into:", table_name)

        # status, ids = insert_vectors(index_client, table_name, vectors)
        total_ids = []
        ids_lens = 0
        while ids_lens<len(vectors) :
            try:
                status, ids = insert_vectors(index_client, table_name, vectors[ids_lens:ids_lens+100000])
            except:
                status, ids = insert_vectors(index_client, table_name, vectors[ids_lens:len(vectors)])
            ids_lens += 100000
            total_ids += ids
            print("ids:",len(ids))

        create_index(index_client, table_name)

        with open('id_name.csv','a') as f:
            writer = csv.writer(f)
            writer.writerows(zip(total_ids,names))

        create_pg_table()
        copy_data_to_postgres()
        create_pg_index()

        # for i in range(len(names)):
        #     cache[total_ids[i]] = names[i]
        print("FP finished")
        return "FP finished"
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e)


