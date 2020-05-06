import os
import yaml
import random
import time
import json
from datetime import datetime,timedelta

from logger import bi_logger
from config import config, constants
from utils import mysqlhelper


def log(info):
    """
    print log info both in report and log file
    :param info: log info
    """
    print(info)
    bi_logger.info(info)


def warn(info):
    """
    print log info both in report and log file
    :param info: log info
    """
    print(info)
    bi_logger.warning(info)


def debug(info):
    """
    print debug info in log file
    :param info: debug info
    """
    bi_logger.debug(info)


def error(info):
    print(info)
    bi_logger.error(info, exc_info=True)


def load_yml(file_path):
    """
    load yml file data. support file under ./testdata, just pass filename. if not, pass full path
    """
    result = None
    if config.BASE_PATH not in file_path:
        file_path = os.path.join(config.TEST_DATA_DIR, file_path)
    with open(file_path, 'r') as stream:
        try:
            result = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error(exc)
    return result


def get_random_numb(start=1, end=8888):
    return random.randint(start, end)


def get_time_stamp(time_format='%Y%m%d%H%M%S'):
    return time.strftime(time_format, time.localtime(time.time()))


def get_db_connector(database):
    conn = None
    if database:
        resource = load_yml("resources.yaml")
        conn = mysqlhelper.MysqlConnector(
            resource['Mysql']['RiskDB']['host'],
            resource['Mysql']['RiskDB']['user'],
            resource['Mysql']['RiskDB']['password'],
            database)
    return conn


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    return added, modified


def dump_obj(json_obj):
    # json_str = json.dumps(json_obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    json_str = json.dumps(json_obj, default=lambda o: o.__dict__,  sort_keys=True)
    return json_str


def load_json(json_str):
    return json.loads(json_str)


def query_json(json_content, query, delimiter='.'):
    """ Do an xpath-like query with json_content.
    Args:
        json_content (dict/list/string): content to be queried.
        query (str): query string.
        delimiter (str): delimiter symbol.
    Returns:
        str: queried result.
    """
    raise_flag = False
    response_body = u"response body: {}\n".format(json_content)
    try:
        for key in query.split(delimiter):
            if isinstance(json_content, (list, str, bytes)):
                json_content = json_content[int(key)]
            elif isinstance(json_content, dict):
                json_content = json_content[key]
            else:
                error("invalid type value: {}({})".format(json_content, type(json_content)))
                raise_flag = True
    except (KeyError, ValueError, IndexError):
        raise_flag = True
    if raise_flag:
        err_msg = u"Failed to extract! => {}\n".format(query)
        err_msg += response_body
        error(err_msg)
        raise Exception(err_msg)
    return json_content


def update_none_str_2_none(json_dict):
    for k, v in json_dict.items():
        if v == 'None' or v == 'null' or v == '':
            json_dict[k] = None
    return json_dict


def get_datetime_per_timezone():
    """get now() datetime obj per timezone"""
    from dateutil import tz
    from dateutil.parser import parse

    if config.COUNTRY == constants.PHL:
        tz = tz.gettz('Asia/Manila')
    elif config.COUNTRY == constants.IDN:
        tz = tz.gettz('Asia/Jakarta')
    else:
        tz = tz.gettz('Asia/Ho_Chi_Minh')
    time_str = datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S")
    return parse(time_str)  # parse str to datetime obj


def get_time_minus(datetime_now, datetime_before):
    """获取两个datetime对象的时差绝对值，按分钟算"""
    total_seconds = (datetime_now - datetime_before).total_seconds()
    minutes = abs(int(total_seconds / 60))
    return minutes


def get_previous_date(before_day_gap, str_format='%Y-%m-%d %H:%M:%S'):
    """获取前N天的日期, before_day_gap=N：前N天"""
    today = datetime.now()
    offset = timedelta(days=-before_day_gap)
    new_date = (today + offset).strftime(str_format)
    return new_date


