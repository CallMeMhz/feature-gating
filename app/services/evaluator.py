"""条件表达式计算引擎"""
from typing import List, Dict, Any, Union
from app.services.hash import get_hashed_value


def _parse_list_value(value: Union[str, list]) -> List[str]:
    """
    解析列表值，支持：
    - 数组：["1", "2", "3"]
    - 逗号分割："1,2,3" 或 "1, 2, 3"
    - 换行符分割："1\n2\n3"
    """
    if isinstance(value, list):
        return [str(v).strip() for v in value]
    
    if isinstance(value, str):
        # 先尝试换行符分割
        if '\n' in value:
            return [v.strip() for v in value.split('\n') if v.strip()]
        # 否则使用逗号分割
        return [v.strip() for v in value.split(',') if v.strip()]
    
    return []


def evaluate_condition(condition: Dict[str, Any], context: Dict[str, str]) -> bool:
    """
    计算单个条件是否满足
    
    条件结构示例：
    
    1. 哈希运算（灰度发布）：
    {
        "field": "user_id",
        "operator": "%",
        "value": 10,
        "comparator": ">",
        "target": 1
    }
    计算逻辑：hash(user_id) % 10 > 1
    
    2. 直接相等判断（白名单）：
    {
        "field": "user_id",
        "operator": "==",
        "value": "uid_8555"
    }
    
    3. 白名单判断（in/not in）：
    {
        "field": "user_id",
        "operator": "in",
        "value": ["1", "2", "3"]  // 或 "1,2,3" 或 "1\n2\n3\n4"
    }
    """
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")
    comparator = condition.get("comparator")
    target = condition.get("target")
    
    # 获取字段值
    field_value = context.get(field)
    if field_value is None:
        return False
    
    # 白名单操作符：直接比较字段值，不进行哈希
    if operator == "==":
        # 直接相等判断，支持字符串
        return str(field_value) == str(value)
    
    elif operator == "!=":
        # 直接不等判断
        return str(field_value) != str(value)
    
    elif operator == "in":
        # 白名单判断
        whitelist = _parse_list_value(value)
        return str(field_value) in whitelist
    
    elif operator == "not in":
        # 黑名单判断
        blacklist = _parse_list_value(value)
        return str(field_value) not in blacklist
    
    # 哈希运算操作符：对字段进行哈希后计算
    hashed = get_hashed_value(field, field_value)
    
    # 应用运算符
    if operator == "%":
        result = hashed % value
    elif operator == "/":
        result = hashed / value if value != 0 else 0
    elif operator == "//":
        result = hashed // value if value != 0 else 0
    elif operator == "*":
        result = hashed * value
    else:
        # 未知运算符，直接使用哈希值
        result = hashed
    
    # 应用比较符
    if comparator == ">":
        return result > target
    elif comparator == "<":
        return result < target
    elif comparator == ">=":
        return result >= target
    elif comparator == "<=":
        return result <= target
    elif comparator == "==":
        return result == target
    elif comparator == "!=":
        return result != target
    else:
        return False


def evaluate_conditions(conditions: List[Dict[str, Any]], context: Dict[str, str]) -> bool:
    """
    计算所有条件（AND 逻辑）
    所有条件都满足才返回 True
    """
    if not conditions:
        return True
    
    for condition in conditions:
        if not evaluate_condition(condition, context):
            return False
    
    return True

