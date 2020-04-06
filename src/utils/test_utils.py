"""
Various helpful functions and classes for running tests.
"""

import abc
import dotenv
import os
import random
import time

from django.test import TestCase, Client, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from uuid import UUID

from users.models import User

"""
---------------------------------------------------
Helper functions
---------------------------------------------------
"""

# Methods for randomly generating fields for User instances
random_uuid = lambda rd: UUID(int=rd.getrandbits(128)).hex
random_username = lambda rd: f"meepy-{random_uuid(rd)[:10]}"
random_email = lambda rd: f"meepy-{random_uuid(rd)[:10]}@colorado.edu"
random_password = lambda rd: random_uuid(rd)


def create_random_user(rd):
    username = random_username(rd)
    email = random_email(rd)
    password = random_password(rd)
    return username, email, password


"""
---------------------------------------------------
Generic abstract testing class
---------------------------------------------------
"""


class AbstractTestCase(abc.ABC):
    def setUp(self, seed=0, create_user=False, preauth=False):
        ### Seed RNG for consistent results
        self.rd = random.Random()
        self.rd.seed(seed)

        ### Create a test username, email, and password for tests involving
        ### users.
        self.username = random_username(self.rd)
        self.password = random_password(self.rd)
        self.email = random_email(self.rd)

        ### If preauth or create_user == True, then create a new user for the
        ### test. In addition, if preauth == True, then we automatically log
        ### in as the user.
        self.client = Client()
        if preauth or create_user:
            self.user = User.objects.create_user(
                email=self.email, username=self.username, password=self.password
            )

        if preauth:
            self.client.force_login(self.user)

    @abc.abstractmethod
    def fail(self, *args, **kwargs):
        pass

    def wait_for(self, test, max_wait=10, interval=0.25):
        """
        Wait for a test to pass. When it passes we can continue execution. If the
        wait exceeds the time limit, then we throw an error.

        Parameters
        ----------
        test
            A function that takes no inputs. If the test fails then test() should
            raise an exception of some sort. If it succeeds, then no exception
            should be raised.

        Keyword parameters
        ----------
        max_wait (float) (default = 5)
            The maximum amount of time (in seconds) we are willing to wait for the
            test to pass. Once this time has been exceeded, we call self.fail. Must
            be non-negative.

        interval (float) (default = 0.1)
            The amount of time (in seconds) to wait between evaluations of test().
            Must be non-negative.

        Returns
        ----------
        None
        """
        if not isinstance(max_wait, (int, float)) or max_wait < 0:
            raise ValueError("max_wait must be a non-negative number.")
        if not isinstance(interval, (int, float)) or interval < 0:
            raise ValueError("interval must be a non-negative number.")

        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                test()
                ex = None
                break
            except Exception as _:
                ex = _

        if ex:
            raise ex


"""
---------------------------------------------------
Functional testing base class
---------------------------------------------------
"""


@tag("functional-tests")
class FunctionalTest(StaticLiveServerTestCase, AbstractTestCase):
    """
    Base class for functional tests.
    """

    def setUp(self, **kwargs):
        AbstractTestCase.setUp(self, **kwargs)
        dotenv.load_dotenv()
        staging_server = os.getenv("STAGING_SERVER")
        if staging_server:
            self.live_server_url = staging_server

            # Authenticate to staging server
            self.fail("TODO")

        ### Create a Selenium WebDriver to run functional tests
        browser = os.getenv("BROWSER", "Firefox")
        if browser.lower() == "firefox":
            self.browser = webdriver.Firefox()
        elif browser.lower() == "chrome":
            self.browser = webdriver.Chrome()
        else:
            raise Exception(f"Browser type '{browser}' not recognized.")

        if kwargs.get("preauth"):
            self.client.force_login(self.user)
            cookie = self.client.cookies["sessionid"]
            self.browser.get(self.live_server_url)
            self.browser.add_cookie(
                {
                    "name": "sessionid",
                    "value": cookie.value,
                    "secure": False,
                    "path": "/",
                }
            )

    def tearDown(self):
        self.browser.quit()


"""
---------------------------------------------------
Unit testing base class
---------------------------------------------------
"""


@tag("unit-tests")
class UnitTest(TestCase, AbstractTestCase):
    def setUp(self, **kwargs):
        AbstractTestCase.setUp(self, **kwargs)
