# GetFavicon package 📦
[Pypi.org package](https://pypi.org/project/getFavicon/) 
<br/>
GetFavicon is a simple python tool to grab site's favicons. While working on favicon tool which was using [favicon](https://pypi.org/project/favicon/) python package, I've got enough inspiration to create mine due to bugs of this package. While I was sure I can create a better and faster package, I've managed to create a package with more options but speed is not much better. While original favicon's speed is around 0.6s avg, mine is 0.4s-0.5s. 


#### Use example:
```
from getFavicon import scan
from fastapi import FastAPI
from pydantic import HttpUrl
import asyncio

app = FastAPI()
@app.get("/")
async def serve_main(domain_url: HttpUrl):
    return await scan(domain_url)
```

#### Response example (fastapi + getFavicon package):
<img src="https://i.imgur.com/JuWLbsd.png"/>
