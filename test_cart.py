from django.test import Client
c = Client()
try:
    res = c.post('/cart/add/4/', {'quantity': 1})
    if res.status_code == 302:
        print("Redirected to:", res.url)
        res = c.get(res.url)
    print("Final status:", res.status_code)
    if res.status_code == 500:
        print("ERROR 500!")
        import rfc3987 # arbitrary to fail or print(res.content)
        # We want to see the error type inside the HTML
        content = res.content.decode()
        import re
        m = re.search(r"Exception Type:.*?<th>Exception Value:</th>\s*<td><pre>(.*?)</pre>", content, re.DOTALL)
        if m:
            print(m.group(1))
        else:
            m = re.search(r"<title>(.*?)</title>", content)
            print("Title:", m.group(1) if m else "Unknown Error")
except Exception as e:
    import traceback
    traceback.print_exc()
