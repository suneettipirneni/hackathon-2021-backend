# flake8: noqa
import json
from src.models.hacker import Hacker
from src.models.user import ROLES
from tests.base import BaseTestCase
from datetime import datetime


class TestHackersBlueprint(BaseTestCase):
    """Tests for the Hackers Endpoints"""

    """create_hacker"""

    def test_create_hacker(self):
        now = datetime.now()
        res = self.client.post(
            "/api/hackers/",
            data={"hacker": json.dumps(
                {
                    "username": "foobar",
                    "email": "foobar@email.com",
                    "password": "123456",
                    "date": now.isoformat(),
                }
            )},
            content_type="multipart/form-data",
        )

        self.assertEqual(res.status_code, 201)
        self.assertEqual(Hacker.objects.count(), 1)

    def test_create_hacker_invalid_json(self):
        res = self.client.post(
            "/api/hackers/", data={"hacker": json.dumps({})}, content_type="multipart/form-data"
        )

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(Hacker.objects.count(), 0)

    def test_create_hacker_duplicate_user(self):
        now = datetime.now()
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER,
        )

        res = self.client.post(
            "/api/hackers/",
            data={"hacker": json.dumps(
                {
                    "username": "foobar",
                    "email": "foobar@email.com",
                    "password": "123456",
                    "date": now.isoformat(),
                }
            )},
            content_type="multipart/form-data",
        )

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 409)
        self.assertIn(
            "Sorry, that username or email already exists.", data["description"]
        )
        self.assertEqual(Hacker.objects.count(), 1)

    def test_create_hacker_invalid_datatypes(self):
        res = self.client.post(
            "/api/hackers/",
            data={"hacker": json.dumps(
                {"username": "foobar", "email": "notanemail", "password": "123456"}
            )},
            content_type="multipart/form-data",
        )

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["name"], "Bad Request")
        self.assertEqual(Hacker.objects.count(), 0)

    """get_user_search"""

    def test_get_user_search(self):
        h = Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER,
        )

        res = self.client.get("/api/hackers/foobar/")

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(h.username, data["User Name"])

    def test_get_user_search_not_found(self):
        res = self.client.get("/api/hackers/foobar/")

        self.assertEqual(res.status_code, 404)

    """delete_hacker"""

    def test_delete_hacker(self):
        with self.assertRaises(TypeError):
            Hacker.createOne(
                username="foobar",
                email="foobar@email.com",
                password="123456",
                roles=ROLES.HACKER,
            )

            token = self.login_user(ROLES.ADMIN)

            res = self.client.delete("/api/hackers/foobar/", headers=[("sid", token)])


            self.assertEqual(res.status_code, 201)
            self.assertEqual(Hacker.objects.count(), 0)

    def test_delete_hacker_as_self(self):
        with self.assertRaises(TypeError):
            hacker = Hacker.createOne(
                username="foobar",
                email="foobar@email.com",
                password="123456",
                roles=ROLES.HACKER,
            )

            token = self.login_as(hacker, password="123456")

            res = self.client.delete("/api/hackers/foobar/", headers=[("sid", token)])


            self.assertEqual(res.status_code, 201)
            self.assertEqual(Hacker.objects.count(), 0)

    def test_delete_hacker_as_other_hacker(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER,
        )

        token = self.login_user(ROLES.HACKER)

        res = self.client.delete("/api/hackers/foobar/", headers=[("sid", token)])

        self.assertEqual(res.status_code, 401)

    def test_delete_hacker_not_found(self):

        token = self.login_user(ROLES.ADMIN)

        res = self.client.delete("/api/hackers/foobar/", headers=[("sid", token)])

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 404)
        self.assertIn(
            "The specified hacker does not exist in the database.", data["description"]
        )

    """update_hacker"""

    def test_update_user_profile_settings(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER,
        )

        res = self.client.put(
            "/api/hackers/foobar/",
            data=json.dumps({"email": "schmuckbar@mensch.com"}),
            content_type="application/json",
        )

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 201)

        updated = Hacker.findOne(username="foobar")

        self.assertEqual(updated.email, "schmuckbar@mensch.com")

    def test_update_user_profile_settings_same_email(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER
        )

        res = self.client.put(
            "/api/hackers/foobar/",
            data=json.dumps({"first_name": "schmuckbar"}),
            content_type="application/json",
        )

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 201)

        updated = Hacker.findOne(username="foobar")

        self.assertEqual(updated.first_name, "schmuckbar")

    def test_update_user_profile_settings_invalid_json(self):
        res = self.client.put(
            "/api/hackers/foobar/", data=json.dumps({}), content_type="application/json"
        )

        self.assertEqual(res.status_code, 400)

    def test_update_user_profile_settings_not_found(self):
        res = self.client.put(
            "/api/hackers/foobar/",
            data=json.dumps({"email": "schmuckbar@mensch.com"}),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 404)

    def test_update_user_profile_settings_invalid_datatypes(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER,
        )

        res = self.client.put(
            "/api/hackers/foobar/",
            data=json.dumps({"email": 2}),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 400)

    """hacker_settings"""
    def test_hacker_settings(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER
        )

        res = self.client.get("/api/hackers/foobar/settings/")

        self.assertEqual(res.status_code, 200)


    def test_hacker_settings_not_found(self):

        res = self.client.get("/api/hackers/foobar/settings/")

        self.assertEqual(res.status_code, 404)

    """accept_hacker"""
    def test_accept_hacker(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER
        )

        token = self.login_user(ROLES.ADMIN)

        res = self.client.put(
            "/api/hackers/foobar/accept/",
            headers=[("sid", token)]
        )

        self.assertEqual(res.status_code, 201)

    def test_accept_hacker_not_found(self):

        token = self.login_user(ROLES.ADMIN)

        res = self.client.put(
            "/api/hackers/foobar/accept/",
            headers=[("sid", token)]
        )

        self.assertEqual(res.status_code, 404)

    """get_all_hackers"""
    def test_get_all_hackers(self):
        Hacker.createOne(
            username="foobar",
            email="foobar@email.com",
            password="123456",
            roles=ROLES.HACKER
        )

        Hacker.createOne(
            username="foobar1",
            email="foobar1@email.com",
            password="123456",
            roles=ROLES.HACKER
        )

        res = self.client.get("/api/hackers/get_all_hackers/")

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data["hackers"][0]["username"], "foobar")
        self.assertEqual(data["hackers"][1]["username"], "foobar1")

    
    def test_get_all_hackers_not_found(self):
        res = self.client.get("/api/hackers/get_all_hackers/")

        data = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["name"], "Not Found")
