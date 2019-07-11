'''Some function which will print something each 10 seconds '''
import time
def time_delay(func, delay=5):
    def wrapper(): 
        time.sleep(delay)
        func()
    return wrapper

@time_delay
def do_it():
    print('Something')
if __name__=="__main__":
    while True:
        do_it()
