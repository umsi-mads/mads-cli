def deep_merge(dict1, dict2):
    """Merge two dictionaries recursively."""

    result = dict1.copy()
    for k, v in dict2.items():
        if isinstance(v, dict):
            node = result.get(k, {})
            result[k] = deep_merge(node, v)
        else:
            result[k] = v

    return result
