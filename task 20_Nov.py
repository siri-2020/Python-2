import time

class Timer:
    def __init__(self):
        pass

    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.end_time = time.time()
        print(self.end_time - self.start_time)
        return True

def fibo(n):
    if n == 1 or n == 2:
        return 1
    else:
        return fibo(n - 1) + fibo(n - 2)

with Timer() as t:
    fibo(35)