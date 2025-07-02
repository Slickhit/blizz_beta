import modules.memory_db as memory_db


def test_add_and_search(tmp_path):
    db_file = tmp_path / "mem.db"
    memory_db.init_db(str(db_file))
    memory_db.add_entry("u1", "t1", "raw1", "sum1", [1.0, 0.0], [])
    memory_db.add_entry("u1", "t2", "raw2", "sum2", [0.0, 1.0], [])
    results = memory_db.search([1.0, 0.0], k=1)
    assert results and results[0]["summary"] == "sum1"
