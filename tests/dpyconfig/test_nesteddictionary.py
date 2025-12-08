from nesteddictonary import NestedDictionary


def test_constractor_empty():
    """ コンストラクタのテスト（空辞書）

    """
    nd = NestedDictionary({})
    # コンストラクタの結果に対しての検証
    assert isinstance(nd, NestedDictionary)
    assert len(nd) == 0
    # is_rootメソッドの検証
    assert nd.is_root()
    # searchメソッドの検証
    assert nd.search("anykey") == []
    # __str__メソッドの検証
    assert str(nd) == "{}"


def test_constractor_flat_dict():
    """ コンストラクタのテスト（フラット辞書）

    """
    data = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
    nd = NestedDictionary(data)
    # コンストラクタの結果に対しての検証
    assert isinstance(nd, NestedDictionary)
    assert len(nd) == 3
    assert nd["key1"] == "value1"
    assert nd["key2"] == "value2"
    assert nd["key3"] == "value3"
    # is_rootメソッドの検証
    assert nd.is_root()
    # searchメソッドの検証
    assert nd.search("key1") == ["value1"]
    # __str__メソッドの検証
    assert str(nd) == str(data)


def test_constractor_nested_dict():
    """ コンストラクタのテスト（ネスト辞書）

    """
    data = {
        "key1": "value1",
        "key2": {
            "subkey1": "subvalue1",
            "subkey2": "subvalue2"
        },
        "key3": "value3"
    }
    # コンストラクタの結果に対しての検証
    nd = NestedDictionary(data)
    assert isinstance(nd, NestedDictionary)
    assert len(nd) == 3
    assert nd["key1"] == "value1"
    assert isinstance(nd["key2"], NestedDictionary)
    assert len(nd["key2"]) == 2
    assert nd["key2"]["subkey1"] == "subvalue1"
    assert nd["key2"]["subkey2"] == "subvalue2"
    assert nd["key3"] == "value3"
    # is_rootメソッドの検証
    assert nd.is_root()
    assert nd["key2"].parent == nd
    # searchメソッドの検証
    assert nd.search("key1") == ["value1"]
    assert nd.search("key2") == [data["key2"]]
    assert nd.search("subkey1") == ["subvalue1"]
    # __str__メソッドの検証
    assert str(nd) == str(data)


def test_constractor_deeply_nested_dict():
    """ コンストラクタのテスト（深くネストされた辞書）

    """
    data = {
        "level1": {
            "level2": {
                "level3": {
                    "key": "deepvalue"
                }
            }
        }
    }
    # コンストラクタの結果に対しての検証
    nd = NestedDictionary(data)
    assert isinstance(nd, NestedDictionary)
    assert len(nd) == 1
    assert isinstance(nd["level1"], NestedDictionary)
    assert isinstance(nd["level1"]["level2"], NestedDictionary)
    assert isinstance(nd["level1"]["level2"]["level3"], NestedDictionary)
    assert nd["level1"]["level2"]["level3"]["key"] == "deepvalue"
    # is_rootメソッドの検証
    assert nd.is_root()
    assert nd["level1"].parent == nd
    assert nd["level1"]["level2"].parent == nd["level1"]
    assert nd["level1"]["level2"]["level3"].parent == nd["level1"]["level2"]
    # searchメソッドの検証
    assert nd.search("key") == ["deepvalue"]
    # __str__メソッドの検証
    assert str(nd) == str(data)


def test_constractor_deeply_nested_dict():
    """ コンストラクタのテスト（深くネストされた辞書）

    """
    data = {
        "key1": "value1",
        "key2": {
            "subkey1": "subvalue1",
            "subkey2": {
                "subsubkey1": "subsubvalue1"
            }
        },
        "key3": {
            "subkey1": "subvalue1",
            "subkey2": {
                "subsubkey1": "subsubvalue1"
            }
        },
    }
    # コンストラクタの結果に対しての検証
    nd = NestedDictionary(data)
    assert isinstance(nd, NestedDictionary)
    assert len(nd) == 3
    assert nd["key1"] == "value1"
    assert isinstance(nd["key2"], NestedDictionary)
    assert isinstance(nd["key2"]["subkey2"], NestedDictionary)
    assert isinstance(nd["key3"], NestedDictionary)
    assert isinstance(nd["key3"]["subkey2"], NestedDictionary)
    assert nd["key2"]["subkey2"]["subsubkey1"] == "subsubvalue1"
    assert nd["key3"]["subkey2"]["subsubkey1"] == "subsubvalue1"
    # is_rootメソッドの検証
    assert nd.is_root()
    assert nd["key2"].parent == nd
    assert nd["key2"]["subkey2"].parent == nd["key2"]
    assert nd["key3"].parent == nd
    assert nd["key3"]["subkey2"].parent == nd["key3"]
    # searchメソッドの検証
    assert nd.search("subsubkey1") == ["subsubvalue1", "subsubvalue1"]
    assert nd.search("subkey2") == [{"subsubkey1": "subsubvalue1"}, {
        "subsubkey1": "subsubvalue1"}]
    # __str__メソッドの検証
    assert str(nd) == str(data)
