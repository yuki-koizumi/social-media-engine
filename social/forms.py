from django import forms
from .models import Tweet, VerificationTask

import io
import json
import datetime

class TweetUploadForm(forms.Form):
    file = forms.FileField(label='File containing tweets in json format in each line',
                           widget=forms.FileInput(attrs={'class': 'form-control'}))

    def import_tweet(self):
        tweet_file = io.TextIOWrapper(self.cleaned_data['file'])
        for tweet_json in tweet_file:
            tweet = json.loads(tweet_json)

            full_address = ', '.join(tweet['address']['full_address']) if 'full_address' in tweet['address'] else None
            prefecture   = ', '.join(tweet['address']['prefecture']) if 'prefecture' in tweet['address'] else None
            city         = ', '.join(tweet['address']['city']) if 'city' in tweet['address'] else None
            town         = ', '.join(tweet['address']['town']) if 'town' in tweet['address'] else None
            village      = ', '.join(tweet['address']['village']) if 'village' in tweet['address'] else None

            tm = Tweet.objects.create(json                  = tweet,
                                      full_text             = tweet['full_text'],
                                      screen_name           = tweet['user']['screen_name'],
                                      tweet_id              = tweet['id'],
                                      user_id               = tweet['user']['id'],
                                      created_at            = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y'),
                                      address_type          = tweet['address']['address_type'],
                                      prefecture            = prefecture,
                                      city                  = city,
                                      town                  = town,
                                      village               = village,
                                      full_address          = full_address,
                                      firsthand_result      = tweet['filter']['firsthand'],
                                      firsthand0_score      = tweet['filter']['firsthand_score'][0],
                                      firsthand1_score      = tweet['filter']['firsthand_score'][1],
                                      firsthand2_score      = tweet['filter']['firsthand_score'][2],
                                      relevance_result      = tweet['filter']['relevance'],
                                      relevance0_score      = tweet['filter']['relevance_score'][0],
                                      relevance1_score      = tweet['filter']['relevance_score'][1],
                                      rescue_result         = tweet['filter']['rescue'],
                                      rescue0_score         = tweet['filter']['rescue_score'][0],
                                      rescue1_score         = tweet['filter']['rescue_score'][1],
                                      in_reply_to_status_id = tweet['in_reply_to_status_id'] if 'in_reply_to_status_id' in tweet else None,
                                      in_reply_to_user_id   = tweet['in_reply_to_user_id'] if 'in_reply_to_user_id' in tweet else None,
                                      is_quote_status       = tweet['is_quote_status'] if 'is_quote_status' in tweet else None)

            tm.save()


class VolunteerTaskUpdateForm(forms.ModelForm):
    class Meta:
        model = VerificationTask
        fields = ('result', 'status', 'address', 'note', 'image')
        widgets = { 'result': forms.RadioSelect(attrs={'class': 'btn-check'}),
                    'status': forms.RadioSelect(attrs={'class': 'btn-check'}),
                    'address': forms.TextInput(attrs={'class': 'form-control'}),
                    'note': forms.Textarea(attrs={'class': 'form-control'}),
                    'image':  forms.FileInput(attrs={'class': 'form-control'})}

