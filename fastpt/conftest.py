#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from _pytest.logging import LogCaptureFixture
from filelock import FileLock
from loguru import logger
from py._xmlgen import html

from fastpt.common.log import log
from fastpt.core.get_conf import TESTER_NAME, PROJECT_NAME


@pytest.fixture(scope='session', autouse=True)
def session_fixture() -> None:
    # 避免分布式执行用例循环执行此fixture
    with FileLock("session.lock"):
        ...
    yield
    ...


@pytest.fixture(scope='package', autouse=True)
def package_fixture() -> None:
    ...
    yield
    log.info('测试用例执行结束')


@pytest.fixture(scope='module', autouse=True)
def module_fixture() -> None:
    ...
    yield
    ...


@pytest.fixture(scope='class', autouse=True)
def class_fixture() -> None:
    ...
    yield
    ...


@pytest.fixture(scope='function', autouse=True)
def function_fixture(request) -> None:
    log.info(f'----------------- Running case: {request.function.__name__} -----------------')

    def log_end():
        log.info('end \n')

    request.addfinalizer(log_end)  # teardown终结函数 == yield后的代码


@pytest.fixture(autouse=True)
def caplog(caplog: LogCaptureFixture):
    """
    将 pytest 的 caplog 夹具默认日志记录器改为 loguru,而非默认 logging
    :param caplog:
    :return:
    """
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells) -> None:
    # 向html报告中的table添加额外信息
    cells.insert(1, html.th('Case description', class_="sortable", col="name"))


def pytest_html_results_summary(prefix, summary, postfix) -> None:
    # 向html报告中的summary添加额外信息
    prefix.extend([html.p(f"test project: {PROJECT_NAME}")])
    prefix.extend([html.p(f"tester: {TESTER_NAME}")])


def pytest_collection_modifyitems(items) -> None:
    # item表示每个用例, 避免在使用数据驱动ids参数为中文时,控制台输出乱码
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")