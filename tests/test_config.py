"""Testes do módulo de configuração.

O que está sendo testado:
    - Carregamento correto das configurações padrão
    - Validação de valores inválidos
    - Existência dos diretórios do projeto
    - Imutabilidade do objeto Settings

Por que esses testes são importantes:
    - Configuração é a base do projeto — se ela falhar,
      tudo falha.
    - Validar cedo (fail fast) evita bugs difíceis de
      rastrear em produção.
    - Garantir imutabilidade previne alterações acidentais.
"""

from pathlib import Path

import pytest

from src.utils.config import Settings, BASE_DIR, DATA_DIR, MODELS_DIR


class TestSettingsDefaults:
    """Testa se as configurações padrão são carregadas corretamente."""

    def test_default_environment(self, sample_settings: Settings) -> None:
        """O ambiente padrão deve ser 'development'."""
        assert sample_settings.environment == "development"

    def test_default_log_level(self, sample_settings: Settings) -> None:
        """O nível de log padrão deve ser 'DEBUG'."""
        assert sample_settings.log_level == "DEBUG"

    def test_default_ocr_engine(self, sample_settings: Settings) -> None:
        """A engine OCR padrão deve ser 'tesseract'."""
        assert sample_settings.ocr_engine == "tesseract"

    def test_default_ocr_language(self, sample_settings: Settings) -> None:
        """O idioma OCR padrão deve ser 'por' (português)."""
        assert sample_settings.ocr_language == "por"


class TestSettingsValidation:
    """Testa validações dos valores de configuração."""

    def test_invalid_environment_raises_error(self) -> None:
        """Deve rejeitar ambientes inválidos."""
        with pytest.raises(ValueError, match="Ambiente inválido"):
            Settings(environment="invalid")

    def test_invalid_ocr_engine_raises_error(self) -> None:
        """Deve rejeitar engines OCR inválidas."""
        with pytest.raises(ValueError, match="Engine OCR inválida"):
            Settings(ocr_engine="invalid")

    def test_valid_environments(self) -> None:
        """Deve aceitar todos os ambientes válidos."""
        for env in ("development", "staging", "production"):
            s = Settings(environment=env)
            assert s.environment == env

    def test_valid_ocr_engines(self) -> None:
        """Deve aceitar todas as engines OCR válidas."""
        for engine in ("tesseract", "easyocr"):
            s = Settings(ocr_engine=engine)
            assert s.ocr_engine == engine


class TestSettingsImmutability:
    """Testa que Settings é imutável (frozen dataclass)."""

    def test_cannot_modify_environment(self, sample_settings: Settings) -> None:
        """Não deve ser possível alterar o ambiente após criação."""
        with pytest.raises(AttributeError):
            sample_settings.environment = "production"  # type: ignore[misc]

    def test_cannot_modify_log_level(self, sample_settings: Settings) -> None:
        """Não deve ser possível alterar o log level após criação."""
        with pytest.raises(AttributeError):
            sample_settings.log_level = "ERROR"  # type: ignore[misc]


class TestProjectDirectories:
    """Testa a existência dos diretórios do projeto."""

    def test_base_dir_exists(self) -> None:
        """O diretório base do projeto deve existir."""
        assert BASE_DIR.exists()
        assert BASE_DIR.is_dir()

    def test_data_dir_exists(self) -> None:
        """O diretório de dados deve existir."""
        assert DATA_DIR.exists()
        assert DATA_DIR.is_dir()

    def test_models_dir_exists(self) -> None:
        """O diretório de modelos deve existir."""
        assert MODELS_DIR.exists()
        assert MODELS_DIR.is_dir()

    def test_base_dir_contains_src(self) -> None:
        """O diretório base deve conter o diretório src/."""
        assert (BASE_DIR / "src").exists()

    def test_settings_repr(self, sample_settings: Settings) -> None:
        """A representação deve conter informações úteis."""
        repr_str = repr(sample_settings)
        assert "environment" in repr_str
        assert "development" in repr_str
