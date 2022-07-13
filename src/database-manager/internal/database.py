from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

#FIXME: need to move user to less privileged user, problem with mariadb setup 

SQLALCHEMY_DATABASE_URL = DATABASE_URL = 'mysql://root:bryana@localhost/wisebox'
# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = automap_base()

# reflect the tables in the database
Base.prepare(autoload_with=engine, reflect=True)


# mapped classes are now created with names by default
# matching that of the table name.

ApiKey = Base.classes.ApiKey
Bucket = Base.classes.Bucket
BucketMetadata = Base.classes.BucketMetadata
BucketRssi = Base.classes.BucketRssi
Device = Base.classes.Device
Organisation = Base.classes.Organisation
Timezone = Base.classes.Timezone







