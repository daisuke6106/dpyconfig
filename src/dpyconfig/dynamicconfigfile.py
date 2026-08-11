import os
import threading
from configfile import ConfigFile


class DynamicConfigFile(ConfigFile):
    """設定ファイルを動的に読み込むクラス

    静的読み込み（ConfigFile.load）と異なり、コンストラクタでバックグラウンドの
    デーモンスレッドを起動する。このスレッドが指定間隔ごとにファイルのタイムスタンプを
    監視し、変更を検知すると自動的に静的読み込み結果（内部インスタンス）を差し替える。
    get_str・search 等は常にその時点の最新の内部インスタンスへ委譲されるため、
    プロセスが稼働中でも最新の値を取得できる。
    """

    def __init__(self, config_file_path: str, interval_seconds: float = 60, autostart: bool = True):
        """コンストラクタ

        Args:
            config_file_path (str): 設定ファイルパス
            interval_seconds (float, optional): 監視間隔（秒）. Defaults to 60.
            autostart (bool, optional): Trueの場合、コンストラクタ内で監視スレッドを開始する. Defaults to True.
        """
        super().__init__(config_file_path)
        self._interval_seconds = interval_seconds
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread = None
        # 初回は同期的に読み込む（存在しない・壊れたファイルは即座に例外送出される）
        self._inner = ConfigFile.load(config_file_path)
        self._mtime = os.path.getmtime(config_file_path)
        if autostart:
            self.start()

    def start(self) -> None:
        """バックグラウンドの監視スレッドを開始する

        既にスレッドが稼働中の場合は何もしない。
        """
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = None) -> None:
        """バックグラウンドの監視スレッドを停止する

        Args:
            timeout (float, optional): スレッド終了を待つ最大秒数. Defaults to None（無制限に待つ）.
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout)

    def reload(self, force: bool = False) -> bool:
        """設定ファイルを再読込する

        Args:
            force (bool, optional): Trueの場合、タイムスタンプの変化に関わらず再読込する. Defaults to False.

        Returns:
            bool: 再読込を実施した場合True、タイムスタンプに変化が無く再読込しなかった場合False

        Raises:
            DPyConfigException: 再読込に失敗した場合、その原因例外がそのまま送出される
        """
        current_mtime = os.path.getmtime(self._config_file_path)
        if not force and current_mtime == self._mtime:
            return False
        new_inner = ConfigFile.load(self._config_file_path)
        with self._lock:
            self._inner = new_inner
            self._mtime = current_mtime
        return True

    def _watch_loop(self) -> None:
        """バックグラウンドスレッドの監視ループ

        stop() が呼ばれるまで指定間隔で reload() を試み続ける。
        監視対象ファイルが一時的に壊れている等の理由で reload() が失敗しても、
        監視スレッド自体は継続する。
        """
        while not self._stop_event.wait(self._interval_seconds):
            try:
                self.reload()
            except Exception:
                pass

    def search(self, key: str) -> list:
        """ 指定されたキーを持つ要素を再帰的に検索する（最新の内部インスタンスへ委譲）

        Args:
            key (str): 検索するキー

        Returns:
            list: 検索結果のリスト
        """
        with self._lock:
            inner = self._inner
        return inner.search(key)

    def get_str(self, key: str, is_required: bool = True) -> str:
        """文字列型の設定値を取得する（最新の内部インスタンスへ委譲）

        Args:
            key (str): 設定キー
            is_required (bool): 必須フラグ。Trueの場合、キーが存在しない場合に例外をスローする

        Returns:
            str: 設定値
        """
        with self._lock:
            inner = self._inner
        return inner.get_str(key, is_required)

    def __enter__(self) -> "DynamicConfigFile":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.stop()
        return False
