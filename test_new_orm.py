
from dataclasses import dataclass
from re import U
import shutil
import os
from typing import get_type_hints, TypeVar, Type
import super_py as sp
import dictdatabase as DDB

T = TypeVar("T")
T2 = TypeVar("T2")

# TODO: How to handle .id, autocreate id possibility?

####
####
####
####
################################################################################
#### Utils
################################################################################


class sp_test_must_except():
    def __init__(self, exception_type: Type[Exception]):
        self.exception_type = exception_type

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            raise Exception(f"Expected an exception of type {self.exception_type}")
        if not issubclass(exc_type, self.exception_type):
            raise Exception(f"Expected an exception of type {self.exception_type}, got {exc_type}")
        # Return True to surpress the exception
        return True




def setup():
    DDB.config.storage_directory = ".ddb_storage_testing"
    DDB.config.pretty_json_files = True
    DDB.config.use_compression = False
    shutil.rmtree(".ddb_storage_testing", ignore_errors=True)
    os.makedirs(DDB.config.storage_directory, exist_ok=True)


def teardown():
    shutil.rmtree(".ddb_storage_testing")


####
####
####
####
################################################################################
#### Mixin
################################################################################

@dataclass
class NestedObjectMixin(object):
    def __init__(self, json):
        print("🟣NestedObjectMixin.__init__")

        for hint_name, hint_type in get_type_hints(self).items():

            # Check if all attributes are in the json
            if hint_name not in json:
                raise AttributeError(
                    f"Init {type(self).__name__}: "
                    f"{hint_name} is missing from json {type(self).__name__}"
                )

            input_value = json[hint_name]

            # Check if hint_type inherits from NestedObjectMixin
            if issubclass(hint_type, NestedObjectMixin):
                print(f"🟣 {hint_name} is a NestedObjectMixin")
                setattr(self, hint_name, hint_type(input_value))
                continue

            # Check if provided value has the same type as the hint_type
            if not isinstance(input_value, hint_type):
                raise TypeError(
                    f"{hint_name} is of type {type(input_value)}, "
                    f"but should be {hint_type}"
                )

            # If everything is ok, set the attribute
            setattr(self, hint_name, input_value)


    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__dict__})"

    def dict(self) -> dict:
        res = {}
        for attr_name in get_type_hints(self).keys():
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, NestedObjectMixin):
                res[attr_name] = attr_value.dict()
            else:
                res[attr_name] = attr_value
        return res



@dataclass
class ObjectMixin(NestedObjectMixin):
    def __init__(self, json=None, **kwargs):
        print("🔵 ObjectMixin.__init__")
        if json is None:
            json = {k: v for k, v in kwargs.items()}
        super().__init__(json)


    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__dict__})"



    @classmethod
    def read_one_by_id(cls: Type[T], id) -> T | None:
        json = DDB.read(f"{cls.__name__}/{id}")
        if json is None:
            return None
        return cls(json)

    @classmethod
    def write_one_by_id(cls: Type[T], obj: T):
        DDB.create(f"{cls.__name__}/{obj.id}", overwrite=True, db=obj.dict())


    @classmethod
    def read_as_list(cls: Type[T], filter=None) -> list[T]:
        print("🔵 ObjectMixin.read_as_list")
        json = DDB.multiread(f"{cls.__name__}/*")
        list = [cls(u) for u in json.values()]
        if filter is not None:
            list = [x for x in list if filter(x)]
        return list


    @classmethod
    def write_from_list(cls: Type[T], input_list: list[T]):
        print("🔵 ObjectMixin.write_from_list")
        for item in input_list:
            DDB.create(f"{cls.__name__}/{item.id}", overwrite=True, db=item.dict())



    @classmethod
    def read_as_dict(cls: Type[T], by_key: Type[T2]) -> dict[T2, T]:
        print("🔵 ObjectMixin.read_as_dict")
        json = DDB.multiread(f"{cls.__name__}/*")
        res = {}
        for value in json.values():
            res[value[by_key]] = cls(value)
        return res

    @classmethod
    def write_from_dict(cls: Type[T], input_dict: dict[T2, T]):
        print("🔵 ObjectMixin.write_from_dict")
        for value in input_dict.values():
            DDB.create(f"{cls.__name__}/{value.id}", overwrite=True, db=value.dict())




    @classmethod
    def clean_db_from_removed_attrs(cls):
        """
        TODO
        """
        raise NotImplementedError


####
####
####
####
################################################################################
#### Expense
################################################################################


class Expense(ObjectMixin):
    id: int
    user_id: int
    title: str
    amount: int

####
####
####
####
################################################################################
#### User
################################################################################


class UserPreferences(NestedObjectMixin):
    dark_mode: bool
    favorite_colors: list
    # other: list[str]  # TODO
    # sime: dict[str, int]  # TODO



class User(ObjectMixin):
    id: int
    first_name: str
    last_name: str
    age: int
    preferences: UserPreferences

    @property
    def expenses(self) -> list[Expense]:
        print("User.expenses")
        return Expense.read_as_list(
            filter=lambda expense: expense.user_id == self.id
        )

    def full_name(self):
        return f"{self.first_name} {self.last_name}"



DDB.create("User", "1", overwrite=True, db={
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "email": "doe@gmail.com",
    "preferences": {
        "dark_mode": True,
        "favorite_colors": ["green", "blue"],
    }
})




DDB.create("User", "2", overwrite=True, db={
    "id": 2,
    "first_name": "Jane",
    "last_name": "Doe",
    "age": 20,
    "preferences": {
        "dark_mode": True,
        "favorite_colors": ["red", "blue"]
    }
})


DDB.create("Expense", "1", overwrite=True, db={
    "id": 1,
    "user_id": 2,
    "title": "Rent",
    "amount": 1000,
})

DDB.create("Expense", "1", overwrite=True, db={
    "id": 2,
    "user_id": 2,
    "title": "Car",
    "amount": 234,
})



print("🚀🚀🚀🚀 Start script")
users_list = User.read_as_list()
# users_list.append(User({
#     "id": 3,
#     "first_name": "John",
#     "last_name": "Doe",
#     "age": 30,
#     "preferences": {"dark_mode": True, "favorite_colors": ["green", "blue"]}})
# )

users_list[0].age = 999
print(f"{users_list=}")


User.write_from_list(users_list)



users_dict = User.read_as_dict(by_key="id")
print(f"{users_dict=}")

assert users_dict[1].full_name() == "John Doe"




####
####
####
####
################################################################################
#### Tests
################################################################################

@sp.test(setup, teardown)
def test_ObjectMixin_init_by_kwargs():
    class User(ObjectMixin):
        id: int
        hobbies: list

    u1 = User(id=1, hobbies=["swim", 3])
    assert u1.id == 1
    assert u1.hobbies == ["swim", 3]

    # Missing attribute should raise AttributeError
    with sp_test_must_except(AttributeError):
        User(id=1)

    # Wrong type should raise TypeError
    with sp_test_must_except(TypeError):
        User(id="1", hobbies=["swim", 3])
    with sp_test_must_except(TypeError):
        User(id=1, hobbies="swim")


@sp.test(setup, teardown)
def test_ObjectMixin_init_by_dict():
    class User(ObjectMixin):
        id: int
        hobbies: list

    # Normal init should work
    u1 = User({"id": 1, "hobbies": ["swim", 3]})
    assert u1.id == 1
    assert u1.hobbies == ["swim", 3]

    # Missing attribute should raise AttributeError
    with sp_test_must_except(AttributeError):
        User({"id": 1})

    # Wrong type should raise TypeError
    with sp_test_must_except(TypeError):
        User({"id": "1", "hobbies": ["swim", 3]})
    with sp_test_must_except(TypeError):
        User({"id": 1, "hobbies": "swim"})


@sp.test(setup, teardown)
def test_ObjectMixin_read_write():
    class User(ObjectMixin):
        id: int
        name: str

    DDB.create("User", "1", overwrite=True, db={"id": 1, "name": "John"})

    # If user does not exist, read should return None
    assert User.read_one_by_id(2) is None

    # Read an existing user
    u1 = User.read_one_by_id(1)
    assert u1.id == 1
    assert u1.name == "John"

    # Change attribute and write
    u1.name = "Ben"
    User.write_one_by_id(u1)

    # Read again and check attribute
    u1_reread = User.read_one_by_id(1)
    assert u1_reread.name == "Ben"
