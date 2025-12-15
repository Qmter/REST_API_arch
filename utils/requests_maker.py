import requests

class ApiRequests:

    @staticmethod
    def get_request(url, endpoint, **kwargs):
        """Унифицироанный метод отправки GET-запроса.
            В качестве аргументов принимается endpoint
            и словарь соответствующий типу:
            {имя_переменной: значение_переменной}"""
        request_url = url + f"{endpoint}"

        # Объявление arguments = None, при отсутствии аргумента
        if "arguments" not in kwargs:
            kwargs["arguments"] = None

        # Строение ссылки запроса при наличии arguments
        if kwargs["arguments"] is not None:
            arguments = kwargs["arguments"]
            request_url += "?"

            for key, value in arguments.items():
                request_url += str(key) + "=" + str(value) + "&"

            request_url = request_url[:-1]

        return Http_methods.get(request_url)