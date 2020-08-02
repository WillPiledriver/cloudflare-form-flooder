import requests
from essential_generators import DocumentGenerator
import cloudscraper
import random
import json
import string
from multiprocessing.dummy import Pool


def get_all_proxies():
    raw = requests.get("https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=elite").text
    return raw.split("\r\n")


def get_proxies():
    f = open("good_proxies.json", "r")
    j = json.load(f)
    f.close()
    return j


def get_random_string(length):
    letters = "abcd" + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def post_proxy(url, p, request_data, proxy_list, cloudflare=None):
    if p not in proxy_list:
        return (False, None)
    try:
        if cloudflare is not None:
            x = cloudflare.post(url)
        else:
            x = requests.post(url, data=request_data, proxies={"http": p, "https": p}, timeout=10)
        x.proxy = p
        return (x.status_code==requests.codes.ok, x)

    except requests.exceptions.ReadTimeout:
        return(False, None)
    except requests.exceptions.ConnectTimeout:
        if p in proxy_list:
            proxy_list.remove(p)
            print("Connection too slow. Removed.")
        return ("remove", None)
    except requests.exceptions.ProxyError as e:
        if p in proxy_list:
            proxy_list.remove(p)
            print(f'Problem with proxy {proxy}. Removing proxy from the pool.\n {e}')
        return ("remove", None)
    except Exception as e:
        print(f'Something strange happened {e}')
        return (False, None)


def cloud_proxy(url, proxy):
    try:
        x = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=10)
        x.proxy = proxy
    except Exception as e:
        x = None
    if x is not None:
        result = cloudscraper.create_scraper(x)
        result.proxy = proxy
    else:
        return None
    return result


if __name__ == "__main__":
    pool_size = 20
    proxy_index = 0
    url = "https://hyperxoffensive.com/auth.php"
    url = "https://cybercupauth.com/auth.php"
    cloudflare = True
    proxies = get_all_proxies()
    gen = DocumentGenerator()
    server_errors = list()

    scraper_sessions = dict()

    i = 0
    while i < len(proxies):
        thread_pool = Pool(pool_size)
        futures = list()
        for x in range(pool_size):
            if i >= len(proxies):
                break
            futures.append(thread_pool.apply_async(cloud_proxy, [url, proxies[i]]))
            i += 1
        clean = [f.get() for f in futures]
        for c in clean:
            if c is not None:
                scraper_sessions[c.proxy] = c

        if len(scraper_sessions) > 0:
            print(len(scraper_sessions))




    c = 0
    while True:
        thread_pool = Pool(pool_size)
        futures = list()
        r = random.choice([gen.email(), gen.word()+gen.word(), gen.name()+gen.word()+gen.word()])
        #r = get_random_string(random.randrange(120, 500))
        request_data = {"doAuth": "1", "login": r.replace(" ", ""), "password": gen.word()+gen.word()+str(gen.small_int())}
        for i in range(pool_size):
            if proxy_index < len(proxies):
                proxy = proxies[proxy_index]
                proxy_index += 1
            else:
                proxy = proxies[0]
                proxy_index = 1
            if proxy in scraper_sessions:
                futures.append(thread_pool.apply_async(post_proxy, [url, proxy, request_data, proxies, (None, scraper_sessions[proxy])[cloudflare]]))


        clean = [f.get() for f in futures]
        for x in clean:
            if x[0] == True:
                pass
            elif x[0] == "remove":
                continue
            else:
                if x[1] is not None:
                    if x[1].status_code == 500:
                        server_errors.append(x[1].proxy)
                        print(f'Server error detected using proxy {x[1].proxy}')

                    print(f'Status code of website: {x[1].status_code} // {server_errors[:1]}')
                continue

            c += 1
            if c % 5 == 0:
                print(f'{c} requests have been made.')
