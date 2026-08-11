from abc import ABC, abstractmethod
import os
import re
import yaml
import configparser
from nesteddictonary import NestedDictionary
from exception.dpyconfigexception import (
    DPyConfigFileNotFoundException,
    DPyYamlConfigFileLoadFaileException,
    DPyIniConfigFileLoadFaileException,
)

# ini, cfg, conf, cnf, config 形式として扱う拡張子一覧
_INI_EXTENSIONS = (".ini", ".cfg", ".conf", ".cnf", ".config")
# configparserに渡す前に、セクションヘッダの無いトップレベルのkey=valueを
# 格納するための番兵セクション名
_INI_ROOT_SECTION = "__DPYCONFIG_ROOT__"


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
        # ini, cfg, conf, cnf, configファイルの場合
        elif ext in _INI_EXTENSIONS:
            return IniConfigFile(config_file_path)
        else:
            raise DPyConfigFileNotFoundException(
                f"Unsupported config file type. config_file_path={config_file_path}"
            )

    @classmethod
    def dynamic_load(cls, config_file_path: str, interval_seconds: float = 60):
        """設定ファイルを動的読み込みする

        静的読み込み（load）と異なり、プロセス稼働中にファイル内容が変更された場合、
        バックグラウンドのデーモンスレッドがファイルのタイムスタンプを監視し、
        変更を検知すると自動的に再読込を行う。

        Args:
            config_file_path (str): 設定ファイルパス
            interval_seconds (float, optional): 監視間隔（秒）. Defaults to 60.
        Returns:
            DynamicConfigFile: 動的読み込みに対応した設定ファイルオブジェクト
        """
        if interval_seconds <= 0:
            raise ValueError(
                f"interval_seconds must be greater than 0. interval_seconds={interval_seconds}"
            )
        # dynamicconfigfile と configfile は相互に参照し合うため、
        # モジュールトップレベルではなく遅延importで循環importを回避する
        from dynamicconfigfile import DynamicConfigFile
        return DynamicConfigFile(config_file_path, interval_seconds)

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


class IniConfigFile(ConfigFile):
    """ini, cfg, conf, cnf, config設定ファイルを表すクラス

    `キー=値` 形式で記述された設定ファイルを読み込む。
    セクションヘッダ（`[section]`）が無いトップレベルの記述にも対応するため、
    内部的には番兵セクションを補ってから configparser に渡す。
    """

    #: 単独行での `INCLUDE+ファイルパス` ディレクティブを検出する正規表現
    _INCLUDE_PATTERN = re.compile(r"^INCLUDE\+(.+)$")

    def __init__(self, config_file_path: str):
        super().__init__(config_file_path)
        if self._ext not in _INI_EXTENSIONS:
            raise DPyConfigFileNotFoundException(
                f"Not an INI config file. config_file_path={config_file_path}"
            )
        with open(config_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        try:
            # INCLUDE+ディレクティブを、対象ファイルの中身でテキスト展開する
            expanded_text = self._expand_includes(text)
            # セクションヘッダの無いトップレベル記述を受け付けるため、
            # 番兵セクションを先頭に注入してからパースする
            parser = configparser.ConfigParser(
                interpolation=None, strict=False)
            parser.optionxform = str  # キーの大文字・小文字を保持する
            parser.read_string(
                f"[{_INI_ROOT_SECTION}]\n" + expanded_text,
                source=config_file_path,
            )
            temp_config = self._build_dict(parser)
            self._config = self._create_nested_dictionary(temp_config)
        except configparser.Error as e:
            raise DPyIniConfigFileLoadFaileException(
                f"Failed to load INI config file. config_file_path={config_file_path}",
                e
            )

    def _expand_includes(self, text: str) -> str:
        """INCLUDE+ディレクティブを再帰的に展開する

        Args:
            text (str): 展開対象のテキスト

        Returns:
            str: INCLUDE+行を、対象ファイルの中身に置き換えたテキスト
        """
        lines = []
        for line in text.splitlines():
            match = self._INCLUDE_PATTERN.match(line.strip())
            if match is None:
                lines.append(line)
                continue
            include_path = match.group(1).strip()
            with open(include_path, 'r', encoding='utf-8') as f:
                included_text = f.read()
            # 多段INCLUDEに対応するため、読み込んだ内容も再帰的に展開する
            lines.append(self._expand_includes(included_text))
        return "\n".join(lines)

    def _build_dict(self, parser: configparser.ConfigParser) -> dict:
        """ConfigParserの内容からネスト辞書生成用のdictを組み立てる

        Args:
            parser (configparser.ConfigParser): パース済みのConfigParser

        Returns:
            dict: ルート直下のキーとセクションを1階層のネストとして持つ辞書
        """
        data = {}
        for section in parser.sections():
            if section == _INI_ROOT_SECTION:
                # 番兵セクションの中身はトップレベルのキーとしてマージする
                data.update(dict(parser.items(section)))
            else:
                data[section] = dict(parser.items(section))
        return data
