#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# @Time    : 2021/10/20 12:40
# @Author  : Kai Zhang
# @File    : table.py
# @Software: PyCharm
# =============================================================================

from typing import (
    Mapping,
    Dict,
    Callable
)

from .utils import LRUCache
from .storages import Storage


class Document(dict):
    def __init__(self, value: Mapping, doc_id: int):
        super().__init__(value)
        self.doc_id = doc_id


class Table(object):
    document_class = Document
    document_id_class = int
    query_cache_class = LRUCache
    default_query_cache_capacity = 10

    def __init__(
            self,
            storage: Storage,
            name: str,
            cache_size: int = default_query_cache_capacity
    ):
        """
        Create a table instance.
        """
        self._storage = storage
        self._name = name
        # self._query_cache

        self._next_id = None

    def __repr__(self):
        args = [
            'name={}'.format(self.name),
            'total={}'.format(len(self)),
            'storage={}'.format(self._storage)
        ]

        return '<{} {}>'.format(type(self).__name__, ','.join(args))

    # @property装饰器作用于的函数相当于get函数，可以读取私有属性
    @property
    def name(self) -> str:
        return self._name

    @property
    def storage(self) -> Storage:
        return self._storage

    def insert(self, document: Mapping) -> int:
        # 插入时再次校验数据格式
        if not isinstance(document, Mapping):
            raise ValueError('Document is not a Mapping')

        # Document = Mapping + doc_id
        if isinstance(document, Document):
            doc_id = document.doc_id
            self._next_id = None
        else:
            doc_id = self._get_next_id()

        def updater(table: dict):
            assert doc_id not in table, 'doc_id ' + str(doc_id) + ' already exists'
            table[doc_id] = dict(document)

        self._update_table(updater)

        return doc_id

    def _get_next_id(self):
        # 已知 next_id
        if self._next_id is not None:
            next_id = self._next_id
            self._next_id = self._next_id + 1
            return next_id

        table = self._read_table()
        if not table:
            next_id = 1
            self._next_id = next_id + 1
            return next_id

        max_id = max(self.document_id_class(i) for i in table.keys())
        next_id = max_id + 1
        self._next_id = next_id + 1
        return next_id

    def _read_table(self) -> Dict[int, Mapping]:
        tables = self._storage.read()

        # 空库
        if tables is None:
            return {}

        try:
            table = tables[self.name]
        except KeyError:
            # 表不存在
            return {}

        return {
            self.document_id_class(doc_id): doc
            for doc_id, doc in table.items()
        }

    def _update_table(self, updater: Callable[[Dict[int, Mapping]], None]):
        """
        流程：读取所有表、更新指定表、写入全部表
        :param updater:
        :return:
        """
        tables = self._storage.read()

        # 空库
        if tables is None:
            tables = {}

        # 获取指定表
        try:
            raw_table = tables[self.name]
        except KeyError:
            raw_table = {}

        table = {
            self.document_id_class(doc_id): doc
            for doc_id, doc in raw_table.items()
        }

        updater(table)

        tables[self.name] = {
            str(doc_id): doc
            for doc_id, doc in table.items()
        }

        # 写入全部表
        self._storage.write(tables)

        # 清除缓存
