# 🧪 Tests de Aetos

Este directorio contiene el conjunto completo de pruebas para el wrapper Aetos.

## 📊 Resumen de Pruebas

### Estadísticas
- **Total de pruebas:** 54
- **Cobertura de código:** 97%
- **Tiempo de ejecución:** ~5 segundos

### Tipos de Pruebas

#### 1. **Unit Tests** (`test_aetos.py` - 32 pruebas)
Pruebas unitarias con mocks que validan la lógica interna del wrapper.

**Categorías:**
- **TestConfigManagement (6 pruebas):** Gestión de archivos de configuración
  - Carga de configuración por defecto
  - Carga desde archivo JSON
  - Guardado de configuración
  - Obtención de URL del índice
  - Manejo de JSON inválido

- **TestConfigCommands (6 pruebas):** Comandos de configuración
  - `config show` (default y personalizado)
  - `config set` (URL válida, inválida, sin URL)
  - `config reset`
  - Comandos desconocidos

- **TestArgumentParsing (3 pruebas):** Parsing de argumentos
  - Sin argumentos (muestra error)
  - Comando simple
  - Múltiples paquetes

- **TestCommandConstruction (2 pruebas):** Construcción de comandos pip
  - Incluye `--index-url`
  - Incluye `--trusted-host`

- **TestSubprocessExecution (4 pruebas):** Ejecución de subprocess
  - Ejecución exitosa
  - Error `CalledProcessError`
  - Error `FileNotFoundError`
  - Propagación de returncode

- **TestIntegrationTests (4 pruebas):** Integración con pip
  - `install` (paquete simple y múltiples)
  - `uninstall`
  - `list`

- **TestCustomURLUsage (2 pruebas):** Uso de URL personalizada
  - Comandos usan URL personalizada
  - Comandos usan URL por defecto sin config

- **TestOutputMessages (5 pruebas):** Mensajes de salida
  - URL del índice
  - Mensaje de ejecución
  - Error sin argumentos
  - Ayuda con comandos disponibles

#### 2. **Integration Tests** (`test_aetos_integration.py` - 22 pruebas)
Pruebas que ejecutan el wrapper real desde la terminal usando subprocess.

**Categorías:**
- **Configuración básica (9 pruebas):**
  - Mensaje de ayuda
  - `config show` (default y personalizado)
  - `config set` (validaciones, múltiples URLs)
  - `config reset`
  - Errores (URL inválida, sin URL, comando desconocido)

- **Comandos pip (3 pruebas):**
  - `pip list` con URL personalizada
  - `pip show` (documenta limitación actual)
  - `pip freeze` (documenta limitación actual)

- **Comportamiento de configuración (8 pruebas):**
  - Múltiples mirrors
  - Múltiples cambios de URL
  - Persistencia entre ejecuciones
  - Soporte HTTP y HTTPS
  - Formato de salida
  - Comando `config` sin subcomando
  - Mensajes en español
  - Creación automática de directorio

- **Simulación de instalación (1 prueba):**
  - `install --help` con índice personalizado

## 🚀 Ejecución de Pruebas

### Ejecutar todas las pruebas:
```bash
source venv_test/bin/activate
python -m pytest tests/ -v
```

### Ejecutar solo pruebas unitarias:
```bash
source venv_test/bin/activate
python -m pytest tests/test_aetos.py -v
```

### Ejecutar solo pruebas de integración:
```bash
source venv_test/bin/activate
python -m pytest tests/test_aetos_integration.py -v
```

### Ejecutar con reporte de cobertura:
```bash
source venv_test/bin/activate
python -m pytest tests/ --cov=aetos.aetos --cov-report=term-missing
```

### Ejecutar con reporte HTML de cobertura:
```bash
source venv_test/bin/activate
python -m pytest tests/ --cov=aetos.aetos --cov-report=html
# Abrir htmlcov/index.html en el navegador
```

### Ejecutar una prueba específica:
```bash
source venv_test/bin/activate
python -m pytest tests/test_aetos.py::TestConfigManagement::test_load_config_default -v
```

## 📝 Limitaciones Conocidas Documentadas

El wrapper actual tiene dos limitaciones que están documentadas en las pruebas:

1. **`pip show` y `pip freeze` fallan:**
   - Estos comandos NO aceptan el flag `--index-url`
   - El wrapper añade este flag a TODOS los comandos
   - Las pruebas de integración documentan este comportamiento esperado

2. **Cobertura 97% (no 100%):**
   - Las líneas 107-108 no se cubren completamente por cómo pytest mide cobertura en subprocess
   - El bloque `if __name__ == "__main__":` (línea 139) solo se ejecuta en invocación directa

## 🛠️ Estructura de Archivos

```
tests/
├── __init__.py                          # Paquete vacío
├── test_aetos.py                        # Pruebas unitarias (32 tests)
│   ├── TestConfigManagement             # Gestión de configuración
│   ├── TestConfigCommands               # Comandos de configuración
│   ├── TestArgumentParsing              # Parsing de argumentos
│   ├── TestCommandConstruction          # Construcción de comandos
│   ├── TestSubprocessExecution          # Ejecución de subprocess
│   ├── TestIntegrationTests             # Integración con pip
│   ├── TestCustomURLUsage               # Uso de URL personalizada
│   └── TestOutputMessages              # Mensajes de salida
└── test_aetos_integration.py           # Pruebas de integración (22 tests)
    └── TestRealWrapperExecution        # Ejecución real del wrapper
```

## 🎯 Escenarios Probados

Las pruebas cubren todos los siguientes escenarios:

✅ Cambio de URL del índice
✅ Persistencia de configuración
✅ Validación de URLs (http/https)
✅ Manejo de errores (URL inválida, comandos desconocidos)
✅ Comandos de pip con índice personalizado
✅ Reset a configuración por defecto
✅ Creación automática de directorios
✅ Mensajes en español
✅ Formato de salida correcto
✅ Múltiples mirrors soportados
✅ Cambios múltiples de URL

## 📈 Resultados Recientes

```
============================= test session starts ==============================
platform linux -- Python 3.14.2
plugins: cov-7.0.0
collected 54 items

tests/test_aetos.py ................................             [ 59%]
tests/test_aetos_integration.py ......................       [100%]

============== 54 passed in 5.01s ==============

Coverage: 97%
```

## 🔧 Herramientas Utilizadas

- **pytest:** Framework de pruebas
- **unittest.mock:** Mocking de subprocess y sys
- **pytest-cov:** Medición de cobertura de código
- **subprocess:** Ejecución real del wrapper en pruebas de integración

## 📚 Convenciones de Nombres

- Clases de pruebas: `Test{Categoria}`
- Métodos de pruebas: `test_{accion}_{contexto}`
- Fixtures: `{recurso}` o `temp_{recurso}`
- Uso de español en nombres descriptivos para claridad
