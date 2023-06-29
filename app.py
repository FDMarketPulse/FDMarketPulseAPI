#!/usr/bin/env python
import uvicorn

from application import create_app

app = create_app(debug=True)

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True, root_path="/api")
    # uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True, root_path="/api", ssl_keyfile="private.key",
    #             ssl_certfile="certificate.crt")
