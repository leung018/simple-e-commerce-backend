from app.repositories.postgres.helper import select_query_helper


def test_should_select_query_helper_add_for_share_when_specify_it():
    query = "SELECT * FROM table WHERE id = 2"
    assert (
        select_query_helper(query, for_share=True)
        == "SELECT * FROM table WHERE id = 2 FOR SHARE;"
    )


def test_should_select_query_helper_not_add_for_share_without_specify_it():
    query = "SELECT * FROM table WHERE id = 2"
    assert select_query_helper(query) == "SELECT * FROM table WHERE id = 2;"


def test_should_select_query_helper_add_for_share_and_move_semi_colon_to_the_end():
    query = "SELECT * FROM table WHERE id = 2;"
    assert (
        select_query_helper(query, for_share=True)
        == "SELECT * FROM table WHERE id = 2 FOR SHARE;"
    )
