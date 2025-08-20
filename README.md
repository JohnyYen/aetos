
# 🦅 Aetos – Wrapper de `pip` con índice de paquetes personalizado

> **Aetos** (del griego "águila") es un wrapper ligero y poderoso de `pip` que ejecuta todos los comandos con un **servidor de paquetes (index) predefinido** sin consumo de datos, ideal para entornos con acceso restringido a PyPI, redes corporativas, CI/CD o usuarios que necesitan usar mirrors locales.

🚀 Usa `aetos` como si fuera `pip`, pero **sin tener que recordar `--index-url`** cada vez.

---

## 🌟 ¿Por qué Aetos?

En muchos entornos (como empresas, universidades o regiones con censura), el acceso a `https://pypi.org` es lento o bloqueado. Usar mirrors como **Tsinghua**, **Aliyun**, **Nexus** o **Artifactory** es común, pero obliga a escribir:

```bash
pip install requests --index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

¡Una y otra vez!

**Aetos soluciona esto**: configura el índice una vez en el código y olvídate de él.

---

## 🔧 Características

- ✅ Ejecuta cualquier comando de `pip`: `install`, `uninstall`, `list`, `show`, etc.
- ✅ Usa un **índice de paquetes personalizado definido en el código**
- ✅ No requiere configuraciones manuales ni `.pypirc`
- ✅ 100% compatible con `pip`
- ✅ Fácil de instalar, personalizar y distribuir
- ✅ Ideal para:
  - Equipos de desarrollo
  - CI/CD
  - Entornos offline o con proxy
  - Usuarios en China, Latinoamérica, redes corporativas, etc.

---

## 🚀 Instalación

### Opción 1: Desde PyPI (recomendado)

```bash
pip install aetos
```


### Opción 2: Desde el repositorio (desarrollo)

```bash
git clone https://github.com/JohnyYen/aetos
cd aetos
pip install -e .
```

---

## 🛠️ Uso

Una vez instalado, usa `aetos` como si fuera `pip`:

```bash
aetos install requests
aetos install django flask
aetos uninstall paquete
aetos list
aetos show numpy
```

Todos los comandos se ejecutarán automáticamente con el índice configurado.

---

## 🔐 Índice de paquetes predeterminado

Actualmente, `aetos` está configurado para usar:

```
http://nexus.uclv.edu.cu/repository/npm/
```

> Este es un mirror rápido y confiable de PyPI mantenido por la Universidad de las Villas (Cuba).

---

## 🧩 ¿Quieres cambiar el índice?

Edita el archivo `aetos.py` y modifica la línea:

```python
INDEX_URL = "http://nexus.uclv.edu.cu/repository/npm/"
```


Luego reinstala el paquete:

```bash
pip install -e .
```

---

## 🧪 Comandos soportados

Todos los comandos de `pip` son compatibles:

| Comando | Ejemplo |
|--------|--------|
| `install` | `aetos install requests` |
| `uninstall` | `aetos uninstall requests` |
| `list` | `aetos list` |
| `show` | `aetos show django` |
| `freeze` | `aetos freeze` |
| `download` | `aetos download pillow` |

---

## 🛠️ Desarrollo

Clona el repositorio y configura el entorno:

```bash
git clone https://github.com/JohnyYen/aetos
cd aetos
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

pip install -e .
```

Ahora puedes probar:

```bash
aetos install rich
```

---

## 📦 Publicación (para mantenedores)

```bash
python -m build
twine upload dist/*
```
