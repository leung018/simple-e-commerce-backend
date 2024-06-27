from app.err import MyValueError


class EntityNotFoundError(MyValueError):
    @staticmethod
    def format_err_msg(field_name: str, field_value: str):
        return f"{field_name}: {field_value} does not exists"

    @classmethod
    def create(cls, field_name: str, field_value: str):
        return EntityNotFoundError(cls.format_err_msg(field_name, field_value))
