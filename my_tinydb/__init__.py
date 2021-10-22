#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# @Time    : 2021/10/20 12:34
# @Author  : Kai Zhang
# @File    : __init__.py
# @Software: PyCharm
# =============================================================================

from .database import TinyDB
from .table import Table

__all__ = ('TinyDB', 'Table')
