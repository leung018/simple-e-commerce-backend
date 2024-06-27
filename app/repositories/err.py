from app.err import MyValueError


class EntityNotFoundError(MyValueError):
    @staticmethod
    def create(field_name: str, field_value: str):
        return EntityNotFoundError(f"{field_name}: {field_value} does not exists")
