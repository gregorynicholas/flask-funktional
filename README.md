flask-funktional
================

[flask](http://flask.pocoo.org) extension which hopes to make functional testing easier.


[![Build Status](https://secure.travis-ci.org/gregorynicholas/flask-funktional.png?branch=master)](https://travis-ci.org/gregorynicholas/flask-funktional)


* [docs](http://gregorynicholas.github.io/flask-funktional)
* [source](http://github.com/gregorynicholas/flask-funktional)
* [package](http://packages.python.org/flask-funktional)
* [changelog](https://github.com/gregorynicholas/flask-funktional/blob/master/CHANGES.md)


-----


### getting started

install with *pip*:

    pip install flask-funktional

-----


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
    * works in any standard python flask application + platform, such as amazon or google app engine.
