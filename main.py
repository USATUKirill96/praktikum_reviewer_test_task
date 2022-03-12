import datetime as dt


class Record:
    # Issue: Здесь и далее в функциях не хватает типизации. Проставлять типы - хорошая практика, которая позволит
    #        легче поддерживать код больших проектов в будущем https://docs.python.org/3/library/typing.html
    def __init__(self, amount, comment, date=''):
        self.amount = amount
        # Suggestion: Из-за порядка условий здесь не очевидно, как задается дата. Можно переписать однострочником
        #             self.date = dt.datetime.strptime(date, '%d.%m.%Y').date()) if date else dt.datetime.now().date()
        self.date = (
            dt.datetime.now().date() if
            not
            date else dt.datetime.strptime(date, '%d.%m.%Y').date())
        self.comment = comment


class Calculator:
    def __init__(self, limit):
        self.limit = limit
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def get_today_stats(self):
        today_stats = 0
        # Issue: тут сразу две проблемы с неймингом:
        #        1. Переопределяется имя, использованное для класса Record.
        #        2. По pep 8 переменные принято называть со строчной буквы.
        #           Программист, изучающий код, подумает что это обращение к классу
        #           https://peps.python.org/pep-0008/#function-and-variable-names
        for Record in self.records:
            # Suggestion: обращение к dt.datetime.now().date() можно вынести из цикла как это сделано на 40 строке.
            #             Это сделает код понятным и более консистентным, сократит количество IO операций.
            if Record.date == dt.datetime.now().date():
                today_stats = today_stats + Record.amount
        return today_stats

    def get_week_stats(self):
        week_stats = 0
        today = dt.datetime.now().date()
        for record in self.records:
            # Suggestion: Здесь можно заменить на более простое.
            #             if 7 > (today - record.date).days >= 0:
            if (
                (today - record.date).days < 7 and
                (today - record.date).days >= 0
            ):
                week_stats += record.amount
        return week_stats


class CaloriesCalculator(Calculator):
    # Issue: документация к функции будет более стандартизованной, если оформить её по Docstring Conventions
    #        https://peps.python.org/pep-0257/
    def get_calories_remained(self):  # Получает остаток калорий на сегодня
        # Issue: Название переменной x не говорит ни о чем. Лучше назвать её тем, что она действительно обозначает
        x = self.limit - self.get_today_stats()
        if x > 0:
            # Issue: Несколько проблем с читаемостью:
            #        1. Здесь не требуется перенос строки.
            #        2. Не стоит использовать бэкслеши для переноса строк.
            #           https://docs.google.com/document/d/1s_FqVkqOASwXK0DkOJZj5RzOm4iWBO5voc_8kenxXbw/edit
            #        3. Пробел в начале второй строки ухудшает восприятие текста. Лучше ставить его после первой.
            return f'Сегодня можно съесть что-нибудь' \
                   f' ещё, но с общей калорийностью не более {x} кКал'
        else:
            # Suggestion: Скобки здесь не нужны, можно просто вернуть строку
            return('Хватит есть!')


class CashCalculator(Calculator):
    # Suggestion:
    #   1. Для операций с деньгами лучше использовать модуль Decimal.
    #      https://zetcode.com/python/decimal/
    #   2. В случае с float незначительные округления в коде могут стать большой проблемой для бухгалтерии.
    USD_RATE = float(60)  # Курс доллар США.
    EURO_RATE = float(70)  # Курс Евро.

    # Issue: Для локальных переменных принято использовать только строчные буквы.
    #        https://peps.python.org/pep-0008/#function-and-variable-names
    # Question: Для чего здесь перенос на другую строку? Если для разделения позиционных и именованных аргументов,
    #           то это, скорее всего, не лучшее решение.
    def get_today_cash_remained(self, currency,
                                USD_RATE=USD_RATE, EURO_RATE=EURO_RATE):

        # Issue: здесь очень запутанный участок кода.
        #        Стоит пересмотреть использование переменных currency_type и currency. Использовать одну переменную.
        currency_type = currency
        cash_remained = self.limit - self.get_today_stats()

        # Suggestion: Для сравнения currency с несколькими значениями можно использовать switch-case
        #             https://datagy.io/python-switch-case/
        if currency == 'usd':
            cash_remained /= USD_RATE
            currency_type = 'USD'
        # Issue: Из-за нарушения консистентности имен, кажется что это другое сравнение.
        #        Хотя сравнивается currency и 'eur'
        elif currency_type == 'eur':
            cash_remained /= EURO_RATE
            # Issue: currency_type использовался для хранения типа, а теперь он содержит форматированное значение.
            #        Буквы и переменные бесплатные, можно завести отдельную переменную под это дело
            currency_type = 'Euro'
        elif currency_type == 'rub':
            # Issue: Кажется, здесь опечатка.
            cash_remained == 1.00
            currency_type = 'руб'
        if cash_remained > 0:
            return (
                # Issue: Операцию округления стоит вынести из f-строки. Это считается плохой практикой.
                #        https://docs.google.com/document/d/1s_FqVkqOASwXK0DkOJZj5RzOm4iWBO5voc_8kenxXbw/edit
                f'На сегодня осталось {round(cash_remained, 2)} '
                f'{currency_type}'
            )
        elif cash_remained == 0:
            # Suggestion: В операторе elif нет необходимости, если в предыдущем if-e был return.
            # Так начинает казаться, что предыдущий оператор сравнения не возвращал результат
            return 'Денег нет, держись'
        elif cash_remained < 0:
            # Issue та же проблема с переносом строки через бэкслеш
            return 'Денег нет, держись:' \
                   ' твой долг - {0:.2f} {1}'.format(-cash_remained,
                                                     currency_type)

    def get_week_stats(self):
        # Issue: Если переопределение метода только возвращает вызов родительского, возможно не стоит его переопределять
        super().get_week_stats()
