# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(".."))

# Create mock settings
class MockSettings:
    DB_URL = "sqlite+aiosqlite:///./test.db"
    JWT_SECRET = "test_secret"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_SECONDS = 3600
    MAIL_USERNAME = "test@example.com"
    MAIL_PASSWORD = "test_password"
    MAIL_FROM = "test@example.com"
    MAIL_PORT = 587
    MAIL_SERVER = "smtp.example.com"
    MAIL_FROM_NAME = "Test System"
    CLOUDINARY_NAME = "test_cloud"
    CLOUDINARY_API_KEY = "test_key"
    CLOUDINARY_API_SECRET = "test_secret"
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = True
    REDIS_DOMAIN = "localhost"
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 0

# Mock FastAPI dependencies
class AsyncMock(MagicMock):
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def __call__(self, *args, **kwargs):
        return True

# Mock database session
db_mock = AsyncMock()
sys.modules['src.database.db'] = db_mock
db_mock.get_db = AsyncMock()
db_mock.sessionmanager = AsyncMock()

# Mock config module
config_mock = MagicMock()
config_mock.settings = MockSettings()
sys.modules['src.conf.config'] = config_mock

# Mock FastAPI dependencies
class MockOAuth2PasswordRequestForm:
    def __init__(self, username: str = "test", password: str = "test", scope: str = "", client_id: str = None, client_secret: str = None):
        self.username = username
        self.password = password
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret

class MockOAuth2PasswordBearer(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def __call__(self, *args, **kwargs):
        return "mocked_token"

class MockSecurity:
    def __init__(self):
        self.OAuth2PasswordBearer = MockOAuth2PasswordBearer
        self.OAuth2PasswordRequestForm = MockOAuth2PasswordRequestForm
        self.OpenIdConnect = MagicMock
        self.SecurityBase = MagicMock
        self.base = MagicMock()
        self.oauth2 = MagicMock()
        self.open_id_connect_url = MagicMock()

# Mock FastAPI dependencies
sys.modules['fastapi.security'] = MockSecurity()
sys.modules['fastapi.security.oauth2'] = MagicMock()
sys.modules['fastapi.security.base'] = MagicMock()
sys.modules['fastapi.security.open_id_connect_url'] = MagicMock()
sys.modules['fastapi.security.utils'] = MagicMock()
sys.modules['fastapi.dependencies.utils'] = MagicMock()
sys.modules['fastapi.routing'] = MagicMock()

# Mock FastAPI
class MockFastAPI:
    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.get('prefix', '')
        self.tags = kwargs.get('tags', [])

    def get(self, path, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def post(self, path, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def put(self, path, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def delete(self, path, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

class MockHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class MockAPIRouter(MockFastAPI):
    pass

class MockRequest:
    def __init__(self):
        pass

class MockDepends:
    def __init__(self, dependency=None):
        self.dependency = dependency

    def __call__(self, *args, **kwargs):
        if self.dependency:
            return self.dependency(*args, **kwargs)
        return None

class MockSecurity:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return None

class MockOAuth2PasswordRequestForm:
    def __init__(self, username: str = "test", password: str = "test", scope: str = "", client_id: str = None, client_secret: str = None):
        self.username = username
        self.password = password
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret

# Create a mock FastAPI module
mock_fastapi = type('MockFastAPI', (), {
    'FastAPI': MockFastAPI,
    'APIRouter': MockAPIRouter,
    'HTTPException': MockHTTPException,
    'Depends': MockDepends,
    'Request': MockRequest,
    'Security': MockSecurity,
    'status': type('status', (), {
        'HTTP_200_OK': 200,
        'HTTP_201_CREATED': 201,
        'HTTP_204_NO_CONTENT': 204,
        'HTTP_400_BAD_REQUEST': 400,
        'HTTP_401_UNAUTHORIZED': 401,
        'HTTP_403_FORBIDDEN': 403,
        'HTTP_404_NOT_FOUND': 404,
        'HTTP_409_CONFLICT': 409,
        'HTTP_422_UNPROCESSABLE_ENTITY': 422,
        'HTTP_500_INTERNAL_SERVER_ERROR': 500
    })
})

sys.modules['fastapi'] = mock_fastapi
sys.modules['fastapi.security'] = type('MockSecurity', (), {
    'OAuth2PasswordRequestForm': MockOAuth2PasswordRequestForm,
    'OAuth2PasswordBearer': MockOAuth2PasswordBearer,
    'SecurityBase': MagicMock,
})

# Mock pydantic
class MockFieldValidator:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return lambda x: x

class MockBaseModel:
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def model_validate(cls, *args, **kwargs):
        return cls()

class MockSecretStr:
    def __init__(self, value: str = ""):
        self._value = value

    def get_secret_value(self) -> str:
        return self._value

def mock_conint(*args, **kwargs):
    return int

# Mock Pydantic modules
class MockPydanticModule:
    def __init__(self):
        self.BaseModel = MockBaseModel
        self.Field = lambda *args, **kwargs: None
        self.EmailStr = str
        self.ConfigDict = lambda *args, **kwargs: None
        self.field_validator = MockFieldValidator
        self.DirectoryPath = str
        self.SecretStr = MockSecretStr
        self.conint = mock_conint

class MockPydanticInternalConfigModule:
    def __init__(self):
        self.config_keys = {
            'title': str,
            'json_schema_extra': dict,
            'extra': str,
            'frozen': bool,
            'populate_by_name': bool,
            'use_enum_values': bool,
            'validate_assignment': bool,
            'allow_population_by_field_name': bool,
            'allow_mutation': bool,
            'allow_reuse': bool,
            'schema_extra': dict
        }

class MockPydanticInternalSignatureModule:
    def __init__(self):
        pass

    def get_signature(self, *args, **kwargs):
        return None

    def _field_name_for_signature(self, name: str) -> str:
        return name

class MockPydanticInternalModule:
    def __init__(self):
        self._utils = type('_utils', (), {
            'lenient_issubclass': lambda cls, class_or_tuple: True
        })
        self._config = MockPydanticInternalConfigModule()
        self._signature = MockPydanticInternalSignatureModule()

# Create mock modules
mock_pydantic = MockPydanticModule()
mock_pydantic._internal = MockPydanticInternalModule()

class MockPydanticInternalUtilsModule:
    def __init__(self):
        pass

    def lenient_issubclass(self, cls, class_or_tuple):
        return True

    def _get_type(self, type_: type) -> type:
        return type_

    def is_union(self, type_: type) -> bool:
        return False

    def is_none_type(self, type_: type) -> bool:
        return type_ is type(None)

    def deep_update(self, mapping, *updating_mappings):
        updated_mapping = mapping.copy()
        for updating_mapping in updating_mappings:
            for k, v in updating_mapping.items():
                if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                    updated_mapping[k] = self.deep_update(updated_mapping[k], v)
                else:
                    updated_mapping[k] = v
        return updated_mapping

sys.modules['pydantic'] = mock_pydantic
sys.modules['pydantic._internal'] = mock_pydantic._internal
sys.modules['pydantic._internal._config'] = mock_pydantic._internal._config
sys.modules['pydantic._internal._signature'] = mock_pydantic._internal._signature
sys.modules['pydantic._internal._utils'] = MockPydanticInternalUtilsModule()

# Mock additional Pydantic modules
sys.modules['pydantic.config'] = type('MockPydanticConfig', (), {})
sys.modules['pydantic.fields'] = type('MockPydanticFields', (), {})
sys.modules['pydantic.main'] = type('MockPydanticMain', (), {})

# Mock FastAPI middleware
class MockMiddleware:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return None

class MockCORSMiddleware(MockMiddleware):
    pass

sys.modules['fastapi.middleware'] = type('MockMiddleware', (), {
    'Middleware': MockMiddleware,
})

sys.modules['fastapi.middleware.cors'] = type('MockCORS', (), {
    'CORSMiddleware': MockCORSMiddleware,
})

# Mock FastAPI background tasks
class MockBackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))

sys.modules['fastapi'].BackgroundTasks = MockBackgroundTasks


project = 'GoIT Python Web HW 012'
copyright = '2025, Yuliia Nazymko'
author = 'Yuliia Nazymko'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
