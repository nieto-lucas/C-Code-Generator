# C-Code-Generator

Crea archivos C a partir de un archivo base expandiendolo de forma similar a un L-Sistema pero con una regla de produción fija:

- Las funciones terminales, es decir, aquellas que no llaman a otra función, por cada expansión replican el grafo de llamadas.

Por ej. consideremos el siguiente programa con su respectivo grafo de llamadas.

- Archivo base:

![alt text](/imgs/base.png)

- 1º expansión:

![alt text](/imgs/expansion_cg.png)

![alt text](/imgs/expansion_funcs.png)

## Configuración:

### 1) Crear un entorno virtual:

Desde este directorio ejecutar

```bash
python -m venv .env
source .env/bin/activate
```

### 2) Instalar dependencias desde `pyproject.toml`:

En el mismo directorio y en el entorno virtual ejecutar:

```bash
pip install -e .
```
> Las dependencias del proyecto pueden verificarse en [pyproject.toml](/pyproject.toml)

## Ejecución:

### 1) Crear un archivo .c base

> Consultar [getenv_to_strcpy.c](/seeds/getenv_to_strcpy.c) para referencia de como construir un archivo base con un patron de vulnerabilidad.

### 2) Correr el programa:

```bash
c-generator seed.c -r root -n 2
```

> Para consultar opciones de ejecución agregar el flag `-h` 

## Tests:

### 1) Instalar dependencias desde `pyproject.toml`:

En el mismo directorio y en el entorno virtual ejecutar:

```bash
pip install -e ".[dev]"
```

### 2) Correr tests:

```bash
pytest tests
```

## Limitaciones:

- El archivo base no debe tener ningún tipo de directiva de preprocesador: `#define`, `#include`, ...

- Si se quiere generar un archivo C bien formado, depende de que se escriba correctamente el archivo base, se incorporen los headers necesarios mediante el flag `-i` y todas la funciones que esten en el grafo de llamadas desde root deben retornar el mismo tipo. 

- Actualmente no soporta la generación de cualquier otra directiva que no sean `#include`s.

- Actualmente depende de indicar una función root de forma explicita.
