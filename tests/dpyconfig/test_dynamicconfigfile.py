import os
import time
from pathlib import Path

import pytest

from dpyconfig.configfile import ConfigFile
from dpyconfig.dynamicconfigfile import DynamicConfigFile
from dpyconfig.exception.dpyconfigexception import DPyYamlConfigFileLoadFaileException


def _wait_until(predicate, timeout: float = 2.0, interval: float = 0.02) -> bool:
    """ predicateがTrueになるまでポーリングする（バックグラウンドスレッドの結果待ち用）

    Args:
        predicate (Callable[[], bool]): 判定関数
        timeout (float, optional): 最大待機秒数. Defaults to 2.0.
        interval (float, optional): ポーリング間隔（秒）. Defaults to 0.02.

    Returns:
        bool: timeout以内にpredicateがTrueになった場合True
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def _touch_future(path: Path, seconds_ahead: float = 5.0) -> None:
    """ ファイルのmtimeを明示的に未来へずらす（ファイルシステムのmtime精度に依存しないため）

    Args:
        path (Path): 対象ファイルパス
        seconds_ahead (float, optional): 現在のmtimeから何秒進めるか. Defaults to 5.0.
    """
    current = os.path.getmtime(str(path))
    new_time = current + seconds_ahead
    os.utime(str(path), (new_time, new_time))


# ####################################################################################################
# 初期読み込み・reload() のテスト
# ####################################################################################################


def test_initial_load_matches_static_load(tmp_path: Path):
    """ 初回ロード直後は静的読み込みと同じ値が取得できること

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
    cfg = DynamicConfigFile(str(config_path), autostart=False)

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    try:
        assert cfg.get_str("AAA") == "BBB"
        assert cfg.search("AAA") == ["BBB"]
    finally:
        cfg.stop()


def test_reload_force_updates_value(tmp_path: Path):
    """ reload(force=True) を明示的に呼び出すと、ファイルの最新内容が反映されること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")
    cfg = DynamicConfigFile(str(config_path), autostart=False)

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    try:
        config_path.write_text("AAA: CCC\n", encoding="utf-8")
        _touch_future(config_path)
        reloaded = cfg.reload(force=True)

        # ====================================================================================================
        # 検証
        # ====================================================================================================
        assert reloaded is True
        assert cfg.get_str("AAA") == "CCC"
    finally:
        cfg.stop()


def test_reload_without_change_returns_false(tmp_path: Path):
    """ ファイルに変化が無い場合、reload() は再読込を行わずFalseを返すこと

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")
    cfg = DynamicConfigFile(str(config_path), autostart=False)

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    try:
        reloaded = cfg.reload()

        # ====================================================================================================
        # 検証
        # ====================================================================================================
        assert reloaded is False
        assert cfg.get_str("AAA") == "BBB"
    finally:
        cfg.stop()


def test_reload_propagates_load_errors(tmp_path: Path):
    """ reload() は再読込に失敗した場合、その例外をそのまま送出すること（バックグラウンド監視とは非対称の仕様）

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")
    cfg = DynamicConfigFile(str(config_path), autostart=False)

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    try:
        with config_path.open(mode="a", encoding="utf-8") as f:
            f.write("-invalid_yaml_line\n")
            f.write("-another_invalid_line\n")
        _touch_future(config_path)

        # ====================================================================================================
        # 検証
        # ====================================================================================================
        with pytest.raises(DPyYamlConfigFileLoadFaileException):
            cfg.reload(force=True)
    finally:
        cfg.stop()


# ####################################################################################################
# バックグラウンド監視スレッドのテスト
# ####################################################################################################


def test_background_thread_autoreloads(tmp_path: Path):
    """ バックグラウンドスレッドが自律的にファイルの変更を検知し再読込すること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")
    cfg = DynamicConfigFile(str(config_path), interval_seconds=0.1)

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    try:
        config_path.write_text("AAA: CCC\n", encoding="utf-8")
        _touch_future(config_path)

        # ====================================================================================================
        # 検証
        # ====================================================================================================
        assert _wait_until(lambda: cfg.get_str("AAA") == "CCC", timeout=2.0)
    finally:
        cfg.stop()


def test_stop_halts_background_reload(tmp_path: Path):
    """ stop() 呼び出し後は、ファイルを変更してもバックグラウンド再読込が行われないこと

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")
    cfg = DynamicConfigFile(str(config_path), interval_seconds=0.05)

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    cfg.stop()
    config_path.write_text("AAA: CCC\n", encoding="utf-8")
    _touch_future(config_path)
    # stop後も監視周期数回分は待って、反映されないことを確認する
    time.sleep(0.3)

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert cfg.get_str("AAA") == "BBB"
    assert cfg._thread.is_alive() is False


def test_start_is_idempotent(tmp_path: Path):
    """ start() を複数回呼び出してもスレッドが1つだけ稼働すること

    Args:
        tmp_path (Path): _description_
    """
    # ====================================================================================================
    # データ作成
    # ====================================================================================================
    config_path = tmp_path / "config.yaml"
    config_path.write_text("AAA: BBB\n", encoding="utf-8")
    cfg = DynamicConfigFile(str(config_path), interval_seconds=1)

    # ====================================================================================================
    # テスト実行
    # ====================================================================================================
    try:
        first_thread = cfg._thread
        cfg.start()
        second_thread = cfg._thread

        # ====================================================================================================
        # 検証
        # ====================================================================================================
        assert first_thread is second_thread
        assert first_thread.is_alive()
    finally:
        cfg.stop()


def test_context_manager_stops_thread_on_exit(tmp_path: Path):
    """ withブロックを抜けると監視スレッドが停止すること

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
    with ConfigFile.dynamic_load(str(config_path), interval_seconds=0.1) as cfg:
        assert cfg.get_str("AAA") == "BBB"
        thread_during = cfg._thread

    # ====================================================================================================
    # 検証
    # ====================================================================================================
    assert thread_during.is_alive() is False
