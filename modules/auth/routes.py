"""
认证API路由

支持：
- 手机验证码登录
- 密码登录
- 用户注册
- Token刷新
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import logging
import hashlib
import secrets
import jwt
import time
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])

# JWT配置 - 从环境变量读取
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24


# ============ 请求/响应模型 ============

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号", pattern=r"^1[3-9]\d{9}$")


class SmsLoginRequest(BaseModel):
    """短信验证码登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码", min_length=4, max_length=6)


class PasswordLoginRequest(BaseModel):
    """密码登录请求"""
    username: str = Field(..., description="用户名/手机号/邮箱")
    password: str = Field(..., description="密码", min_length=6)


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")
    password: str = Field(..., description="密码", min_length=6)
    nickname: Optional[str] = Field(None, description="昵称")


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    token: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    role: Optional[str] = None
    message: Optional[str] = None


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    nickname: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    role: str
    avatar: Optional[str]


# ============ 工具函数 ============

def generate_token(user_id: int, username: str, role: str) -> str:
    """生成JWT Token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """验证JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的Token")


def hash_password(password: str) -> str:
    """密码哈希"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{salt}:{pwd_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    try:
        salt, pwd_hash = password_hash.split(":")
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest() == pwd_hash
    except:
        return False


def generate_verify_code() -> str:
    """生成6位验证码"""
    return str(secrets.randbelow(900000) + 100000)


# ============ API端点 ============

@router.post("/send-code")
async def send_verify_code(request: SendCodeRequest):
    """
    发送验证码

    - **phone**: 手机号
    """
    try:
        from common.postgresql_pool import pg_pool

        # 生成验证码
        code = generate_verify_code()
        expires_at = datetime.now() + timedelta(minutes=5)

        with pg_pool.get_dict_cursor() as cursor:
            # 删除旧验证码
            cursor.execute(
                "DELETE FROM ai_service.verify_codes WHERE phone = %s AND purpose = 'login'",
                (request.phone,)
            )

            # 插入新验证码
            cursor.execute(
                """
                INSERT INTO ai_service.verify_codes (phone, code, purpose, expires_at)
                VALUES (%s, %s, 'login', %s)
                """,
                (request.phone, code, expires_at)
            )

        # TODO: 调用短信服务发送验证码
        # 这里先返回验证码（生产环境应该发送短信）
        logger.info(f"📱 验证码已发送: {request.phone} -> {code}")

        return {
            "success": True,
            "message": "验证码已发送",
            # 开发环境返回验证码，生产环境删除这行
            "code": code
        }

    except Exception as e:
        logger.error(f"❌ 发送验证码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/sms", response_model=LoginResponse)
async def sms_login(request: SmsLoginRequest):
    """
    短信验证码登录

    - **phone**: 手机号
    - **code**: 验证码
    """
    try:
        from common.postgresql_pool import pg_pool

        with pg_pool.get_dict_cursor() as cursor:
            # 验证验证码
            cursor.execute(
                """
                SELECT id FROM ai_service.verify_codes
                WHERE phone = %s AND code = %s AND purpose = 'login'
                AND is_used = FALSE AND expires_at > %s
                ORDER BY created_at DESC LIMIT 1
                """,
                (request.phone, request.code, datetime.now())
            )
            verify_record = cursor.fetchone()

            if not verify_record:
                return LoginResponse(
                    success=False,
                    message="验证码无效或已过期"
                )

            # 标记验证码已使用
            cursor.execute(
                "UPDATE ai_service.verify_codes SET is_used = TRUE WHERE id = %s",
                (verify_record['id'],)
            )

            # 查找或创建用户
            cursor.execute(
                "SELECT * FROM ai_service.users WHERE phone = %s",
                (request.phone,)
            )
            user = cursor.fetchone()

            if not user:
                # 自动创建用户
                username = f"user_{request.phone[-6:]}"
                nickname = f"用户{request.phone[-4:]}"
                password_hash = hash_password(secrets.token_hex(8))

                cursor.execute(
                    """
                    INSERT INTO ai_service.users (username, phone, password_hash, nickname, role)
                    VALUES (%s, %s, %s, %s, 'user')
                    RETURNING *
                    """,
                    (username, request.phone, password_hash, nickname)
                )
                user = cursor.fetchone()

            # 更新最后登录时间
            cursor.execute(
                "UPDATE ai_service.users SET last_login_at = %s WHERE id = %s",
                (datetime.now(), user['id'])
            )

            # 记录登录日志
            cursor.execute(
                """
                INSERT INTO ai_service.login_logs (user_id, login_type, status)
                VALUES (%s, 'sms', 'success')
                """,
                (user['id'],)
            )

        # 生成Token
        token = generate_token(user['id'], user['username'], user['role'])

        return LoginResponse(
            success=True,
            token=token,
            user_id=user['id'],
            username=user['username'],
            nickname=user['nickname'],
            role=user['role']
        )

    except Exception as e:
        logger.error(f"❌ 短信登录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/password", response_model=LoginResponse)
async def password_login(request: PasswordLoginRequest):
    """
    密码登录

    - **username**: 用户名/手机号/邮箱
    - **password**: 密码
    """
    try:
        from common.postgresql_pool import pg_pool

        with pg_pool.get_dict_cursor() as cursor:
            # 查找用户
            cursor.execute(
                """
                SELECT * FROM ai_service.users
                WHERE username = %s OR phone = %s OR email = %s
                """,
                (request.username, request.username, request.username)
            )
            user = cursor.fetchone()

            if not user:
                return LoginResponse(
                    success=False,
                    message="用户不存在"
                )

            # 验证密码
            if not verify_password(request.password, user['password_hash']):
                # 记录失败日志
                cursor.execute(
                    """
                    INSERT INTO ai_service.login_logs (user_id, login_type, status)
                    VALUES (%s, 'password', 'failed')
                    """,
                    (user['id'],)
                )
                return LoginResponse(
                    success=False,
                    message="密码错误"
                )

            # 检查用户是否激活
            if not user['is_active']:
                return LoginResponse(
                    success=False,
                    message="账号已被禁用"
                )

            # 更新最后登录时间
            cursor.execute(
                "UPDATE ai_service.users SET last_login_at = %s WHERE id = %s",
                (datetime.now(), user['id'])
            )

            # 记录登录日志
            cursor.execute(
                """
                INSERT INTO ai_service.login_logs (user_id, login_type, status)
                VALUES (%s, 'password', 'success')
                """,
                (user['id'],)
            )

        # 生成Token
        token = generate_token(user['id'], user['username'], user['role'])

        return LoginResponse(
            success=True,
            token=token,
            user_id=user['id'],
            username=user['username'],
            nickname=user['nickname'],
            role=user['role']
        )

    except Exception as e:
        logger.error(f"❌ 密码登录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """
    用户注册

    - **username**: 用户名
    - **phone**: 手机号
    - **code**: 验证码
    - **password**: 密码
    """
    try:
        from common.postgresql_pool import pg_pool

        with pg_pool.get_dict_cursor() as cursor:
            # 验证验证码
            cursor.execute(
                """
                SELECT id FROM ai_service.verify_codes
                WHERE phone = %s AND code = %s AND purpose = 'register'
                AND is_used = FALSE AND expires_at > %s
                ORDER BY created_at DESC LIMIT 1
                """,
                (request.phone, request.code, datetime.now())
            )
            verify_record = cursor.fetchone()

            if not verify_record:
                return LoginResponse(
                    success=False,
                    message="验证码无效或已过期"
                )

            # 检查用户名是否已存在
            cursor.execute(
                "SELECT id FROM ai_service.users WHERE username = %s",
                (request.username,)
            )
            if cursor.fetchone():
                return LoginResponse(
                    success=False,
                    message="用户名已存在"
                )

            # 检查手机号是否已注册
            cursor.execute(
                "SELECT id FROM ai_service.users WHERE phone = %s",
                (request.phone,)
            )
            if cursor.fetchone():
                return LoginResponse(
                    success=False,
                    message="手机号已注册"
                )

            # 标记验证码已使用
            cursor.execute(
                "UPDATE ai_service.verify_codes SET is_used = TRUE WHERE id = %s",
                (verify_record['id'],)
            )

            # 创建用户
            password_hash = hash_password(request.password)
            nickname = request.nickname or request.username

            cursor.execute(
                """
                INSERT INTO ai_service.users (username, phone, password_hash, nickname, role)
                VALUES (%s, %s, %s, %s, 'user')
                RETURNING *
                """,
                (request.username, request.phone, password_hash, nickname)
            )
            user = cursor.fetchone()

        # 生成Token
        token = generate_token(user['id'], user['username'], user['role'])

        return LoginResponse(
            success=True,
            token=token,
            user_id=user['id'],
            username=user['username'],
            nickname=user['nickname'],
            role=user['role']
        )

    except Exception as e:
        logger.error(f"❌ 注册失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user(token: str):
    """
    获取当前用户信息

    - **token**: JWT Token
    """
    try:
        payload = verify_token(token)
        user_id = payload.get('user_id')

        from common.postgresql_pool import pg_pool

        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                "SELECT id, username, nickname, phone, email, role, avatar FROM ai_service.users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")

            return UserInfo(**user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_token(token: str):
    """
    刷新Token

    - **token**: JWT Token
    """
    try:
        payload = verify_token(token)
        user_id = payload.get('user_id')
        username = payload.get('username')
        role = payload.get('role')

        new_token = generate_token(user_id, username, role)

        return {
            "success": True,
            "token": new_token
        }

    except Exception as e:
        logger.error(f"❌ 刷新Token失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
