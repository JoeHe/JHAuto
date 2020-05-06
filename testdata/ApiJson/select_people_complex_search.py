from utils import utils


class SearchLabelGroupReq:
    def __init__(self, logical_condition_list):
        self.searchLabelGroupReqList = logical_condition_list

    def __repr__(self):
        return repr(self.searchLabelGroupReqList)


class LogicalCondition:
    def __init__(self, logical_condition, search_label_req_list):
        self.logicalCondition = logical_condition
        self.searchLabelReqList = search_label_req_list


class SearchLabelReq:
    def __init__(self, labelId, labelWhereValue, logicalCondition, groupId, searchLabelParamsReqList):
        self.labelId = labelId
        self.labelWhereValue = labelWhereValue
        self.logicalCondition = logicalCondition
        self.groupId = groupId
        self.searchLabelParamsReqList = searchLabelParamsReqList


class SearchLabelParamsReq:
    def __init__(self, paramsId, paramsValue, paramsOperator):
        self.paramsId = paramsId
        self.paramsValue = paramsValue
        self.paramsOperator = paramsOperator


def get_logical_condition(label_data_list):
    if not isinstance(label_data_list, list):
        raise Exception("please pass a list type parameter!")
    label_list = []
    for dt in label_data_list:
        label_list.append(get_search_label(dt))
    logical_condition = LogicalCondition('and', label_list)
    return logical_condition


def get_search_label(label_data):
    params_list = []
    for param in label_data['paramsList']:
        param_config = SearchLabelParamsReq(param['paramsId'], param['paramsValue'], param['paramsOperator'])
        params_list.append(param_config)
    search_label = SearchLabelReq(label_data['labelId'], label_data['labelWhereValue'], label_data['logicalCondition'],
                                  label_data['groupId'], params_list)
    return search_label


def get_select_people_complex_payload(crm_complex_data, grp1_label_list, grp2_label_list):
    """
    generate two group search people complex json.
    :param crm_complex_data:
    :param grp1_label_list: group 1 labels list, the groupId for labels in list should be same in yml.
    :param grp2_label_list: group 2 labels list, eg: ['latestRiskScore', 'installDate']
    :return: payload json
    """
    if not isinstance(crm_complex_data, dict) or len(crm_complex_data) <= 0:
        utils.warn('please pass a valid dict parameter')
        return None
    group1_label_data_list, group2_label_data_list = [], []
    for label in grp1_label_list: group1_label_data_list.append(crm_complex_data[label])
    for label in grp2_label_list: group2_label_data_list.append(crm_complex_data[label])
    search_complex_payload = SearchLabelGroupReq([get_logical_condition(group1_label_data_list), get_logical_condition(group2_label_data_list)])
    json_str = utils.dump_obj(search_complex_payload)
    payload_json = utils.load_json(json_str)
    return payload_json

