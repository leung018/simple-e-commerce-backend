from app.repositories.base import LockLevel
from app.repositories.postgres.helper import select_query_helper


def test_should_select_query_helper_add_for_update_when_lock_level_modify_lock():
    query = "SELECT * FROM table WHERE id = 2"
    assert (
        select_query_helper(query, lock_level=LockLevel.MODIFY_LOCK)
        == "SELECT * FROM table WHERE id = 2 FOR UPDATE;"
    )


def test_should_select_query_helper_add_nothing_when_lock_level_none():
    query = "SELECT * FROM table WHERE id = 2"
    assert (
        select_query_helper(query, lock_level=LockLevel.NONE)
        == "SELECT * FROM table WHERE id = 2;"
    )


def test_should_select_query_helper_move_semi_colon_to_the_end_even_if_need_to_append_sth_to_query():
    query = "SELECT * FROM table WHERE id = 2;"
    assert (
        select_query_helper(query, lock_level=LockLevel.MODIFY_LOCK)
        == "SELECT * FROM table WHERE id = 2 FOR UPDATE;"
    )
