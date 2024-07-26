from app.repositories.postgres.helper import select_query_helper


def test_should_select_query_helper_add_for_share_when_for_share_true():
    query = "SELECT * FROM table WHERE id = 2"
    assert (
        select_query_helper(query, for_update=True)
        == "SELECT * FROM table WHERE id = 2 FOR UPDATE;"
    )


def test_should_select_query_helper_not_add_for_share_when_for_share_false():
    query = "SELECT * FROM table WHERE id = 2"
    assert (
        select_query_helper(query, for_update=False)
        == "SELECT * FROM table WHERE id = 2;"
    )


def test_should_select_query_helper_add_for_share_and_move_semi_colon_to_the_end():
    query = "SELECT * FROM table WHERE id = 2;"
    assert (
        select_query_helper(query, for_update=True)
        == "SELECT * FROM table WHERE id = 2 FOR UPDATE;"
    )
