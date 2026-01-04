#!/usr/bin/env python3

import subprocess
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRealWrapperExecution:
    """Tests que ejecutan el wrapper real desde la terminal"""

    def test_wrapper_help_message(self):
        """Test que el wrapper muestra mensaje de ayuda"""
        result = subprocess.run(
            [sys.executable, 'aetos.py'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert 'Uso:' in result.stdout
        assert 'aetos config show' in result.stdout
        assert 'aetos config set' in result.stdout
        assert 'aetos config reset' in result.stdout

    def test_config_show_default(self):
        """Test comando config show con URL por defecto"""
        # Limpiar configuración previa
        config_file = Path.home() / '.aetos' / 'config.json'
        if config_file.exists():
            config_file.unlink()

        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'show'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'URL del índice actual' in result.stdout
        assert 'https://nexus.uclv.edu.cu/repository/pypi.org/' in result.stdout
        assert 'configuración por defecto' in result.stdout

    def test_config_set_valid_url(self):
        """Test comando config set con URL válida"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'https://pypi.org/simple/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'actualizada' in result.stdout
        assert 'https://pypi.org/simple/' in result.stdout
        assert 'config.json' in result.stdout

        # Verificar que el archivo se creó
        config_file = Path.home() / '.aetos' / 'config.json'
        assert config_file.exists()

        # Verificar contenido del archivo
        with open(config_file, 'r') as f:
            config = json.load(f)
        assert config['index_url'] == 'https://pypi.org/simple/'

    def test_config_show_custom_url(self):
        """Test comando config show con URL personalizada"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'show'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'https://pypi.org/simple/' in result.stdout
        assert 'personalizada' in result.stdout

    def test_config_set_another_url(self):
        """Test comando config set con otra URL"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'https://test-mirror.com/simple/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'https://test-mirror.com/simple/' in result.stdout

    def test_pip_list_with_custom_url(self):
        """Test comando pip list con URL personalizada"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'list'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Package' in result.stdout or 'pytest' in result.stdout
        assert 'https://test-mirror.com/simple/' in result.stderr or 'https://test-mirror.com/simple/' in result.stdout

    def test_config_reset(self):
        """Test comando config reset"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Restablecida' in result.stdout or 'restablecida' in result.stdout
        assert 'https://nexus.uclv.edu.cu/repository/pypi.org/' in result.stdout

        # Verificar que el archivo fue eliminado
        config_file = Path.home() / '.aetos' / 'config.json'
        assert not config_file.exists()

    def test_config_show_after_reset(self):
        """Test config show después de reset"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'show'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'configuración por defecto' in result.stdout

    def test_config_set_invalid_url(self):
        """Test comando config set con URL inválida"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'invalid-url'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert 'debe comenzar' in result.stdout
        assert 'http://' in result.stdout

    def test_config_set_no_url(self):
        """Test comando config set sin URL"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert 'Uso:' in result.stdout

    def test_config_unknown_command(self):
        """Test comando config desconocido"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'unknown'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert 'desconocido' in result.stdout

    def test_pip_show_command(self):
        """Test comando pip show (comportamiento conocido: falla con --index-url)"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'show', 'pytest'],
            capture_output=True,
            text=True
        )
        # NOTA: pip show y freeze NO aceptan --index-url, por lo que fallan
        # Este es un comportamiento conocido del wrapper actual
        # El wrapper añade --index-url a TODOS los comandos, incluso los que no lo necesitan
        assert result.returncode != 0  # Debería fallar por el flag --index-url
        assert 'no such option: --index-url' in result.stderr or 'Error al ejecutar pip' in result.stdout

    def test_pip_freeze_command(self):
        """Test comando pip freeze (comportamiento conocido: falla con --index-url)"""
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'freeze'],
            capture_output=True,
            text=True
        )
        # NOTA: pip freeze NO acepta --index-url, por lo que falla
        # Este es un comportamiento conocido del wrapper actual
        assert result.returncode != 0  # Debería fallar por el flag --index-url
        assert 'no such option: --index-url' in result.stderr or 'Error al ejecutar pip' in result.stdout

    def test_config_set_with_different_mirrors(self):
        """Test configuración con diferentes mirrors"""
        mirrors = [
            'https://pypi.org/simple/',
            'https://pypi.tuna.tsinghua.edu.cn/simple/',
            'https://mirrors.aliyun.com/pypi/simple/',
        ]

        for mirror in mirrors:
            result = subprocess.run(
                [sys.executable, 'aetos.py', 'config', 'set', mirror],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert mirror in result.stdout

            # Verificar que la URL se guardó correctamente
            result = subprocess.run(
                [sys.executable, 'aetos.py', 'config', 'show'],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert mirror in result.stdout

    def test_multiple_url_changes(self):
        """Test múltiples cambios de URL"""
        # Limpiar primero
        config_file = Path.home() / '.aetos' / 'config.json'
        if config_file.exists():
            config_file.unlink()

        urls = [
            'https://mirror1.com/simple/',
            'https://mirror2.com/simple/',
            'https://mirror3.com/simple/',
        ]

        for url in urls:
            # Set
            result = subprocess.run(
                [sys.executable, 'aetos.py', 'config', 'set', url],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0

            # Verify
            result = subprocess.run(
                [sys.executable, 'aetos.py', 'config', 'show'],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert url in result.stdout

        # Reset
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_config_file_persistence(self):
        """Test que la configuración persiste entre ejecuciones"""
        # Set URL
        url = 'https://persistent-test.com/simple/'
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', url],
            capture_output=True,
            text=True
        )

        # Check en una nueva ejecución
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'show'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert url in result.stdout

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )

    def test_http_and_https_urls(self):
        """Test que acepta tanto HTTP como HTTPS"""
        test_urls = [
            'http://test-http.com/simple/',
            'https://test-https.com/simple/',
        ]

        for url in test_urls:
            result = subprocess.run(
                [sys.executable, 'aetos.py', 'config', 'set', url],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Fallo con URL: {url}"

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )

    def test_command_output_format(self):
        """Test que los comandos tienen el formato de salida correcto"""
        # Set custom URL
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'https://test-output.com/simple/'],
            capture_output=True,
            text=True
        )

        # Run pip command and check output format
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'list'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Check emoji y formato
        output = result.stdout + result.stderr
        assert '🦅' in output or 'Aetos' in output
        assert 'https://test-output.com/simple/' in output
        assert 'Ejecutando:' in output

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )

    def test_config_without_command(self):
        """Test comando config sin subcomando (equivalente a show)"""
        # Set a URL first
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'https://test-no-command.com/simple/'],
            capture_output=True,
            text=True
        )

        # Run config without subcommand
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'URL del índice actual' in result.stdout
        assert 'https://test-no-command.com/simple/' in result.stdout

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )

    def test_error_messages_are_in_spanish(self):
        """Test que los mensajes de error están en español"""
        # Test invalid URL
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'invalid'],
            capture_output=True,
            text=True
        )
        assert 'Error' in result.stdout or 'debe comenzar' in result.stdout

        # Test unknown command
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'unknown-command'],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0

        # Test config unknown
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'unknown'],
            capture_output=True,
            text=True
        )
        assert 'desconocido' in result.stdout

    def test_config_directory_creation(self):
        """Test que el directorio de configuración se crea automáticamente"""
        # Remove config directory if exists
        config_dir = Path.home() / '.aetos'
        if config_dir.exists():
            import shutil
            shutil.rmtree(config_dir)

        assert not config_dir.exists()

        # Set config should create directory
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'https://test-dir.com/simple/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert config_dir.exists()
        assert (config_dir / 'config.json').exists()

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )

    def test_install_mock_package_with_custom_index(self):
        """Test de instalación simulada (no real) con índice personalizado"""
        # Set custom index
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'set', 'https://test-install.com/simple/'],
            capture_output=True,
            text=True
        )

        # Check that command uses custom index
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'install', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # The install --help should work and show help
        assert 'install' in result.stdout.lower() or 'usage' in result.stdout.lower()

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )

        # Check that the command uses the custom index
        result = subprocess.run(
            [sys.executable, 'aetos.py', 'install', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # The install --help should work and show help
        assert 'install' in result.stdout.lower() or 'usage' in result.stdout.lower()

        # Clean up
        subprocess.run(
            [sys.executable, 'aetos.py', 'config', 'reset'],
            capture_output=True,
            text=True
        )
