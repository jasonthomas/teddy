#!/bin/env python
#jason thomas
import praw
import random


def get(sub, limit=40):
    urls = []
    r = praw.Reddit(user_agent='teddy')
    submissions = r.get_subreddit(sub).get_hot(limit=limit)
    for submission in submissions:
        urls.append(submission.url)

    return random.choice(urls)
