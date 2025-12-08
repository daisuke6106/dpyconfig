from abc import ABC, abstractmethod
import os
import yaml
import configparser
from nesteddictonary import NestedDictionary
from exception.dpyconfigexception import DPyConfigFileNotFoundException, DPyYamlConfigFileLoadFaileException


class ConfigFile(ABC):
    """設定ファイルを表すクラス

    このクラスは、設定ファイルの読み込みを行うためのメソッドを提供します。

    """
    @classmethod
    def load(cls, config_file_path: str):
        """設定ファイルを読み込む
        Args:
            config_file_path (str): 設定ファイルパス
        Returns:
            ConfigFile: 設定ファイルオブジェクト
        """
        _, ext = os.path.splitext(config_file_path)
        ext = ext.lower()
        # YAMLファイルの場合
        if ext == ".yaml" or ext == ".yml":
            return YamlConfigFile(config_file_path)
        # ini, cfg, confファイルの場合
        # (未作成のためコメントアウト)
        # elif ext == ".ini" or ext == ".cfg" or ext == ".conf":
        #     return IniConfigFile(config_file_path)
        else:
            raise DPyConfigFileNotFoundException(
                f"Unsupported config file type. config_file_path={config_file_path}"
            )

    def __init__(self, config_file_path: str):
        # 設定ファイルが存在しない場合、例外をスローする
        if not os.path.exists(config_file_path):
            raise DPyConfigFileNotFoundException(
                f"Config file not Found. config_file_path={config_file_path}"
            )
        self._config_file_path = config_file_path
        # 拡張子名を取得する
        _, ext = os.path.splitext(config_file_path)
        self._ext = ext.lower()  # 小文字に変換して保存する

    def search(self, key: str) -> list:
        """ 指定されたキーを持つ要素を再帰的に検索する

        Args:
            key (str): 検索するキー

        Returns:
            list: 検索結果のリスト
        """
        return self._config.search(key)

    def _create_nested_dictionary(self, data: dict) -> NestedDictionary:
        """ネスト辞書オブジェクトを作成する

        Args:
            data (dict): 辞書データ

        Returns:
            NestedDictionary: ネスト辞書オブジェクト
        """
        return NestedDictionary(data)


class YamlConfigFile(ConfigFile):
    """YAML設定ファイルを表すクラス
    """

    class _IncludeLoader(yaml.SafeLoader):
        """YAMLのInclude機能をサポートするローダークラス
        """
        pass

    def _yaml_include(self, loader, node):
        """YAMLのInclude機能を実装するメソッド
        Args:
            loader (_IncludeLoader): ローダーオブジェクト
            node (yaml.Node): ノードオブジェクト
        Returns:
            dict: インクルードされたYAMLデータ
        """
        include_path = loader.construct_scalar(node)
        with open(include_path, 'r', encoding='utf-8') as f:
            return yaml.load(f, YamlConfigFile._IncludeLoader)

    def __init__(self, config_file_path: str):
        super().__init__(config_file_path)
        if self._ext != ".yaml" and self._ext != ".yml":
            raise DPyConfigFileNotFoundException(
                f"Not a YAML config file. config_file_path={config_file_path}"
            )
        with open(config_file_path, 'r', encoding='utf-8') as f:
            # Include機能を登録する
            YamlConfigFile._IncludeLoader.add_constructor(
                '!include', self._yaml_include)
            self._loader = self._IncludeLoader(f)
            try:
                # YAMLデータを読み込む
                temp_config = self._loader.get_data()
                # 空のYAMLファイルの場合、空の辞書を設定する
                if temp_config is None:
                    temp_config = {}
                # ネスト辞書オブジェクトを作成する
                self._config = self._create_nested_dictionary(temp_config)
            except yaml.YAMLError as e:
                raise DPyYamlConfigFileLoadFaileException(
                    f"Failed to load YAML config file. config_file_path={config_file_path}",
                    e
                )

    def _create_nested_dictionary(self, data: dict) -> NestedDictionary:
        """ネスト辞書オブジェクトを作成する
        Args:
            data (dict): 辞書データ
        Returns:
            NestedDictionary: ネスト辞書オブジェクト
        """
        return super()._create_nested_dictionary(data)

    def get_str(self, key: str, is_required: bool = True) -> str:
        """文字列型の設定値を取得する

        Args:
            key (str): 設定キー
            is_required (bool): 必須フラグ。Trueの場合、キーが存在しない場合に例外をスローする
        Raises:
            KeyError: キーが存在しない場合にスローされる（is_requiredがTrueの場合）
            TypeError: 設定値が文字列型でない場合にスローされる
        Returns:
            str: 設定値
        """
        value = self._config.get(key)
        if value is None:
            if is_required:
                raise KeyError(f"Key '{key}' not found in config.")
            else:
                return None

        if not isinstance(value, str):
            raise TypeError(f"Value for key '{key}' is not a string.")
        return value
