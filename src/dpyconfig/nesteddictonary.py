
class NestedDictionary(dict):

    def __init__(self, args_dict: dict = {}, parent: "NestedDictionary" = None):
        """ コンストラクタ

        このクラスは、ネストされた辞書構造を扱うための辞書クラスです。

        Args:
            args_dict (dict, optional): 初期化用辞書. Defaults to {}.
            parent (NestedDictionary, optional): 親辞書. Defaults to None.
        """
        # 親辞書を設定する
        self.parent = parent
        # 子辞書リストを初期化する
        self.children = []
        # 要素にディクショナリが含まれていた場合、NestedDictionaryに変換して格納する
        for key, value in args_dict.items():
            if isinstance(value, dict):
                value = NestedDictionary(args_dict=value, parent=self)
                self.children.append(value)
            super().__setitem__(key, value)

    def is_root(self) -> bool:
        """ ルート辞書かどうかを判定する

        Returns:
            bool: ルート辞書の場合True、そうでない場合False
        """
        return self.parent is None

    def search(self, key: str) -> list:
        """ 指定されたキーを持つ要素を再帰的に検索する

        Args:
            key (str): 検索するキー

        Returns:
            list: 検索結果のリスト
        """
        result = []
        self.__recurcive_search_by_key(key, result)
        return result

    def __recurcive_search_by_key(self, key: str, result: list) -> None:
        """ 指定されたキーを持つ要素を再帰的に検索する

        Args:
            key (str): 検索するキー
            result (list): 検索結果を格納するリスト
        """
        if key in self:
            result.append(self[key])
        for child in self.children:
            child.__recurcive_search_by_key(key, result)

    def __getitem__(self, key):
        # オブジェクト[key]のとき実行される
        # 通常通りの動作を行う
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        # オブジェクト[key]=valueのとき実行される
        # 変更不可とする
        raise NotImplementedError("NestedDictionary is read-only.")

    def __delattr__(self, name):
        # del オブジェクト[key]のとき実行される
        # 変更不可とする
        raise NotImplementedError("NestedDictionary is read-only.")

    def __iter__(self):
        # for key in オブジェクトのとき実行される
        # 通常通りの動作を行う
        return super().__iter__()

    def ___contains__(self, key):
        # key in オブジェクトのとき実行される
        # 通常通りの動作を行う
        return super().__contains__(key)

    def __reversed__(self):
        # reversed(オブジェクト)のとき実行される
        # 通常通りの動作を行う
        return super().__reversed__()

    def __len__(self):
        # len(オブジェクト)のとき実行される
        # 通常通りの動作を行う
        return super().__len__()

    def __str__(self):
        # str(オブジェクト)のとき実行される
        # 通常通りの動作を行う
        return super().__str__()
