import time

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def consume_with_timeout(generator, timeout_sec):
    start = time.time()
    for value in generator:
        print(value)
        if time.time() - start > timeout_sec:
            print("⏱ Timeout reached")
            break
