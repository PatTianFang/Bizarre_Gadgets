import math

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y

def power(x, y):
    return x ** y

def square_root(x):
    if x < 0:
        raise ValueError("Cannot calculate square root of a negative number.")
    return math.sqrt(x)

def log(x, base=10):
    if x <= 0:
        raise ValueError("Logarithm undefined for non-positive values.")
    return math.log(x, base)

def sin(x):
    return math.sin(math.radians(x))

def cos(x):
    return math.cos(math.radians(x))

def tan(x):
    return math.tan(math.radians(x))

def factorial(x):
    if x < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
    return math.factorial(x)

def exp(x):
    return math.exp(x)

def mod(x, y):
    return x % y

def radians(x):
    return math.radians(x)

def degrees(x):
    return math.degrees(x)

def abs_value(x):
    return abs(x)