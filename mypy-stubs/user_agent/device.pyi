from typing import Any, Dict, List

DataStore = List[Dict[str, Any]]

def load_package_json_data(location: str) -> DataStore: ...

SMARTPHONE_DEV_IDS: DataStore
TABLET_DEV_IDS: DataStore
