# dpyconfig
本プロジェクトはconfigファイルを読み込んでその設定を取り出すことが可能なライブラリです。

読み込み可能なファイルは以下の通り

## 読み込み可能なファイル

### ini, cnf, config

キー=値として記述されたファイルを読み込む。

例）example.config

```
AAA=BBB
```
 
### yml, yaml

yamlファイルとしてい読み込む
例）example.yaml
```
AAA: BBB
```

## 機能

### INCLUDE指定
ファイルにINCLUDE+ファイルパスを指定することで複数ファイルに跨る設定を読み込むことができます。

### 静的読み込み、動的読み込み
ファイルを読み込む際に、静的に読み込みか、動的に読み込みかを指定することで
プロセスが稼働中に設定ファイルが変更された際の挙動を指定できます。

#### 静的な場合
プロセスが稼働している最中にファイルの記載内容が変わったとしても再読込は行いません。

#### 動的な場合
プロセスが稼働している最中にファイルに記載内容が変わった場合、再読込が行われプロセスからgetした際には最新の値で取得されます。
※背景処理としてデーモンスレッドが指定時間毎（デフォルト１分、オプションとして秒単位で指定可能）にファイルのタイムスタンプを監視しており、タイムスタンプが変わった場合そのファイルの再読込を実施します。

## How to insrall

```
pip install dpyconfig
```

## How to use

```
# import文
from dpyconfig.configfile import ConfigFile

# 静的読み込みの場合
config = ConfigFile.load("./example.conf")
aaa = config.get_str("AAA")
print(aaa) # BBB

# 動的読み込みの場合
config = ConfigFile.dynamic_load("./example.conf")
aaa = config.get_str("AAA")
print(aaa) # BBB
```
