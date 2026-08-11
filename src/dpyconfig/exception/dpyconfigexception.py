class DPyConfigException(Exception):
    """DPyConfigの基本例外クラス
    """

    def __init__(self, message: str, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
            org_exception (Exception, optional): 元例外情報. Defaults to None.
        """
        super().__init__(message)
        self.org_exception = org_exception


class DPyConfigUnsupportedException(DPyConfigException):
    """設定ファイル不未サポート例外クラス
    """

    def __init__(self, message):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
        """
        super().__init__(message)


class DPyConfigFileNotFoundException(DPyConfigException):
    """設定ファイル不存在例外クラス
    """

    def __init__(self, message):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
        """
        super().__init__(message)


class DPyYamlConfigFileLoadFaileException(DPyConfigException):
    """YAML設定ファイル読み込み失敗例外クラス
    """

    def __init__(self, message, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
        """
        super().__init__(message, org_exception)


class DPyIniConfigFileLoadFaileException(DPyConfigException):
    """INI設定ファイル読み込み失敗例外クラス
    """

    def __init__(self, message, org_exception: Exception = None):
        """コンストラクタ
        Args:
            message (str): 例外メッセージ
        """
        super().__init__(message, org_exception)
