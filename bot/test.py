import time

def hello():
    start = time.perf_counter()
    print("koo")
    print("koo")
    print("koo")
    print("koo")
    print("koo")
    print("koo")

    end =  time.perf_counter()
    print(end-start)

    

hello()