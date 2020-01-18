import os

MILVUS_HOST = os.getenv("MILVUS_HOST", "127.0.0.1")
MILVUS_PORT = os.getenv("MILVUS_PORT", 19530)
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", 5432)
PG_USER = os.getenv("PG_USER", "zilliz")
PG_PASSWORD = os.getenv("PG_PASSWORD", "zilliz")
PG_DATABASE = os.getenv("PG_DATABASE", "postgres_mols")
PG_TABLE = os.getenv("PG_TABLE", "id_with_name")
VECTOR_DIMENSION = os.getenv("VECTOR_DIMENSION", 512)
DEFAULT_TABLE = os.getenv("DEFAULT_TABLE", "defult_mol_search_table")
