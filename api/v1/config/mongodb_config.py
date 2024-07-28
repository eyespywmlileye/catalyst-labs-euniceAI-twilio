from dataclasses import dataclass

@dataclass
class MongoDBConfig: 
    database_name: str = "catalyst-lab"
    vector_search_index_name: str = "catalyst-vector-index"

