import datetime
import colorama

colorama.init()


class Logger:
    @classmethod
    def send_log(cls, message, severity):
        print(f"[{colorama.Fore.CYAN}{str(datetime.datetime.now())}{colorama.Fore.LIGHTWHITE_EX}] {severity} {message}{colorama.Fore.LIGHTWHITE_EX}")

    @classmethod
    def log(cls, message):
        cls.send_log(message, colorama.Fore.LIGHTGREEN_EX + "INFO" + colorama.Fore.LIGHTWHITE_EX)

    @classmethod
    def warn(cls, message):
        cls.send_log(message, colorama.Fore.LIGHTYELLOW_EX + "WARN" + colorama.Fore.LIGHTWHITE_EX)

    @classmethod
    def error(cls, message):
        cls.send_log(message, colorama.Fore.LIGHTRED_EX + "ERROR" + colorama.Fore.RED)
