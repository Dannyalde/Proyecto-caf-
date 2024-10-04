
import mysql.connector
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url



def conexion_DB():
    
    connection = mysql.connector.connect(
        host='localhost',
        database='dev_color_cafe',
        user='root',
        password='1009'
    )

    return connection


def conexion_cloudinary():

# Configuration       
    cloudinary.config( 
    cloud_name = "dz3xltmzm", 
    api_key = "129854472215897", 
    api_secret = "Khi_zk8hjkV5fCyyZY8nsy7qEDw", # Click 'View API Keys' above to copy your API secret
    secure=True
)