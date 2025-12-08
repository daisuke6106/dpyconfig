from configfile import ConfigFile, YamlConfigFile
from pathlib import Path
from exception.dpyconfigexception import DPyConfigFileNotFoundException, DPyYamlConfigFileLoadFaileException
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
# get メソッドのテスト
# ####################################################################################################
