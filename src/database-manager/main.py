
# database manager for mariadb database that emulates the original postgres django db

# mainly based on this: https://fastapi.tiangolo.com/tutorial/sql-databases/
# lots of warnings on startup due to Duplicate ID: https://github.com/tiangolo/fastapi/issues/4740

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request

#from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


from internal.database import  Base, engine
from routers import apikey, device, bucket, bucketrssi, bucketmetadata, organisation, timezone

from starlette.convertors import Convertor, register_url_convertor

from os.path import dirname, basename, isfile, join
import glob

Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

# can do better than this, later...

app.include_router(device.router)
app.include_router(apikey.router)
app.include_router(bucket.router)
app.include_router(bucketrssi.router)
app.include_router(bucketmetadata.router)
app.include_router(organisation.router)
app.include_router(timezone.router)







