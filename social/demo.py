#!/usr/bin/env python

import json
import datetime
import numpy as np
import regex
import itertools

from .models import Tweet, VerificationTask, FirstresponderTask

def load_tweet_db(file_name):
    with open(file_name, mode='r') as f:
        db = [json.loads(x) for x in f]
    return db

def create_tweet_data(tweet):
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

    return tm

def create_volunteer_task(tweet_model):
    v = VerificationTask.objects.create(tweet=tweet_model)
    return v

def create_firstresponder_task(tweet_model):
    f = FirstresponderTask.objects.create(tweet=tweet_model)
    return f

def create_crowd_reaction(tweet_model, rng):
    if not rng:
        rng = np.random.default_rng(seed = 1)

    num_crowd = rng.poisson(lam=tweet_model.relevance1_score * 1000)
    num_crowd = num_crowd if num_crowd > 10 else 10

    tweet_model.firsthand0_reaction = rng.binomial(num_crowd, p=tweet_model.firsthand0_score)
    tweet_model.firsthand1_reaction = rng.binomial(num_crowd, p=tweet_model.firsthand1_score)
    tweet_model.firsthand2_reaction = rng.binomial(num_crowd, p=tweet_model.firsthand2_score)

    tweet_model.rescue0_reaction    = rng.binomial(num_crowd, p=tweet_model.rescue0_score)
    tweet_model.rescue1_reaction    = rng.binomial(num_crowd, p=tweet_model.rescue1_score)

    tweet_model.relevance0_reaction = rng.binomial(num_crowd, p=tweet_model.relevance0_score)
    tweet_model.relevance1_reaction = rng.binomial(num_crowd, p=tweet_model.relevance1_score)

    tweet_model.urgent_reaction     = rng.binomial(num_crowd, p=tweet_model.relevance1_score)
    tweet_model.doubtful_reaction   = rng.binomial(num_crowd, p=tweet_model.relevance0_score)

    return tweet_model

def extract_address(tweet):
    return tweet['address']['full_address'] if 'full_address' in tweet['address'] else None

def extract_address_list(db):
    addr_list = [extract_address(t) for t in db]
    addr_list = filter(None, addr_list)
    addr_set  = set(itertools.chain.from_iterable(addr_list))
    return list(addr_set)

def sanitize_text(full_text):
    full_text = regex.sub(r'^Retweeted .*?:\s*', '', full_text)
    return full_text

def sanitize_tweet_db(db):
    for tweet in db:
        tweet['full_text'] = sanitize_text(tweet['full_text'])
    return db

def create_demo_data(input_file):
    db  = load_tweet_db(input_file)
    rng = np.random.default_rng(seed=1)

    address_list = extract_address_list(db)

    db = sanitize_tweet_db(db)

    for tweet in db:
        tm = create_tweet_data(tweet)
        tm = create_crowd_reaction(tm, rng=rng)

        num_volunteer = rng.poisson(3)
        for i in range(num_volunteer):
            v = create_volunteer_task(tm)
            v.save()

        if tm.relevance0_score > 0.9 and tm.address_type == 1 and rng.random() < 0.3:
            f = create_firstresponder_task(tm)
            f.save()

        tm.save()
    return
