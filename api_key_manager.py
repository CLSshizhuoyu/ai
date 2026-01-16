import os
import json
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Optional, List, Dict

# ==================== 配置项（可根据需要调整） ====================
API_KEY_FILE = "api_keys.enc"    # 加密的API密钥文件
CACHE_FILE = "secret_cache.enc"  # 缓存文件
SALT_FILE = "salt.bin"          # 盐值文件
MAX_ATTEMPTS = 3                # 最大秘钥输入尝试次数
# =================================================================


class APIKeyManager:
    """API密钥管理库，提供通过索引/名称获取解密后密钥的功能"""

    def __init__(self):
        self._api_keys: Optional[Dict[str, str]] = None  # 存储解密后的密钥

    def _get_fernet_key(self, password: str) -> Optional[bytes]:
        """生成Fernet加密/解密密钥"""
        if not os.path.exists(SALT_FILE):
            raise FileNotFoundError(f"盐值文件 {SALT_FILE} 不存在，请确认文件完整")

        # 读取盐值
        with open(SALT_FILE, "rb") as f:
            salt = f.read()

        # 生成密钥
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
        except Exception as e:
            raise RuntimeError(f"生成解密密钥失败：{str(e)}")

    def _decrypt_api_keys(self, password: str) -> Dict[str, str]:
        """解密API密钥，返回字典"""
        if not os.path.exists(API_KEY_FILE):
            raise FileNotFoundError(f"API密钥文件 {API_KEY_FILE} 不存在，请确认文件完整")

        # 获取解密密钥
        fernet_key = self._get_fernet_key(password)
        if not fernet_key:
            raise RuntimeError("无法生成解密密钥")

        # 解密数据
        try:
            fernet = Fernet(fernet_key)
            with open(API_KEY_FILE, "rb") as f:
                encrypted_data = f.read()

            decrypted_str = fernet.decrypt(encrypted_data).decode()
            api_keys = json.loads(decrypted_str)

            if not isinstance(api_keys, dict) or len(api_keys) == 0:
                raise ValueError("解密后的API密钥格式无效")

            return api_keys
        except Exception as e:
            if "InvalidToken" in str(e):
                raise ValueError("解密失败：秘钥不正确")
            raise RuntimeError(f"解密过程出错：{str(e)}")

    def _cache_secret(self, password: str) -> None:
        """加密缓存秘钥"""
        try:
            # 生成临时加密密钥
            cache_key = Fernet.generate_key()
            fernet = Fernet(cache_key)
            encrypted_password = fernet.encrypt(password.encode())

            # 保存缓存数据
            cache_data = {
                "key": base64.urlsafe_b64encode(cache_key).decode(),
                "password": base64.urlsafe_b64encode(encrypted_password).decode()
            }

            with open(CACHE_FILE, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            raise RuntimeError(f"缓存秘钥失败：{str(e)}")

    def _get_cached_secret(self) -> Optional[str]:
        """读取缓存的秘钥"""
        if not os.path.exists(CACHE_FILE):
            return None

        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)

            # 解密缓存的秘钥
            cache_key = base64.urlsafe_b64decode(cache_data["key"])
            encrypted_password = base64.urlsafe_b64decode(
                cache_data["password"])

            fernet = Fernet(cache_key)
            password = fernet.decrypt(encrypted_password).decode()
            return password
        except Exception:
            # 缓存损坏则删除
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
            return None

    def _safe_input_password(self, prompt: str) -> str:
        """
        兼容CMD的密码输入函数（替代getpass）
        :param prompt: 输入提示语
        :return: 用户输入的密码
        """
        if sys.platform == "win32":
            # Windows系统：使用msvcrt实现无回显输入
            import msvcrt
            print(prompt, end="", flush=True)
            password = []
            while True:
                # 读取单个字符
                char = msvcrt.getch()
                # 处理回车（结束输入）
                if char in (b'\r', b'\n'):
                    print()  # 换行
                    break
                # 处理退格
                elif char == b'\x08':  # Backspace
                    if password:
                        password.pop()
                        # 回显退格（删除屏幕上的*）
                        print('\b \b', end="", flush=True)
                # 处理Ctrl+C（终止程序）
                elif char == b'\x03':
                    raise KeyboardInterrupt("用户终止输入")
                # 普通字符
                else:
                    password.append(char.decode('utf-8', errors='ignore'))
                    print('*', end="", flush=True)  # 显示*代替真实字符
            return ''.join(password)
        else:
            # 非Windows系统：继续使用getpass
            import getpass
            return getpass.getpass(prompt)

    def _prompt_for_secret(self) -> str:
        """提示用户输入秘钥（兼容CMD）"""
        print("\n=== 请输入API密钥解密秘钥 ===")
        for attempt in range(MAX_ATTEMPTS):
            remaining = MAX_ATTEMPTS - attempt
            prompt = f"秘钥（剩余尝试次数：{remaining}）："
            try:
                # 使用兼容CMD的输入函数
                password = self._safe_input_password(prompt)
                if not password:
                    print("错误：秘钥不能为空")
                    continue
                # 验证秘钥是否正确
                self._decrypt_api_keys(password)
                # 缓存秘钥
                self._cache_secret(password)
                return password
            except ValueError as e:
                print(f"错误：{str(e)}")
            except KeyboardInterrupt:
                print("\n用户终止输入，程序退出")
                sys.exit(1)
            except Exception as e:
                print(f"错误：{str(e)}")

        raise PermissionError("多次输入错误，无法获取API密钥")

    def load_api_keys(self) -> None:
        """加载并解密API密钥（核心方法，首次调用自动执行）"""
        if self._api_keys is not None:
            return  # 已加载过，直接返回

        # 1. 尝试使用缓存的秘钥
        cached_secret = self._get_cached_secret()
        if cached_secret:
            try:
                print("检测到缓存的秘钥，正在自动解密...")
                self._api_keys = self._decrypt_api_keys(cached_secret)
                return
            except Exception:
                print("缓存秘钥无效，需要重新输入")

        # 2. 提示用户输入秘钥
        self._prompt_for_secret()
        # 重新加载（此时秘钥已缓存）
        self.load_api_keys()

    def get_key_by_index(self, index: int) -> str:
        """
        通过索引（第几个）获取API密钥
        :param index: 索引，从1开始（如1表示第一个，2表示第二个）
        :return: 对应的API密钥值
        :raises IndexError: 索引超出范围
        """
        # 确保密钥已加载
        self.load_api_keys()

        if self._api_keys is None:
            raise RuntimeError("API密钥未成功加载")

        # 将字典的键转为列表，按插入顺序获取第N个
        key_names = list(self._api_keys.keys())

        if index < 1 or index > len(key_names):
            raise IndexError(f"索引超出范围，当前共有 {len(key_names)} 个API密钥")

        key_name = key_names[index - 1]
        return self._api_keys[key_name]

    def get_key_by_name(self, name: str) -> str:
        """
        通过名称获取API密钥
        :param name: 密钥名称（如"openai_api_key"）
        :return: 对应的API密钥值
        :raises KeyError: 名称不存在
        """
        # 确保密钥已加载
        self.load_api_keys()

        if self._api_keys is None:
            raise RuntimeError("API密钥未成功加载")

        if name not in self._api_keys:
            raise KeyError(
                f"不存在名为 {name} 的API密钥，可用名称：{list(self._api_keys.keys())}")

        return self._api_keys[name]

    def list_keys(self) -> List[str]:
        """
        获取所有API密钥的名称列表（按顺序）
        :return: 密钥名称列表
        """
        self.load_api_keys()

        if self._api_keys is None:
            raise RuntimeError("API密钥未成功加载")

        return list(self._api_keys.keys())

# ==================== 便捷函数（简化调用） ====================


def get_api_key(index: int = None, name: str = None) -> str:
    """
    快速获取API密钥（二选一：索引或名称）
    :param index: 第几个密钥（从1开始）
    :param name: 密钥名称
    :return: 对应的API密钥值
    """
    if index is None and name is None:
        raise ValueError("必须指定 index 或 name 参数")

    manager = APIKeyManager()

    if index is not None:
        return manager.get_key_by_index(index)
    else:
        return manager.get_key_by_name(name)
