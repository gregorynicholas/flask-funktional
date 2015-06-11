flask-funktional
================

[flask](http://flask.pocoo.org) extension to make functional testing easier.


<br>
**build-status:**

`master ` [![travis-ci build-status: master](https://secure.travis-ci.org/gregorynicholas/flask-funktional.svg?branch=master)](https://travis-ci.org/gregorynicholas/flask-funktional)
<br>
`develop` [![travis-ci build-status: develop](https://secure.travis-ci.org/gregorynicholas/flask-funktional.svg?branch=develop)](https://travis-ci.org/gregorynicholas/flask-funktional)


**links:**

* [homepage](http://gregorynicholas.github.io/flask-funktional)
* [source](http://github.com/gregorynicholas/flask-funktional)
* [python-package](http://packages.python.org/flask-funktional)
* [changelog](https://github.com/gregorynicholas/flask-funktional/blob/master/CHANGES.md)
* [github-issues](https://github.com/gregorynicholas/flask-funktional/issues)
* [travis-ci](http://travis-ci.org/gregorynicholas/flask-funktional)


<br>
-----
<br>


### getting started


install with pip:

    $ pip install flask-funktional


<br>
-----
<br>


### features

* completely seamless
    * nifty pre / post class setup code means you don't have to make repetitive `super()` calls.
    * focus on signals + hooks to help avoid having to write shitty code in your subclasses.
* enables and promotes the healthy use of `url_for` instead of hard coding url paths.
    * boom, less brittle code.
    * oddly, there's a lot of things that go wrong out of the box with this, so funktional removes all of this shity setup code from your actual test code.
* test file uploads in flask applications. right ouf of the box.
    * perfect for your [shitty] little csv uploader tools.
* cross platform
    * works in any standard python flask application + platform, such as [amazon-aws](http://aws.amazon.com) or [google app-engine](http://appengine.google.com).


<br>
-----
<br>


### example usage

* [todo]
