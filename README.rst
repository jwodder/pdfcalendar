|repostatus| |ci-status| |license|

.. |repostatus| image:: https://www.repostatus.org/badges/latest/concept.svg
    :target: https://www.repostatus.org/#concept
    :alt: Project Status: Concept – Minimal or no implementation has been done
          yet, or the repository is only intended to be a limited example,
          demo, or proof-of-concept.

.. |ci-status| image:: https://github.com/jwodder/pdfcalendar/actions/workflows/test.yml/badge.svg
    :target: https://github.com/jwodder/pdfcalendar/actions/workflows/test.yml
    :alt: CI Status

.. |license| image:: https://img.shields.io/github/license/jwodder/pdfcalendar.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/pdfcalendar>`_
| `Issues <https://github.com/jwodder/pdfcalendar/issues>`_

``pdfcalendar`` is a Python program for producing a PDF document containing
calendars for multiple years.  Currently, the output always consists of a page
containing five annual calendars, each laid out in a column, starting with the
current year.

See |example.pdf|_ for example output.

.. |example.pdf| replace:: ``example.pdf``
.. _example.pdf: example.pdf

Installation
============
``pdfcalendar`` requires Python 3.12 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install git+https://github.com/jwodder/pdfcalendar.git


Usage
=====

::

    pdfcalendar [<options>] <outfile>

Produce a PDF document at ``<outfile>`` containing calendars for multiple
years.  The month names and weekday abbreviations used are determined based on
the current locale settings.

Options
-------

--font-name FONT            Set the name of the font to use for the text
                            [default: Times-Roman]

--font-size INT             Set the size of the font to use for the text
                            [default: 10]
