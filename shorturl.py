#!/bin/env python3

from flask import flash, Flask, request, redirect, render_template, url_for
import random
import string

try:
    import redis
except:
    logging.error('redis module not loaded')


# Create application object and read config from config.py
app = Flask(__name__)
app.config.from_object('config')

redis = redis.Redis(host=app.config['REDISHOST'],
                    port=app.config['REDISPORT'],
                    db=app.config['REDISDB'],
                    password=app.config['REDISPASSWD'])


def GenShortKey():
    """ Function to generate a short random string to use as a key to build
        the short URLs. Default is 8 characters in length. """
    validchars = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(validchars) for i in range(8))


def GetValue(key):
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
        redis.setnx(shorturl, fullurl)

        # Set expiration for key to remove shot URL after x seconds
        if expiration > 0:
            redis.expire(shorturl, expiration)
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
    skey = GenShortKey()

    # If trailing / is not present add it to ensure a valid URL
    if siteurl.endswith('/'):
        surl = siteurl + skey
    else:
        surl = siteurl + '/' + skey

    # Only accept input that begins with the http protocol
    # Show an error on the page if invalid
    if not furl.startswith('http'):
        flash('Missing protocol for URL %s' % (furl))
        return redirect(url_for('ShowIndex'))
    else:
        if InsertData(skey, furl):
            flash('Full URL: %s' % furl)
            flash('Short URL: %s' % surl)

        # Show a status page with the full URL and short URL equivalent
        return render_template('index.html', fullurl=furl, shorturl=surl)


@app.route('/<urlkey>')
def ExpandURL(urlkey):
    """ Attempt to open the URL matching the provided key. """
    furl = GetValue(urlkey)
    if furl:
        return redirect(furl)
    else:
        flash('Invalid or missing short URL')
        return redirect(url_for('ShowIndex'))


if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
