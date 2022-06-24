from django.test import TestCase

# Create your tests here.
class AnimalTestCase(TestCase):
    def setUp(self):
        pass

    def test_api_setup(self):
        """"""
        self.assertEqual(1, 1)