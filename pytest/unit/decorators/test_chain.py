import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.chain import chain


class Chainable:
    def __init__(self, value):
        self.value = value

    def chain(self):
        return self.value * 2


class NonChainable:
    def __init__(self, value):
        self.value = value


@chain
def return_chainable():
    return Chainable(5)


@chain
def return_non_chainable():
    return NonChainable(5)


@chain
def return_value():
    return 5


@chain
def return_chainable_with_exception():
    class ChainableWithException:
        def chain(self):
            raise ValueError("Chain method error")

    return ChainableWithException()


def test_chain_method_called() -> None:

    """
    Test case 1: Chain method is called on the result.
    """
    result = return_chainable()
    assert result == 10  # Chain method doubles the value


def test_chain_method_not_called() -> None:

    """
    Test case 2: Chain method is not called on the result.
    """
    result = return_non_chainable()
    assert result.value == 5  # Chain method does not exist


def test_no_chain_method() -> None:

    """
    Test case 3: No chain method on the result.
    """
    result = return_value()
    assert result == 5  # No chain method to call


def test_chain_method_with_kwargs() -> None:

    """
    Test case 4: Chain method with keyword arguments.
    """

    class ChainableWithKwargs:
        def __init__(self, value):
            self.value = value

        def chain(self, multiplier=2):
            return self.value * multiplier

    @chain
    def return_chainable_with_kwargs():
        return ChainableWithKwargs(5)

    result = return_chainable_with_kwargs()
    assert result == 10  # Default multiplier is 2


def test_chain_method_with_args() -> None:

    """
    Test case 5: Chain method with positional arguments.
    """

    class ChainableWithArgs:
        def __init__(self, value):
            self.value = value

        def chain(self, multiplier):
            return self.value * multiplier

    @chain
    def return_chainable_with_args():
        return ChainableWithArgs(5)

    result = return_chainable_with_args()
    assert isinstance(result, ChainableWithArgs)
    assert result.value == 5  # chain is not called because required args are missing


def test_chain_method_with_args_and_kwargs() -> None:

    """
    Test case 6: Chain method with positional and keyword arguments.
    """

    class ChainableWithArgsAndKwargs:
        def __init__(self, value):
            self.value = value

        def chain(self, multiplier, addend=0):
            return self.value * multiplier + addend

    @chain
    def return_chainable_with_args_and_kwargs():
        return ChainableWithArgsAndKwargs(5)

    result = return_chainable_with_args_and_kwargs()
    assert isinstance(result, ChainableWithArgsAndKwargs)
    assert result.value == 5  # chain is not called when required args are missing


def test_chain_method_with_no_args() -> None:

    """
    Test case 7: Chain method with no arguments.
    """

    class ChainableWithNoArgs:
        def __init__(self, value):
            self.value = value

        def chain(self):
            return self.value * 2

    @chain
    def return_chainable_with_no_args():
        return ChainableWithNoArgs(5)

    result = return_chainable_with_no_args()
    assert result == 10  # No arguments are passed


def test_chain_method_raises_exception() -> None:

    """
    Test case 8: Chain method raises an exception.
    """
    with pytest.raises(
        RuntimeError,
        match="Error calling 'chain' method on result of return_chainable_with_exception: Chain method error",
    ):
        return_chainable_with_exception()


def test_chain_method_with_custom_exception() -> None:

    """
    Test case 9: Chain method raises a custom exception.
    """

    class CustomException(Exception):
        pass

    class ChainableWithCustomException:
        def chain(self):
            raise CustomException("Custom chain method error")

    @chain
    def return_chainable_with_custom_exception():
        return ChainableWithCustomException()

    with pytest.raises(
        RuntimeError,
        match="Error calling 'chain' method on result of return_chainable_with_custom_exception: Custom chain method error",
    ):
        return_chainable_with_custom_exception()
