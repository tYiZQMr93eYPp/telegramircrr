def matrix_alias_for_indexer(indexer, domain: str) -> str:
    return f"#telegramircrr-{indexer.__name__.lower()}:{domain}"
