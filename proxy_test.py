import requests
from multiprocessing.dummy import Pool
import json

pool_size = 50
thread_pool = Pool(pool_size)


def get_proxies():
    f = open("all_elite.txt", "r")
    return f.read().split("\n").remove("")


def test_proxy(url, p):
    if p == "":
        return (False, p)
    try:
        r = requests.get(url,proxies={"http": p, "https": p}, timeout=10)
        return (r.status_code==requests.codes.ok, p)
    except:
        return (False, p)


if __name__ == "__main__":
    proxies = get_proxies()
    proxy_pool = proxies
    good_proxies = list()
    url = 'https://hyperxoffensive.com/auth.php'
    i = 0
    while i < len(proxies):
        thread_pool = Pool(pool_size)
        futures = []
        for x in range(pool_size):
            if i >= len(proxy_pool):
                break
            proxy = proxy_pool[i]
            i += 1
            futures.append(thread_pool.apply_async(test_proxy, [url, proxy]))
        clean = [f.get()[1] for f in futures if f.get()[0]]
        if len(clean) > 0:
            print(clean)
            good_proxies += clean

    with open("good_proxies.json", "w") as f:
        f.write(json.dumps(good_proxies))
