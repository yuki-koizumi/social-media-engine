from django.db import models
import uuid

# Create your models here.

class Tweet(models.Model):
    json        = models.JSONField()
    full_text   = models.CharField(max_length=512)
    screen_name = models.CharField(max_length=16)
    tweet_id    = models.BigIntegerField()
    user_id     = models.BigIntegerField()
    created_at  = models.DateTimeField()

    address_type = models.IntegerField()
    prefecture   = models.CharField(max_length=512, null=True, blank=True)
    city         = models.CharField(max_length=512, null=True, blank=True)
    town         = models.CharField(max_length=512, null=True, blank=True)
    village      = models.CharField(max_length=512, null=True, blank=True)
    full_address = models.CharField(max_length=512, null=True, blank=True)

    firsthand_result = models.IntegerField()
    firsthand0_score = models.FloatField()
    firsthand1_score = models.FloatField()
    firsthand2_score = models.FloatField()

    relevance_result = models.IntegerField()
    relevance0_score = models.FloatField()
    relevance1_score = models.FloatField()

    rescue_result = models.IntegerField()
    rescue0_score = models.FloatField()
    rescue1_score = models.FloatField()

    in_reply_to_status_id = models.BigIntegerField(null=True, blank=True)
    in_reply_to_user_id   = models.BigIntegerField(null=True, blank=True)
    is_quote_status       = models.BooleanField(default=False, null=True)

    urgent_reaction   = models.IntegerField(default=0)
    doubtful_reaction = models.IntegerField(default=0)

    firsthand0_reaction = models.IntegerField(default=0)
    firsthand1_reaction = models.IntegerField(default=0)
    firsthand2_reaction = models.IntegerField(default=0)

    relevance0_reaction = models.IntegerField(default=0)
    relevance1_reaction = models.IntegerField(default=0)

    rescue0_reaction = models.IntegerField(default=0)
    rescue1_reaction = models.IntegerField(default=0)

    inferred_address = models.JSONField(blank=True, null=True, default=list)

    similar_tweet = models.JSONField(blank=True, null=True, default=list)
    num_worker    = models.IntegerField(default=0)

    is_volunteer_verified = models.BooleanField(default=False)

    verification_result = models.IntegerField(blank=False, default=-1, null=True, choices=((0, 'Yes'), (1, 'No'), (2, 'Unsure')))
    verification_status = models.IntegerField(blank=False, default=-1, null=True, choices=((0, 'Ongoing'), (1, 'Completed'), (2, 'Unsure')))
    verification_note    = models.TextField(blank=True, null=True)
    verification_address = models.CharField(max_length=512, null=True, blank=True)

    firstresponder_status = models.IntegerField(blank=False, default=-1, null=True, choices=((0, 'Working'), (1, 'Resolved'), (2, 'Dismissed')))

    def __str__(self):
        return self.full_text

class VerificationTask(models.Model):
    tweet        = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='verification_task')
    user_id      = models.UUIDField(default=uuid.uuid4)
    result       = models.IntegerField(blank=False, default=-1, null=True, choices=((0, 'Yes'), (1, 'No'), (2, 'Unsure')))
    status       = models.IntegerField(blank=False, default=-1, null=True, choices=((0, 'Ongoing'), (1, 'Completed'), (2, 'Unsure')))
    address      = models.CharField(max_length=512, null=True, blank=True)
    note         = models.TextField(blank=True, null=True)
    image        = models.ImageField(blank=True, null=True, upload_to='image/')
    is_completed = models.BooleanField(default=False)

class FirstresponderTask(models.Model):
    tweet  = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='firstresponder_task')
    result = models.IntegerField(blank=True, null=True)
    is_started   = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
