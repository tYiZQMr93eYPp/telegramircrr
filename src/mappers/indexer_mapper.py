import yaml
from indexers.base import indexer_class


class IndexerMapper:
    def __init__(self, config_path):
        self._map: dict[int, type] = {}
        self._topic_map: dict[tuple[int, int], type] = {}
        self._chat_map: dict[int, type] = {}
        with open(config_path) as f:
            config = yaml.safe_load(f)
        for channel_id, class_name in (config.get("channel_indexers") or {}).items():
            self._map[int(channel_id)] = indexer_class(class_name)
        for composite_key, class_name in (config.get("group_topic_indexers") or {}).items():
            group_id, topic_id = str(composite_key).split("_")
            self._topic_map[(int(group_id), int(topic_id))] = indexer_class(class_name)
        for chat_id, class_name in (config.get("chat_indexers") or {}).items():
            self._chat_map[int(chat_id)] = indexer_class(class_name)

    def get(self, channel_id: int):
        return self._map.get(channel_id)

    def get_topic(self, group_id: int, topic_id: int):
        return self._topic_map.get((group_id, topic_id))

    def get_chat(self, chat_id: int):
        return self._chat_map.get(chat_id)

    def indexers(self):
        return set(self._map.values()) | set(self._topic_map.values()) | set(self._chat_map.values())
