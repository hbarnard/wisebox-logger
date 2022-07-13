# get item by id, list of items and create item, no delete at present


from sqlalchemy.orm import Session
from internal import schemas, database

def get_device(db: Session, device_id: int):
    return db.query(database.Device).filter(database.Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Device).offset(skip).limit(limit).all()


def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = database.Device(mac= device.mac, lat = device.lat, lng = device.lng, title = device.title, place = device.place)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_bucketrssi(db: Session, bucketrssi_id: int):
    return db.query(database.BucketRssi).filter(database.BucketRssi.id == bucketrssi_id).first()


def get_bucketrssis(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.BucketRssi).offset(skip).limit(limit).all()


def create_bucketrssi(db: Session, bucketrssi: schemas.BucketRssiCreate):
    db_bucketrssi = database.BucketRssi(rssi=bucketrssi.rssi)
    db.add(db_bucketrssi)
    db.commit()
    db.refresh(db_bucketrssi)
    return db_bucketrssi


def get_bucket(db: Session, bucket_id: int):
    return db.query(database.Bucket).filter(database.Bucket.id == bucket_id).first()


def get_buckets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Bucket).offset(skip).limit(limit).all()
    
'''    
    id : int 
    start_time : str
    interval: int
    frequency: int
    count : int
'''


def create_bucket(db: Session, bucket: schemas.BucketCreate):
    db_bucket = database.Bucket(start_time=bucket.start_time)
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket


def get_apikey(db: Session, apikey_id: int):
    return db.query(database.ApiKey).filter(database.ApiKey.id == apikey_id).first()


def get_apikeys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.ApiKey).offset(skip).limit(limit).all()


def create_apikey(db: Session, apikey: schemas.ApiKeyCreate):
    db_apikey = database.ApiKey(key=apikey.key)
    db.add(db_apikey)
    db.commit()
    db.refresh(db_apikey)
    return db_apikey


def get_bucketmetadata(db: Session, bucketmetadata_id: int):
    return db.query(database.BucketMetadata).filter(database.BucketMetadata.id == bucketmetadata_id).first()


def get_bucketmetadatas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.BucketMetadata).offset(skip).limit(limit).all()


def create_bucketmetadata(db: Session, bucketmetadata: schemas.BucketMetadataCreate):
    db_bucketmetadata = database.BucketMetadata(name=bucketmetadata.name)
    db.add(db_bucketmetadata)
    db.commit()
    db.refresh(db_bucketmetadata)
    return db_bucketmetadata


def get_organisation(db: Session, organisation_id: int):
    return db.query(database.Organisation).filter(database.Organisation.id == organisation_id).first()


def get_organisations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Organisation).offset(skip).limit(limit).all()


def create_organisation(db: Session, organisation: schemas.OrganisationCreate):
    db_organisation = database.Organisation(name=organisation.name)
    db.add(db_organisation)
    db.commit()
    db.refresh(db_organisation)
    return db_organisation


def get_timezone(db: Session, timezone_id: int):
    return db.query(database.Timezone).filter(database.Timezone.id == timezone_id).first()


def get_timezones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Timezone).offset(skip).limit(limit).all()


def create_timezone(db: Session, timezone: schemas.TimezoneCreate):
    db_timezone = database.Timezone(name=timezone.name)
    db.add(db_timezone)
    db.commit()
    db.refresh(db_timezone)
    return db_timezone

