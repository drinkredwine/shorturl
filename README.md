# shorturl
Python 3 Flask web application to generate short URLs.

### Requirements

- Redis server
- Python 3

requirements.txt:

```
Flask==0.10.1
itsdangerous==0.24
Jinja2==2.8
MarkupSafe==0.23
redis==2.10.5
Werkzeug==0.11.3
```

### Installation

Clone this repository into the document root for your virtual host.

Start the script manually or configure your favorite application and web servers to proxy to it.

### Configuration

Simply modify the following values at the top of the script to point to the appropriate location.

```
REDISHOST = 'localhost'
REDISPORT = '6379'
REDISDB = 0
REDISPASSWD = ''
SITEURL = 'http://example.com'
KEYLENGTH = 8
```