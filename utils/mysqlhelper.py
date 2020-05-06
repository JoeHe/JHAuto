import pymysql
from utils import utils


class MysqlConnector:

    def __init__(self, host, user, password, db, port=3306, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor):
        utils.log("Initial mysql connection...\nHost:[{}]\nUser:[{}]\nDB:[{}]".format(host, user, db))
        self.connection = pymysql.connect(host=host,
                                          port=port,
                                          user=user,
                                          password=password,
                                          db=db,
                                          charset=charset,
                                          cursorclass=cursorclass,
                                          autocommit=True)
        self.cursor = self.connection.cursor()

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.close()
            utils.error("hit error when execute sql:\n{}".format(sql))
            raise e

    def fetchone(self, sql):
        utils.log('read a single record')
        self.execute(sql)
        result = self.cursor.fetchone()
        return result

    def fetchmany(self, sql, size):
        utils.log("read {} records".format(size))
        self.execute(sql)
        result = self.cursor.fetchmany(size)
        return result

    def fetchall(self, sql):
        utils.log('read all records')
        self.execute(sql)
        result = self.cursor.fetchall()
        return result

    def update(self, sql):
        utils.log('update record')
        self.execute(sql)
        return self.cursor.rowcount

    def close(self):
        if self.connection:
            utils.log("close mysql connection.")
            self.connection.close()
