#FIXME: there's a problem with Bucket and the update to the database currently, validation
#FIXME: Since we're now Mariadb can we deal cleanly with geo datatypes here: https://pypi.org/project/geojson-pydantic/ ?
#FIXME: condecimal is an old fix but decimal.Decimal doesn't seem to work?

from pydantic import BaseModel
from datetime import time 
from typing import Optional
from pydantic import condecimal

# Device

class DeviceBase(BaseModel):
    mac: str
    lat: condecimal(max_digits=8, decimal_places=6) 
    lng: condecimal(max_digits=9, decimal_places=6) 
    title: str
    place: str 

class DeviceCreate(DeviceBase):
    mac: str
    lat: condecimal(max_digits=8, decimal_places=6)
    lng: condecimal(max_digits=9, decimal_places=6)
    title: str
    place: str 

class Device(DeviceBase):
    id: int
    mac: str
    lat: condecimal(max_digits=8, decimal_places=6) 
    lng: condecimal(max_digits=9, decimal_places=6)
    title: str
    place: str 
    class Config:
        orm_mode = True


# Bucket Rssi

class BucketRssiBase(BaseModel):
    rssi : int

class BucketRssiCreate(BucketRssiBase):
    rssi : int

class BucketRssi(BucketRssiBase):
    id : int 
    rssi : int
    class Config:
        orm_mode = True

#FIXME: Bucket, Optional should cure validation problem, but not sure it does?

class BucketBase(BaseModel):
    start_time : time
    interval: Optional[int]
    frequency: Optional[int]
    count : Optional[int]


class BucketCreate(BucketBase):
    start_time : time
    interval: int
    frequency: int
    count : int

class Bucket(BucketBase):
    id : int 
    start_time : time
    interval: int
    frequency: int
    count : int
    class Config:
        orm_mode = True

# Api Key

class ApiKeyBase(BaseModel):
    key : str 


class ApiKeyCreate(ApiKeyBase):
    key : str 

class ApiKey(ApiKeyBase):
    id : int 
    key : str 
    class Config:
        orm_mode = True

# Bucket Metadata

class BucketMetadataBase(BaseModel):
    id ; int 
    name: str
    value:  str

class BucketMetadataCreate(BucketMetadataBase):
    id ; int 
    name: str
    value:  str

class BucketMetadata(BucketMetadataBase):
    id ; int 
    name: str
    value:  str
    class Config:
        orm_mode = True

# Organisation

class OrganisationBase(BaseModel):
    name: str

class OrganisationCreate(OrganisationBase):
    name: str

class Organisation(OrganisationBase):
    id: int
    name: str
    class Config:
        orm_mode = True
# Timezone

class TimezoneBase(BaseModel):
    name : str

class TimezoneCreate(TimezoneBase):
    name : str

class Timezone(TimezoneBase):
    id : int 
    name : str
    class Config:
        orm_mode = True


