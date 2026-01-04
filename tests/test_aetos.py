#!/usr/bin/env python3

import pytest
import subprocess
from unittest.mock import patch, MagicMock, call
import sys
import json
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from aetos.aetos import (
    main,
    get_config_dir,
    load_config,
    save_config,
    get_index_url,
    handle_config_command,
    DEFAULT_INDEX_URL,
    CONFIG_FILE,
    CONFIG_DIR
)


@pytest.fixture
def temp_config_dir():
    """Fixture para crear un directorio temporal de configuración"""
    temp_dir = Path(tempfile.mkdtemp())
    original_config_file = CONFIG_FILE

    # Patch CONFIG_FILE y CONFIG_DIR
    import aetos.aetos
    aetos.aetos.CONFIG_FILE = temp_dir / "config.json"
    aetos.aetos.CONFIG_DIR = temp_dir

    yield temp_dir

    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    # Restore original
    aetos.aetos.CONFIG_FILE = original_config_file
    aetos.aetos.CONFIG_DIR = CONFIG_DIR


@pytest.fixture
def clean_config():
    """Fixture para limpiar configuración antes de cada test"""
    import aetos.aetos

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()

    yield

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


class TestConfigManagement:
    """Test de gestión de configuración"""

    def test_load_config_default(self, clean_config):
        """Test que carga config por defecto cuando no existe archivo"""
        config = load_config()
        assert config == {"index_url": DEFAULT_INDEX_URL}

    def test_load_config_from_file(self, temp_config_dir):
        """Test que carga config desde archivo existente"""
        test_config = {"index_url": "https://custom.mirror.com/simple/"}
        with open(temp_config_dir / "config.json", 'w') as f:
            json.dump(test_config, f)

        config = load_config()
        assert config == test_config

    def test_save_config(self, temp_config_dir):
        """Test que guarda configuración correctamente"""
        test_config = {"index_url": "https://test.mirror.com/simple/"}
        save_config(test_config)

        assert (temp_config_dir / "config.json").exists()
        with open(temp_config_dir / "config.json", 'r') as f:
            saved_config = json.load(f)
        assert saved_config == test_config

    def test_get_index_url_default(self, clean_config):
        """Test que retorna URL por defecto cuando no hay config"""
        url = get_index_url()
        assert url == DEFAULT_INDEX_URL

    def test_get_index_url_custom(self, temp_config_dir):
        """Test que retorna URL personalizada"""
        test_config = {"index_url": "https://custom.mirror.com/simple/"}
        with open(temp_config_dir / "config.json", 'w') as f:
            json.dump(test_config, f)

        url = get_index_url()
        assert url == "https://custom.mirror.com/simple/"

    def test_get_index_url_invalid_json(self, temp_config_dir):
        """Test que maneja JSON inválido"""
        with open(temp_config_dir / "config.json", 'w') as f:
            f.write("invalid json")

        url = get_index_url()
        assert url == DEFAULT_INDEX_URL


class TestConfigCommands:
    """Test de comandos de configuración"""

    @patch('builtins.print')
    def test_config_show_default(self, mock_print, clean_config):
        """Test comando config show con URL por defecto"""
        handle_config_command([])
        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any(DEFAULT_INDEX_URL in msg for msg in print_calls)
        assert any('configuración por defecto' in msg.lower() for msg in print_calls)

    @patch('builtins.print')
    def test_config_show_custom(self, mock_print, temp_config_dir):
        """Test comando config show con URL personalizada"""
        test_config = {"index_url": "https://custom.mirror.com/simple/"}
        with open(temp_config_dir / "config.json", 'w') as f:
            json.dump(test_config, f)

        handle_config_command([])
        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any('custom.mirror.com' in msg for msg in print_calls)

    @patch('builtins.print')
    def test_config_set_no_url(self, mock_print, clean_config):
        """Test comando config set sin URL"""
        with pytest.raises(SystemExit) as exc_info:
            handle_config_command(['set'])
        assert exc_info.value.code == 1
        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any('Uso:' in msg for msg in print_calls)

    @patch('builtins.print')
    def test_config_set_invalid_url(self, mock_print, temp_config_dir):
        """Test comando config set con URL inválida"""
        with pytest.raises(SystemExit) as exc_info:
            handle_config_command(['set', 'invalid-url'])
        assert exc_info.value.code == 1
        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any('debe comenzar' in msg.lower() for msg in print_calls)

    @patch('builtins.print')
    def test_config_set_valid_url(self, mock_print, temp_config_dir):
        """Test comando config set con URL válida"""
        new_url = "https://new.mirror.com/simple/"
        handle_config_command(['set', new_url])

        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any('actualizada' in msg.lower() for msg in print_calls)
        assert any(new_url in msg for msg in print_calls)

        # Verificar que se guardó
        with open(temp_config_dir / "config.json", 'r') as f:
            config = json.load(f)
        assert config["index_url"] == new_url

    @patch('builtins.print')
    @patch('sys.exit')
    def test_config_reset(self, mock_exit, mock_print, temp_config_dir):
        """Test comando config reset"""
        test_config = {"index_url": "https://custom.mirror.com/simple/"}
        with open(temp_config_dir / "config.json", 'w') as f:
            json.dump(test_config, f)

        handle_config_command(['reset'])

        # Verificar que se eliminó el archivo
        assert not (temp_config_dir / "config.json").exists()

        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any('restablecida' in msg.lower() for msg in print_calls)

    @patch('builtins.print')
    def test_config_unknown_command(self, mock_print):
        """Test comando config desconocido"""
        with pytest.raises(SystemExit) as exc_info:
            handle_config_command(['unknown'])
        assert exc_info.value.code == 1
        print_calls = [str(call_args) for call_args in mock_print.call_args_list]
        assert any('desconocido' in msg.lower() for msg in print_calls)


class TestArgumentParsing:
    """Test parsing de argumentos"""

    @patch('builtins.print')
    def test_no_arguments_shows_error(self, mock_print):
        """Test que no argumentos muestra error"""
        with patch.object(sys, 'argv', ['aetos']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            mock_print.assert_called()

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_parse_command(self, mock_run, mock_print, mock_exit):
        """Test que comando se parsea correctamente"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert 'install' in call_args
            assert 'requests' in call_args

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_parse_multiple_packages(self, mock_run, mock_print, mock_exit):
        """Test que múltiples paquetes se parsean correctamente"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'django', 'flask', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert 'django' in call_args
            assert 'flask' in call_args
            assert 'requests' in call_args


class TestCommandConstruction:
    """Test construcción de comandos pip"""

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_command_includes_index_url(self, mock_run, mock_print, mock_exit):
        """Test que comando incluye --index-url"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert '--index-url' in call_args
            index_url_index = call_args.index('--index-url')
            assert call_args[index_url_index + 1] == DEFAULT_INDEX_URL

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_command_includes_trusted_host(self, mock_run, mock_print, mock_exit):
        """Test que comando incluye --trusted-host"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert '--trusted-host' in call_args
            trusted_host_index = call_args.index('--trusted-host')
            host = DEFAULT_INDEX_URL.split('//')[-1].split('/')[0]
            assert call_args[trusted_host_index + 1] == host


class TestSubprocessExecution:
    """Test ejecución de subprocess y manejo de errores"""

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_successful_execution(self, mock_run, mock_print, mock_exit):
        """Test ejecución exitosa de comando pip"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            mock_run.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_failed_execution_called_process_error(self, mock_run, mock_print, mock_exit):
        """Test manejo de CalledProcessError"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.side_effect = subprocess.CalledProcessError(1, 'pip')
            main()
            mock_exit.assert_called_once_with(1)
            mock_print.assert_called()
            error_messages = [str(call_args) for call_args in mock_print.call_args_list]
            assert any('Error al ejecutar pip' in msg for msg in error_messages)

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_failed_execution_file_not_found_error(self, mock_run, mock_print, mock_exit):
        """Test manejo de FileNotFoundError"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.side_effect = FileNotFoundError()
            main()
            mock_exit.assert_called_once_with(1)
            mock_print.assert_called()
            error_messages = [str(call_args) for call_args in mock_print.call_args_list]
            assert any('No se encontró pip' in msg for msg in error_messages)

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_returncode_propagation(self, mock_run, mock_print, mock_exit):
        """Test propagación de returncode"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=5)
            main()
            mock_exit.assert_called_once_with(5)


class TestIntegrationTests:
    """Test de integración para varios comandos pip"""

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_install_single_package(self, mock_run, mock_print, mock_exit):
        """Test comando install con paquete único"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert 'install' in call_args
            assert 'requests' in call_args

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_install_multiple_packages(self, mock_run, mock_print, mock_exit):
        """Test comando install con múltiples paquetes"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'django', 'flask', 'numpy']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert 'install' in call_args
            assert 'django' in call_args
            assert 'flask' in call_args
            assert 'numpy' in call_args

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_uninstall_command(self, mock_run, mock_print, mock_exit):
        """Test comando uninstall"""
        with patch.object(sys, 'argv', ['aetos', 'uninstall', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert 'uninstall' in call_args
            assert 'requests' in call_args

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_list_command(self, mock_run, mock_print, mock_exit):
        """Test comando list"""
        with patch.object(sys, 'argv', ['aetos', 'list']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert 'list' in call_args


class TestCustomURLUsage:
    """Test uso de URL personalizada en comandos"""

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_command_uses_custom_url(self, mock_run, mock_print, mock_exit, temp_config_dir):
        """Test que comandos usan URL personalizada configurada"""
        custom_url = "https://custom.mirror.com/simple/"
        test_config = {"index_url": custom_url}
        with open(temp_config_dir / "config.json", 'w') as f:
            json.dump(test_config, f)

        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert '--index-url' in call_args
            index_url_index = call_args.index('--index-url')
            assert call_args[index_url_index + 1] == custom_url

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_command_uses_default_url_when_no_config(self, mock_run, mock_print, mock_exit):
        """Test que comandos usan URL por defecto cuando no hay config"""
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()

        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            call_args = mock_run.call_args[0][0]
            assert '--index-url' in call_args
            index_url_index = call_args.index('--index-url')
            assert call_args[index_url_index + 1] == DEFAULT_INDEX_URL


class TestOutputMessages:
    """Test mensajes de salida"""

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_index_url_message(self, mock_run, mock_print, mock_exit):
        """Test que mensaje de URL del índice se muestra"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            print_calls = [str(call_args) for call_args in mock_print.call_args_list]
            assert any(DEFAULT_INDEX_URL in msg for msg in print_calls)

    @patch('sys.exit')
    @patch('builtins.print')
    @patch('subprocess.run')
    def test_execution_message(self, mock_run, mock_print, mock_exit):
        """Test que mensaje de ejecución se muestra"""
        with patch.object(sys, 'argv', ['aetos', 'install', 'requests']):
            mock_run.return_value = MagicMock(returncode=0)
            main()
            print_calls = [str(call_args) for call_args in mock_print.call_args_list]
            assert any('Ejecutando:' in msg for msg in print_calls)

    @patch('builtins.print')
    def test_error_message_no_args(self, mock_print):
        """Test que mensaje de error se muestra sin argumentos"""
        with patch.object(sys, 'argv', ['aetos']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            mock_print.assert_called()
            print_calls = [str(call_args) for call_args in mock_print.call_args_list]
            assert any('Uso:' in msg for msg in print_calls)

    @patch('builtins.print')
    def test_help_message_shows_available_commands(self, mock_print):
        """Test que mensaje de ayuda muestra comandos disponibles"""
        with patch.object(sys, 'argv', ['aetos']):
            with pytest.raises(SystemExit):
                main()
            print_calls = [str(call_args) for call_args in mock_print.call_args_list]
            assert any('config show' in msg for msg in print_calls)
            assert any('config set' in msg for msg in print_calls)
            assert any('config reset' in msg for msg in print_calls)
