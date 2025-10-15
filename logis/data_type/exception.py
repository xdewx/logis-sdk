class UserFacingException(Exception):
    """
    用户面向的异常类，用于在前端展示异常信息
    """

    def __init__(self, message: str | None = None):
        super().__init__(message)
