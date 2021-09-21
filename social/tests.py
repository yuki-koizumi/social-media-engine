from django.test import TestCase

# Create your tests here.

from .models import Tweet

def create_tweet():
    return Tweet.objects.create()

class TweetModelTest(TestCase):
    def test_tweet(self):
        pass
