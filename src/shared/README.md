# Shared library for all server config component

### Description
- utilities to help execute basic operation/command
- entity class to unify basic function for entity data format

### Entity Class Common Attribute
- A entity Data contain 2 sections.
- - id and type @ root level to identify data type and record id
- - A typical entity data example as following:
```jsonc
{
    "id": "id of the entity",
    "type": "data type of the entity",
    "current": {}
}
```

- A entity change request would be similar to the entity data.
```jsonc
{
    "id": "id of the entity",
    "type": "data type of the entity",
    "desired": {}        // desired data to change current entity into
}
```