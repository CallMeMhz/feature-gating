"""条件表达式计算引擎"""
from typing import List, Dict, Any
from app.services.hash import get_hashed_value


def evaluate_condition(condition: Dict[str, Any], context: Dict[str, str]) -> bool:
    """
    计算单个条件是否满足
    
    条件结构：
    {
        "field": "user_id",
        "operator": "%",
        "value": 10,
        "comparator": ">",
        "target": 1
    }
    
    计算逻辑：hash(field) operator value comparator target
    例如：hash(user_id) % 10 > 1
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
    
    # 对字段进行哈希
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

