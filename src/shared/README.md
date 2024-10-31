# Shared library for all server config component

### Description
- utilities to help execute basic operation/command
- entity class to unify basic function for entity data format

### Entity Class Common Attribute
- State: Make/Break, 
- - Make: meaning the entity should be created and maintain existed.
- - Break: meaning the entity should be deleted or destroyed

- Status: Active/Error,
- - Active: meaning the entity still exists logically
- - Deleted: meaning the entity is already deleted. no need to work on it
- - Error: meaning the entity is having error during creation or maintanence.