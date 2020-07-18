#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import db


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
