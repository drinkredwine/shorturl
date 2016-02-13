#!/bin/env python3

from flask import flash, Flask, request, redirect, render_template, url_for
from os import urandom
import logging
import random
import redis
import string


# Create application object and read config from config.py
app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = urandom(app.config['KEYLENGTH'])

redis = redis.Redis(host=app.config['REDISHOST'],
                    port=app.config['REDISPORT'],
                    db=app.config['REDISDB'],
                    password=app.config['REDISPASSWD'])


def GetExpSeconds(unit, value):
    if unit == 'seconds':
        return value
    elif unit == 'minutes':
        return (60 * value)
    elif unit == 'hours':
        return (60 * 60 * value)
    else:
        return 0

def GenShortKey(length=8):
    """ Function to generate a short random string to use as a key to build
        the short URLs. Default is 8 characters in length. """
    validchars = string.ascii_letters + string.digits
    shortkey = ''

    for i in range(length):
        shortkey += random.SystemRandom().choice(validchars)

    return shortkey


def GetFullURL(key):
    """ Get value for specified key. This should be a valid URL. """

    # Attempt to get the full URL, will return None if key does not exist
    try:
        return redis.get(key).decode('utf-8')
    # Return None on any exception in the event of any exception
    except:
        return None


def InsertData(shorturl, fullurl, expiration=0):
    """ Insert key and full URL into the database for later access. """
    try:
        # Set the key only if it does not exist to prevent overwriting
        # exisitng URL data.
        redis.set(shorturl, fullurl)

        # Set expiration for key to remove shot URL after x seconds
        if expiration > 0:
            redis.setex(shorturl, fullurl, expiration)
        return True
    except:
        return False


@app.route('/')
def ShowIndex():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def InsertRoute():
    siteurl = app.config['SITEURL']

    furl = request.form['fullurl']
    expunit = request.form['expunit']
    if request.form['expval']:
        expval = int(request.form['expval'])
    else:
        expval = 0

    expiration = GetExpSeconds(expunit, expval)

    if app.config['KEYLENGTH']:
        skey = GenShortKey(app.config['KEYLENGTH'])
    else:
        skey = GenShortKey()

    # If trailing / is not present add it to ensure a valid URL
    if siteurl.endswith('/'):
        surl = siteurl + skey
    else:
        surl = siteurl + '/' + skey

    if InsertData(skey, furl, expiration):
        # Show a status page with the full URL and short URL equivalent
        return render_template('index.html', fullurl=furl, shorturl=surl)
    else:
        flash('Error encountered saving data')
        return redirect(url_for('ShowIndex'))


@app.route('/<urlkey>')
def ExpandURL(urlkey):
    """ Attempt to open the URL matching the provided key. """
    furl = GetFullURL(urlkey)
    if furl:
        return redirect(furl)
    else:
        flash('Invalid or missing short URL')
        return redirect(url_for('ShowIndex'))


@app.route('/<urlkey>/preview')
def ViewURL(urlkey):
    furl = GetFullURL(urlkey)

    if furl:
        surl = app.config['SITEURL'] + urlkey
        return render_template('preview.html', fullurl=furl, shorturl=surl)
    else:
        flash('Preview failed: invalid or missing key')
        return render_template('index.html')


if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
