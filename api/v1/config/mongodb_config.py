class MongoDBDatabase:
    """ 
    MongoDB Database Configuration
    """
    def __init__(self, database_name: str = "catalyst_lab") -> None:
        self.database_name = database_name

class MongoDBCollections(MongoDBDatabase):
    """ 
    MongoDB Collections for the Catalyst Lab Database
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.usage_metrics_collection: str = "usage_metrics"
        self.dashboard_collection: str = "dashboard"
        self.state_manager_collection: str = "state_manager"

class MongoDBAtlas(MongoDBCollections):
    """ 
    MongoDB Atlas Configuration
    """
    def __init__(self) -> None:
        super().__init__()