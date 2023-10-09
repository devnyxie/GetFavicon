# GetFavicon library 📦

I've developed a straightforward Python library called "getFavicon" that offers a convenient way to retrieve favicons from a given website URL. When you provide a website URL to the scanner, it will return an array containing links to the favicons associated with that website.

Here's an example of how to use it:

```
from getFavicon import scan
favicons = scan('https://www.google.com')
```

If you require an asynchronous scanner, consider utilizing the **scan_async** function:

```
from fastapi import FastAPI
from pydantic import HttpUrl
from getFavicon import scan_async

app = FastAPI()

@app.get("/")
async def serve_main(domain_url: HttpUrl):
    return favicons = scan_async(domain_url)
```

#### Response example (fastapi + getFavicon):

<img src="https://i.imgur.com/JuWLbsd.png"/>

<br/>

#### Installing Locally for Contributions:

1. `pip install virtualenv`
2. `python3 -m venv myenv`
3. `source venv/bin/activate`
   (On windows, use: `myenv\Scripts\activate`)
4. `pip install -e .`
5. `pip install -r requirements.txt`
