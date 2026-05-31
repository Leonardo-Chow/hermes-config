# Flutter APK 直接二进制修改（不使用 apktool）

## 背景

apktool 回编的 Flutter APK 在华为/HarmonyOS 设备上几乎必然安装失败。正确做法是用 Python zipfile 直接修改原始 APK。

## 失败案例（v10-v12）

| 版本 | 方法 | 结果 | 原因 |
|:-----|:-----|:-----|:-----|
| v10 | apktool 解码 + 改 libapp.so + 回编 | ❌ 安装失败 | apktool 回编改变了 dex 结构 |
| v11 | apktool 解码 + 添加 RefreshHelper.smali + 回编 | ❌ 安装失败 | 同上 |
| v12 | 同上 + MethodChannel | ❌ 安装失败 | 同上 |
| **v13** | **Python zipfile 直接修改** | **✅ 成功** | 不经过 apktool |

## 成功方案：Python zipfile 直接修改

```python
import zipfile

# 读取原始 APK
with zipfile.ZipFile('original.apk', 'r') as original:
    with zipfile.ZipFile('modified.apk', 'w') as new_apk:
        for file_name in original.namelist():
            file_info = original.getinfo(file_name)  # 关键：保留原始压缩方式
            content = original.read(file_name)
            
            # 修改 libapp.so
            if file_name == 'lib/arm64-v8a/libapp.so':
                # 等长字符串替换
                content = content.replace(b'PAID', b'FREE')
            
            # 写入新 APK，保留原始压缩方式
            new_apk.writestr(file_info, content)  # 关键：用 file_info
```

## 关键陷阱

### ❌ 错误：writestr(file_name, content)
使用文件名字符串作为第一个参数时，所有文件会被重新压缩为 ZIP_DEFLATED：
- 原始 APK: 221MB (698 个 ZIP_DEFLATED + 829 个 ZIP_STORED)
- 错误修改: 120MB (全部 ZIP_DEFLATED)
- 结果: 安装失败

### ✅ 正确：writestr(file_info, content)
使用 file_info 对象作为第一个参数，保留原始压缩方式：
- 原始 APK: 221MB
- 正确修改: 221MB (压缩方式完全一致)
- 结果: 安装成功

## 等长字符串替换示例

| 原始字符串 | 替换字符串 | 字节数 | 效果 |
|:-----------|:-----------|:------:|:-----|
| `PAID` | `FREE` | 4 | 付费判断失败 |
| `isPaidRoom` | `isFreeRoom` | 10 | 付费房间判断失败 |
| `OPEN` | `OPEE` | 4 | 开放状态判断失败 |
| `CLOSED` | `CLOSDD` | 6 | 关闭状态判断失败 |

## 签名

```bash
uber-apk-signer -a modified.apk -o signed.apk
```

使用内置 debug keystore，无需指定 `--ks` 参数。

## 验证

```bash
# 检查文件大小是否一致
ls -lh original.apk signed.apk/signed-aligned-debugSigned.apk

# 检查架构是否完整
unzip -l signed.apk | grep "lib/" | grep "\.so$" | awk '{print $NF}' | cut -d'/' -f2 | sort -u

# 检查字符串是否已替换
strings signed.apk | grep -E "PAID|FREE"
```
