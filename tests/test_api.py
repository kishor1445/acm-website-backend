import pytest
import requests
import random
import string


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000"


def test_user(base_url):
    print()
    sub_url = base_url + "/users"
    data = {
        "name": "Temp Name",
        "reg_no": 123456789,
        "email_id": "temp@gmail.com",
        "password": "12345678Ab@",
        "department": "CSE AI-ML",
        "university": "A University",
        "year": random.randint(1, 4),
    }
    for x in ((201, ""), (400, {"detail": "User Already Exists."})):
        run_status_test_with_data(sub_url, data, x[0], x[1], requests.post, "json")
    passed("Create")
    for x in ((204, ""), (400, {"detail": "User Not Found"})):
        run_status_test_with_data(sub_url, data, x[0], x[1], requests.delete, "json")
    passed("Delete")


def test_mail(base_url):
    print()
    dynamic_email = f"acm-test-{''.join([random.choice(string.ascii_lowercase) for _ in range(10)])}@gmail.com"
    sub_url = base_url + "/mail"
    for x in [(subscribe, "Subscribe"), (unsubscribe, "Unsubscribe")]:
        x[0](sub_url, dynamic_email)
        passed(x[1])


def passed(msg):
    print(f"{msg} Passed: ✅")


def run_status_test(url, test_data, method=requests.get):
    for data in test_data:
        full_url = url + "/" + data[0]
        r = method(full_url)
        assert r.status_code == data[1]


def run_status_test_with_data(url, payload, status, msg, method, loc):
    if loc == "json":
        res = method(url, json=payload)
    else:
        res = method(url, data=payload)
    if msg:
        assert res.json() == msg
    assert res.status_code == status


def subscribe(url, email):
    url = url + "/subscribe"
    data = [
        (email, 201),  # Create
        (
            "acm-test-somethingthatdoesnotexists@abcdfelakdf.com",
            400,
        ),  # Invalid Email ID
        ("acm-test-kishorramanan5@mail.com", 400),  # Untrusted Domain
        (email, 400),  # Already exists
    ]
    run_status_test(url, data)


def unsubscribe(url, email):
    url = url + "/subscribe"
    data = [
        (email, 204),  # Delete
        (
            "acm-test-somethingthatdoesnotexist@gmail.com",
            404,
        ),  # Not Exist
    ]
    run_status_test(url, data, requests.delete)
