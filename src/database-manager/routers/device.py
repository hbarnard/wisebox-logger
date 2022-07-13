
from routers.dependencies import *

@router.post("/device/", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    #db_user = crud.get_device(db, database.mac=device.mac)
    return crud.create_device(db=db,  device = device)


@router.get("/devices/", response_model=List[schemas.Device])
def read_device(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return devices


@router.get("/device/{device_id}", response_model=schemas.Device)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device
    
