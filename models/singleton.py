from typing import ClassVar


class Singleton(type):
    """A metaclass that returns the singleton instance. Can be used universally and verified using the id() method.

    To make a class a singleton class, simply use this singleton class as a metaclass:
    MyClass(metaclass=Singleton):
        ...
    """

    _instances: ClassVar = {}  # type: ignore

    def __call__(cls, *args, **kwargs):  # noqa: ANN204, ANN002, ANN003
        """Override the default 'call'-method, whenever a class is instantiated.

        Args:
            *args (): Arguments to be used for the constructor of the class.
            **kwargs ():  Keyword arguments to be used for the constructor of the class.

        Returns:
            An instance of the class.
        """
        if cls not in cls._instances:  # we have not built an instance before, so create one now.
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:  # we already have an instance, so return it
            instance = cls._instances[cls]

        return instance
