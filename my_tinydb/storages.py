#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# @Time    : 2021/10/20 12:47
# @Author  : Kai Zhang
# @File    : storages.py
# @Software: PyCharm
# =============================================================================

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class Storage(ABC):
    """
    所有 Storages 的抽象类
    """
    @abstractmethod
    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        raise NotImplementedError('To be overridden')

    @abstractmethod
    def write(self, data: Dict[str, Dict[str, Any]]):
        raise NotImplementedError('To be overridden')

    def close(self) -> None:
        pass
