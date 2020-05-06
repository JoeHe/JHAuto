import inspect
from pymongo import MongoClient, ASCENDING, UpdateOne
from pymongo.results import UpdateResult

from utils import utils
from config import config


resource = utils.load_yml("resources.yaml")
MONGO_URL = resource['MongoDB']['MONGO_URL']
MONGO_DB_NAME = resource['MongoDB']['MONGO_DB_NAME'][config.COUNTRY]

client = MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB_NAME]
coll_users = db.users
coll_loans = db.loans


class MongoDAL:

    def __init__(self):
        pass

    @staticmethod
    def create_index():
        if not MongoDAL.created_index_called:
            coll_loans.create_index([('id_account', ASCENDING)])
            MongoDAL.created_index_called = True

    @staticmethod
    def pretty_print_result(result):
        func_name = inspect.stack()[1][3]
        if isinstance(result, UpdateResult):
            print("{} UpdateResult(acknowledged: {}, matched_count: {}, modified_count: {}, upserted_id: {})".format(
                func_name, result.acknowledged, result.matched_count, result.modified_count, result.upserted_id))

    @staticmethod
    def get_user(id_account):
        return coll_users.find_one({'id_account': id_account})

    @staticmethod
    def upsert_user(id_account, user_dict):
        user_dict['id_account'] = id_account
        user_dict['updated_at'] = utils.get_time_stamp('%Y-%m-%d %H:%M:%S')
        res = coll_users.replace_one({'id_account': id_account}, user_dict, upsert=True)
        MongoDAL.pretty_print_result(res)

    @staticmethod
    def get_loans(id_account):
        return coll_loans.find_one({'id_account': id_account})

    @staticmethod
    def upsert_user_loans(loans_dict_list):
        operations = []
        for loans_dict in loans_dict_list:
            loans_dict['updated_at'] = utils.get_time_stamp('%Y-%m-%d %H:%M:%S')
            if not coll_loans.find({'id_account': loans_dict['id_account']}).count():
                loans_dict['created_at'] = utils.get_time_stamp('%Y-%m-%d %H:%M:%S')
                operation = UpdateOne({'id_account': loans_dict['id_account']}, {"$set": loans_dict}, upsert=True)
            else:
                operation = UpdateOne({'id_account': loans_dict['id_account']}, {"$set": loans_dict}, upsert=False)
            operations.append(operation)
        if operations:
            coll_loans.bulk_write(operations)

    @staticmethod
    def delete_user(id_account, just_one=False):
        return coll_users.remove({'id_account': id_account}, {'justOne': just_one})


