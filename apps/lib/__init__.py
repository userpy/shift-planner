class AppError(Exception):
    def __init__(self, message):
        self.message = message


class MultiplayerError(AppError):
    def __init__(self):
        super(MultiplayerError, self).__init__({"name": "multiplayer"})


class UserDisplayError(AppError):
    """
    Класс ошибок для показа сообщения пользователю
    """
    pass
