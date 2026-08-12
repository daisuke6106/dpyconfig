from dpyconfig.configfile import ConfigFile, YamlConfigFile, IniConfigFile
from pathlib import Path
from dpyconfig.exception.dpyconfigexception import (
    DPyConfigFileNotFoundException,
    DPyYamlConfigFileLoadFaileException,
    DPyIniConfigFileLoadFaileException,
)
import pytest

# ####################################################################################################
# load メソッドのテスト
# ####################################################################################################


def test_load_empty_yaml(tmp_path: Path):
    """ 空の YAML ファイルを読み込めること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("", encoding="utf-8")
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config == {}


def test_load_file(tmp_path: Path):
    """単純な YAML を読み込めること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single:\n")
        f.write(" - element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi:\n")
        f.write(" - element01\n")
        f.write(" - element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single_block: [element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi_block: [element01,element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("parent:\n")
        f.write("  child: value\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["key"] == "value"
    assert cfg._config["list_single"] == ["element01"]
    assert cfg._config["list_multi"] == ["element01", "element02"]
    assert cfg._config["list_single_block"] == ["element01"]
    assert cfg._config["list_multi_block"] == ["element01", "element02"]
    assert cfg._config["parent"]["child"] == "value"


def test_load_include_single_files(tmp_path: Path):
    """Include 機能で他の YAML ファイルを読み込めること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path = tmp_path / "included.yaml"
    with included_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("inc_key: inc_value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single:\n")
        f.write(" - inc_element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi:\n")
        f.write(" - inc_element01\n")
        f.write(" - inc_element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single_block: [inc_element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi_block: [inc_element01,inc_element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("inc_parent:\n")
        f.write("  inc_child: inc_value\n")

    main_path = tmp_path / "config.yaml"
    with main_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single:\n")
        f.write(" - element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi:\n")
        f.write(" - element01\n")
        f.write(" - element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single_block: [element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi_block: [element01,element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("parent:\n")
        f.write("  child: value\n")
        # ハッシュ形式の YAML データを書き込む
        f.write("# INCLUDE\n")
        f.write(f"include_a: !include {included_path}\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["key"] == "value"
    assert cfg._config["list_single"] == ["element01"]
    assert cfg._config["list_multi"] == ["element01", "element02"]
    assert cfg._config["list_single_block"] == ["element01"]
    assert cfg._config["list_multi_block"] == ["element01", "element02"]
    assert cfg._config["parent"]["child"] == "value"

    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["include_a"]["inc_key"] == "inc_value"
    assert cfg._config["include_a"]["inc_list_single"] == ["inc_element01"]
    assert cfg._config["include_a"]["inc_list_multi"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_a"]["inc_list_single_block"] == [
        "inc_element01"]
    assert cfg._config["include_a"]["inc_list_multi_block"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_a"]["inc_parent"]["inc_child"] == "inc_value"


def test_load_include_muiti_files(tmp_path: Path):
    """Include 機能で他の YAML ファイルを読み込めること（複数）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path_a = tmp_path / "included_a.yaml"
    with included_path_a.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("inc_key: inc_value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single:\n")
        f.write(" - inc_element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi:\n")
        f.write(" - inc_element01\n")
        f.write(" - inc_element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single_block: [inc_element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi_block: [inc_element01,inc_element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("inc_parent:\n")
        f.write("  inc_child: inc_value\n")

    included_path_b = tmp_path / "included_b.yaml"
    with included_path_b.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("inc_key: inc_value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single:\n")
        f.write(" - inc_element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi:\n")
        f.write(" - inc_element01\n")
        f.write(" - inc_element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single_block: [inc_element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi_block: [inc_element01,inc_element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("inc_parent:\n")
        f.write("  inc_child: inc_value\n")

    main_path = tmp_path / "config.yaml"
    with main_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single:\n")
        f.write(" - element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi:\n")
        f.write(" - element01\n")
        f.write(" - element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single_block: [element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi_block: [element01,element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("parent:\n")
        f.write("  child: value\n")
        # ハッシュ形式の YAML データを書き込む
        f.write("# INCLUDE\n")
        f.write(f"include_a: !include {included_path_a}\n")
        # ハッシュ形式の YAML データを書き込む
        f.write("# INCLUDE\n")
        f.write(f"include_b: !include {included_path_b}\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["key"] == "value"
    assert cfg._config["list_single"] == ["element01"]
    assert cfg._config["list_multi"] == ["element01", "element02"]
    assert cfg._config["list_single_block"] == ["element01"]
    assert cfg._config["list_multi_block"] == ["element01", "element02"]
    assert cfg._config["parent"]["child"] == "value"

    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["include_a"]["inc_key"] == "inc_value"
    assert cfg._config["include_a"]["inc_list_single"] == ["inc_element01"]
    assert cfg._config["include_a"]["inc_list_multi"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_a"]["inc_list_single_block"] == [
        "inc_element01"]
    assert cfg._config["include_a"]["inc_list_multi_block"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_a"]["inc_parent"]["inc_child"] == "inc_value"

    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["include_b"]["inc_key"] == "inc_value"
    assert cfg._config["include_b"]["inc_list_single"] == ["inc_element01"]
    assert cfg._config["include_b"]["inc_list_multi"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_b"]["inc_list_single_block"] == [
        "inc_element01"]
    assert cfg._config["include_b"]["inc_list_multi_block"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_b"]["inc_parent"]["inc_child"] == "inc_value"


def test_load_include_muiti_stage_files(tmp_path: Path):
    """Include 機能で他の YAML ファイルを読み込めること（多段）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path_a = tmp_path / "included_a.yaml"
    with included_path_a.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("inc_key: inc_value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single:\n")
        f.write(" - inc_element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi:\n")
        f.write(" - inc_element01\n")
        f.write(" - inc_element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single_block: [inc_element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi_block: [inc_element01,inc_element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("inc_parent:\n")
        f.write("  inc_child: inc_value\n")

    included_path_b = tmp_path / "included_b.yaml"
    with included_path_b.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("inc_key: inc_value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single:\n")
        f.write(" - inc_element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi:\n")
        f.write(" - inc_element01\n")
        f.write(" - inc_element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("inc_list_single_block: [inc_element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("inc_list_multi_block: [inc_element01,inc_element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("inc_parent:\n")
        f.write("  inc_child: inc_value\n")
        # ハッシュ形式の YAML データを書き込む
        f.write("# INCLUDE\n")
        f.write(f"include_a: !include {included_path_a}\n")

    main_path = tmp_path / "config.yaml"
    with main_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: value\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single:\n")
        f.write(" - element01\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi:\n")
        f.write(" - element01\n")
        f.write(" - element02\n")
        # 配列形式（単一）の YAML データを書き込む
        f.write("# リスト（単一）\n")
        f.write("list_single_block: [element01]\n")
        # 配列形式（複数）の YAML データを書き込む
        f.write("# リスト（複数）\n")
        f.write("list_multi_block: [element01,element02]\n")
        # ネスト形式の YAML データを書き込む
        f.write("# ネスト形式\n")
        f.write("parent:\n")
        f.write("  child: value\n")
        # ハッシュ形式の YAML データを書き込む
        f.write("# INCLUDE\n")
        f.write(f"include_b: !include {included_path_b}\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["key"] == "value"
    assert cfg._config["list_single"] == ["element01"]
    assert cfg._config["list_multi"] == ["element01", "element02"]
    assert cfg._config["list_single_block"] == ["element01"]
    assert cfg._config["list_multi_block"] == ["element01", "element02"]
    assert cfg._config["parent"]["child"] == "value"

    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["include_b"]["inc_key"] == "inc_value"
    assert cfg._config["include_b"]["inc_list_single"] == ["inc_element01"]
    assert cfg._config["include_b"]["inc_list_multi"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_b"]["inc_list_single_block"] == [
        "inc_element01"]
    assert cfg._config["include_b"]["inc_list_multi_block"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_b"]["inc_parent"]["inc_child"] == "inc_value"

    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config["include_b"]["include_a"]["inc_key"] == "inc_value"
    assert cfg._config["include_b"]["include_a"]["inc_list_single"] == [
        "inc_element01"]
    assert cfg._config["include_b"]["include_a"]["inc_list_multi"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_b"]["include_a"]["inc_list_single_block"] == [
        "inc_element01"]
    assert cfg._config["include_b"]["include_a"]["inc_list_multi_block"] == [
        "inc_element01", "inc_element02"]
    assert cfg._config["include_b"]["include_a"]["inc_parent"]["inc_child"] == "inc_value"


def test_load_file_not_found_raises(tmp_path: Path):
    """ ファイルが存在しない場合、例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    missing_path = tmp_path / "missing.yaml"
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(DPyConfigFileNotFoundException):
        ConfigFile.load(str(missing_path))


def test_load_unsupported_extension_raises(tmp_path: Path):
    """ サポートしていない拡張子は例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    txt_path = tmp_path / "config.txt"
    txt_path.write_text("irrelevant", encoding="utf-8")
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(DPyConfigFileNotFoundException):
        ConfigFile.load(str(txt_path))


def test_load_nonexistent_yaml_raises(tmp_path: Path):
    """ .yaml 拡張子でもファイルが存在しなければ例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    missing = tmp_path / "nope.yaml"
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert not missing.exists()
    with pytest.raises(DPyConfigFileNotFoundException):
        ConfigFile.load(str(missing))


def test_load_yml_extension(tmp_path: Path):
    """ .yml 拡張子も受け付けること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yml"
    config_path.write_text("a: 1\n", encoding="utf-8")
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, YamlConfigFile)
    assert cfg._config == {"a": 1}


def test_load_notyamlformat_raise(tmp_path: Path):
    """ .yml 拡張子でも YAML 形式でなければ例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# 不正なYAML形式\n")
        f.write("list_multi:\n")
        f.write("-element01\n")
        f.write("-element02\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(DPyYamlConfigFileLoadFaileException):
        YamlConfigFile(str(config_path))

# ####################################################################################################
# get_str メソッドのテスト
# ####################################################################################################


def test_get_str_existing_key(tmp_path: Path):
    """ 存在するキーの文字列値を取得できること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: value\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))
    result = cfg.get_str("key")

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert result == "value"


def test_get_str_not_existing_key(tmp_path: Path):
    """ 存在しないキーの文字列値を取得しようとすると例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: value\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(KeyError):
        cfg.get_str("nonexistent_key")


def test_get_str_brank_value(tmp_path: Path):
    """ 値がブランクの場合としてKeyErrorがraiseされること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: \n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(KeyError):
        cfg.get_str("key")


def test_get_str_str_with_doblequote_value(tmp_path: Path):
    """ 文字列値を文字列値として取得できること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: \"123\"\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert cfg.get_str("key") == "123"


def test_get_str_not_str_value_int(tmp_path: Path):
    """ 数値を文字列値として取得しようとすると例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: 123\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(TypeError):
        cfg.get_str("key")


def test_get_str_not_str_value_bool(tmp_path: Path):
    """ 数値を文字列値として取得しようとすると例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # ハッシュ形式の YAML データを書き込む
        f.write("# ハッシュ\n")
        f.write("key: true\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(TypeError):
        cfg.get_str("key")

# ####################################################################################################
# IniConfigFile load メソッドのテスト
# ####################################################################################################


def test_ini_load_all_extensions(tmp_path: Path):
    """ ini, cfg, conf, cnf, config のいずれの拡張子でもIniConfigFileとして読み込めること

    Args:
        tmp_path (Path): _description_
    """
    for ext in (".ini", ".cfg", ".conf", ".cnf", ".config"):
        # ====================================================================================================
        # データ作成
        # ====================================================================================================
        config_path = tmp_path / f"config{ext}"
        config_path.write_text("AAA=BBB\n", encoding="utf-8")
        # ====================================================================================================
        # テスト実行
        # ====================================================================================================
        cfg = ConfigFile.load(str(config_path))
        # ====================================================================================================
        # 検証
        # ====================================================================================================
        assert isinstance(cfg, IniConfigFile)
        assert cfg._config["AAA"] == "BBB"


def test_ini_load_file_with_section(tmp_path: Path):
    """ セクションヘッダ付きの記述がネストされた辞書として読み込めること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    with config_path.open(mode="a", encoding="utf-8") as f:
        f.write("AAA=BBB\n")
        f.write("[section]\n")
        f.write("KEY=VALUE\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, IniConfigFile)
    assert cfg._config["AAA"] == "BBB"
    assert cfg._config["section"]["KEY"] == "VALUE"


def test_ini_load_key_case_is_preserved(tmp_path: Path):
    """ キーの大文字・小文字が保持されること（小文字化されないこと）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    config_path.write_text("MixedCaseKey=Value\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert cfg._config["MixedCaseKey"] == "Value"
    assert "mixedcasekey" not in cfg._config


def test_ini_load_include_single_files(tmp_path: Path):
    """ INCLUDE+機能で他のiniファイルを読み込めること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path = tmp_path / "included.ini"
    included_path.write_text("INC_KEY=inc_value\n", encoding="utf-8")

    main_path = tmp_path / "config.ini"
    with main_path.open(mode="a", encoding="utf-8") as f:
        f.write("AAA=BBB\n")
        f.write(f"INCLUDE+{included_path}\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, IniConfigFile)
    assert cfg._config["AAA"] == "BBB"
    assert cfg._config["INC_KEY"] == "inc_value"


def test_ini_load_include_muiti_files(tmp_path: Path):
    """ INCLUDE+機能で他のiniファイルを読み込めること（複数）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path_a = tmp_path / "included_a.ini"
    included_path_a.write_text("INC_KEY_A=inc_value_a\n", encoding="utf-8")

    included_path_b = tmp_path / "included_b.ini"
    included_path_b.write_text("INC_KEY_B=inc_value_b\n", encoding="utf-8")

    main_path = tmp_path / "config.ini"
    with main_path.open(mode="a", encoding="utf-8") as f:
        f.write("AAA=BBB\n")
        f.write(f"INCLUDE+{included_path_a}\n")
        f.write(f"INCLUDE+{included_path_b}\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, IniConfigFile)
    assert cfg._config["AAA"] == "BBB"
    assert cfg._config["INC_KEY_A"] == "inc_value_a"
    assert cfg._config["INC_KEY_B"] == "inc_value_b"


def test_ini_load_include_muiti_stage_files(tmp_path: Path):
    """ INCLUDE+機能で他のiniファイルを読み込めること（多段）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path_a = tmp_path / "included_a.ini"
    included_path_a.write_text("INC_KEY_A=inc_value_a\n", encoding="utf-8")

    included_path_b = tmp_path / "included_b.ini"
    with included_path_b.open(mode="a", encoding="utf-8") as f:
        f.write("INC_KEY_B=inc_value_b\n")
        f.write(f"INCLUDE+{included_path_a}\n")

    main_path = tmp_path / "config.ini"
    with main_path.open(mode="a", encoding="utf-8") as f:
        f.write("AAA=BBB\n")
        f.write(f"INCLUDE+{included_path_b}\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert isinstance(cfg, IniConfigFile)
    assert cfg._config["AAA"] == "BBB"
    assert cfg._config["INC_KEY_B"] == "inc_value_b"
    assert cfg._config["INC_KEY_A"] == "inc_value_a"


def test_ini_load_include_overridden_by_local_key(tmp_path: Path):
    """ INCLUDE+で読み込んだキーを、それより後に書かれたローカルのキーで上書き（後勝ち）できること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    included_path = tmp_path / "included.ini"
    included_path.write_text("KEY=FromInclude\n", encoding="utf-8")

    main_path = tmp_path / "config.ini"
    with main_path.open(mode="a", encoding="utf-8") as f:
        f.write(f"INCLUDE+{included_path}\n")
        f.write("KEY=FromLocal\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(main_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert cfg._config["KEY"] == "FromLocal"


def test_ini_load_file_not_found_raises(tmp_path: Path):
    """ ファイルが存在しない場合、例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    missing_path = tmp_path / "missing.ini"
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(DPyConfigFileNotFoundException):
        ConfigFile.load(str(missing_path))


def test_ini_load_invalid_format_raises(tmp_path: Path):
    """ 不正な形式のiniファイルを読み込もうとすると例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    with config_path.open(mode="a", encoding="utf-8") as f:
        # key=value 形式でも継続行でもセクションヘッダでもない不正な行
        f.write("this line is not a valid ini statement\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(DPyIniConfigFileLoadFaileException):
        IniConfigFile(str(config_path))

# ####################################################################################################
# IniConfigFile get_str メソッドのテスト
# ####################################################################################################


def test_ini_get_str_existing_key(tmp_path: Path):
    """ 存在するキーの文字列値を取得できること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    config_path.write_text("AAA=BBB\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))
    result = cfg.get_str("AAA")

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert result == "BBB"


def test_ini_get_str_not_existing_key(tmp_path: Path):
    """ 存在しないキーの文字列値を取得しようとすると例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    config_path.write_text("AAA=BBB\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(KeyError):
        cfg.get_str("nonexistent_key")


def test_ini_get_str_not_required_returns_none(tmp_path: Path):
    """ is_required=Falseの場合、存在しないキーはNoneが返ること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    config_path.write_text("AAA=BBB\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))
    result = cfg.get_str("nonexistent_key", is_required=False)

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert result is None


def test_ini_get_str_blank_value(tmp_path: Path):
    """ 値がブランクの場合、空文字が返ること（YAMLの空値がKeyErrorになるのとは異なる仕様）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    config_path.write_text("AAA=\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert cfg.get_str("AAA") == ""


def test_ini_get_str_numeric_and_bool_like_values_are_strings(tmp_path: Path):
    """ 数値・真偽値らしい値も常に文字列として取得できること（ini値は常に文字列のため）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.ini"
    with config_path.open(mode="a", encoding="utf-8") as f:
        f.write("NUM=123\n")
        f.write("FLAG=true\n")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.load(str(config_path))

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert cfg.get_str("NUM") == "123"
    assert cfg.get_str("FLAG") == "true"

# ####################################################################################################
# dynamic_load メソッドのテスト
# （DynamicConfigFile固有の内部動作の詳細テストは test_dynamicconfigfile.py を参照）
# ####################################################################################################


def test_dynamic_load_returns_dynamic_config_file(tmp_path: Path):
    """ dynamic_load が DynamicConfigFile を返し、静的読み込みと同じ値が取得できること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    from dpyconfig.dynamicconfigfile import DynamicConfigFile
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg = ConfigFile.dynamic_load(str(config_path), interval_seconds=0.1)

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    try:
        assert isinstance(cfg, DynamicConfigFile)
        assert isinstance(cfg, ConfigFile)
        assert cfg.get_str("AAA") == "BBB"
    finally:
        cfg.stop()


def test_dynamic_load_invalid_interval_raises(tmp_path: Path):
    """ interval_secondsが0以下の場合、例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(ValueError):
        ConfigFile.dynamic_load(str(config_path), interval_seconds=0)


def test_dynamic_load_file_not_found_raises(tmp_path: Path):
    """ ファイルが存在しない場合、静的読み込みと同様に例外を投げること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    missing_path = tmp_path / "missing.yaml"
    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    # ====================================================================================================
    # 検証
    # ====================================================================================================
    with pytest.raises(DPyConfigFileNotFoundException):
        ConfigFile.dynamic_load(str(missing_path), interval_seconds=0.1)
