#!/bin/bash

python3 manage.py collectstatic --clear --noinput
python3 manage.py compress
