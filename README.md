# GetFavicon library 📦

I've developed a straightforward Python library called **getFavicon** that offers a convenient way to retrieve favicons from a given website URL. When you provide a website URL to the scanner, it will return an array containing links to the favicons associated with that website.

### scan_async - fast async scanner

Here's an example of how to use `scan_async`:

```
favicons = scan_async('https://www.google.com')
```

`scan_async` in **FastAPI**:

```
from fastapi import FastAPI
from pydantic import HttpUrl
from getFavicon import scan_async

app = FastAPI()

@app.get("/")
async def serve_main(domain_url: HttpUrl):
    return favicons = await scan_async(domain_url)
```

### scan - sync scanner

If you require non-async scanner, consider using `scan`:

```
from getFavicon import scan
favicons = scan('https://www.google.com')
```

### timeout

You can specify a timeout duration (in seconds) for both the **scan** and **scan_async** functions, with the default `timeout` set to **2 seconds**.

```
favicons = scan('https://www.google.com', timeout = 10)
```

### first_only - retrieve only one favicon

You can also use the `first_only = True` flag to retrieve only the first favicon found. It's worth noting that using this flag will have no impact on the behavior of the scanner_async since it operates asynchronously.

```
favicons = scan('https://www.google.com', first_only = True)
```

### Response example

<img src="https://i.imgur.com/xAtm6pU.png"/>

test
test
test
test
test
test
test
test
test
test
test