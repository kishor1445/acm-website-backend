import pytest
import requests
import random
import string


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"


dynamic_email = f"acm-test-{''.join([random.choice(string.ascii_lowercase) for x in range(10)])}@gmail.com"


def run_status_test(url, test_data, method=requests.get):
    print()
    for data in test_data:
        full_url = url + "/" + data[0]
        r = method(full_url)
        assert r.status_code == data[1]
        print(f"Test Passed: ✅")


def test_subscribe(base_url):
    url = base_url + "/subscribe"
    data = [
        (dynamic_email, 201),  # Create
        (
            "acm-test-somethingthatdoesnotexists@abcdfelakdf.com",
            400,
        ),  # Invalid Email ID
        ("acm-test-kishorramanan5@mail.com", 400),  # Untrusted Domain
        (dynamic_email, 400),  # Already exists
    ]
    run_status_test(url, data)


def test_unsubscribe(base_url):
    url = base_url + "/subscribe"
    data = [
        (dynamic_email, 204),  # Delete
        (
            "acm-test-somethingthatdoesnotexists@abcdfelakdf.com",
            400,
        ),  # Invalid Email ID
        (dynamic_email, 404),  # Not exist
    ]
    run_status_test(url, data, requests.delete)


# TODO: Complete remaining tests
