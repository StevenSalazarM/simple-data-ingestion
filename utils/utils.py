import datetime
from configs.config import mask_encoder, private_fiels

def get_age_group(birth_date_str):
    """Calculates the age group from a birth date string in the format 'YYYY-MM-DD'.

    Args:
        birth_date_str: The birth date string.

    Returns:
        The age group as a string in the format '[age_range]'.
    """

    birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    age_group = f"[{age // 10 * 10}-{age // 10 * 10 + 10}]"
    return age_group

def mask_fields(element):
    new_element = {}
    for k in element:
        if k in private_fiels:
            new_element[k] = mask_encoder
        else:
            new_element[k] = element[k]
    return new_element