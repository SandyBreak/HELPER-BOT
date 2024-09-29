# -*- coding: UTF-8 -*-

class TelegramAddressNotValidError(Exception):
    """
    Пустой адрес телеграмм аккаунта пользователя
    """
    pass

 
class DataInputError(Exception):
	"""
	Ввод данных неправильного формата
	"""
	pass


class LongTimeInputError(Exception):
	"""
	Ввод времени которое пересекается с другими конференциями
	"""
	pass


class CreateMeetingError(Exception):
	"""
	Ошибка создания конференции
	"""
	pass


class UserNotRegError(Exception):
    """
    Ошибка из-за того, что пользователь не зарегистиррован в боте
    """
    pass


class RegistrationError(Exception):
    """
    Ошибка регистрации
    """
    pass


class EpmtyTableError(Exception):
    """
    Ошибка пустой таблицы
    """
    pass