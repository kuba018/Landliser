# backend/conftest.py

import pytest

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Pozwala wszystkim testom korzystać z bazy danych Django bez pisania @pytest.mark.django_db."""
    pass
