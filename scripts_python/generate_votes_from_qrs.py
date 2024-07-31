import os
import cv2
import pyzbar.pyzbar as pyzbar
import re
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Database setup
Base = declarative_base()

class RegisterVote(Base):
    __tablename__ = 'actas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    register_num = Column(String, nullable=False)
    maduro = Column(Integer, nullable=False)
    luis_martinez = Column(Integer, nullable=False)
    javier_bertucci = Column(Integer, nullable=False)
    jose_brito = Column(Integer, nullable=False)
    antonio_ecarri = Column(Integer, nullable=False)
    claudio_fermin = Column(Integer, nullable=False)
    daniel_ceballos = Column(Integer, nullable=False)
    edmundo_gonzalez = Column(Integer, nullable=False)
    enrique_marquez = Column(Integer, nullable=False)
    benjamin_rausseo = Column(Integer, nullable=False)
    image_name = Column(String, unique=True, nullable=False)
    pais = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    municipio = Column(String, nullable=True)
    parroquia = Column(String, nullable=True)
    escuela = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    numero_colegio = Column(String, nullable=True)
    num_electores = Column(Integer, nullable=True)

class ErrorLog(Base):
    __tablename__ = 'error_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_name = Column(String, nullable=False)
    error_text = Column(String, nullable=False)
    time = Column(DateTime, default=datetime.utcnow)

# Change the DATABASE_URL to your database connection string if not using SQLite
DATABASE_URL = "sqlite:///votes.db"

# Create an engine that stores data in the local directory's votes.db file.
engine = create_engine(DATABASE_URL)

# Create all tables in the engine. This is equivalent to "Create Table" statements in raw SQL.
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

def sum_array(values):
    return sum(map(int, values))

def process_input(input_string, image_name):
    pattern = r'^(\d+\.\d+\.\d+\.\d+)\!(\d+(,\d+)*)\!(\d+)\!(\d+)$'
    matches = re.match(pattern, input_string)
    if not matches:
        raise ValueError("Input string has an invalid format.")
    
    acta_number = matches.group(1)
    votes_values = matches.group(2).split(',')

    maduro_values = votes_values[0:13]
    luis_martinez_values = votes_values[13:19]
    javier_bertucci_value = votes_values[19]
    jose_brito_values = votes_values[20:24]
    antonio_ecarri_values = votes_values[24:30]
    claudio_fermin_value = votes_values[30]
    daniel_ceballos_values = votes_values[31:33]
    edmundo_gonzalez_values = votes_values[33:36]
    enrique_marquez_value = votes_values[36]
    benjamin_rausseo_value = votes_values[37]

    if session.query(RegisterVote).filter_by(register_num=acta_number).first():
        raise ValueError(f'Acta {acta_number} already exists in the database.')

    register_vote = RegisterVote(
        register_num=acta_number,
        maduro=sum_array(maduro_values),
        luis_martinez=sum_array(luis_martinez_values),
        javier_bertucci=int(javier_bertucci_value),
        jose_brito=sum_array(jose_brito_values),
        antonio_ecarri=sum_array(antonio_ecarri_values),
        claudio_fermin=int(claudio_fermin_value),
        daniel_ceballos=sum_array(daniel_ceballos_values),
        edmundo_gonzalez=sum_array(edmundo_gonzalez_values),
        enrique_marquez=int(enrique_marquez_value),
        benjamin_rausseo=int(benjamin_rausseo_value),
        image_name=image_name
    )

    session.add(register_vote)
    session.commit()

def save_error(image_name, error_text):
    error_log = ErrorLog(
        image_name=image_name,
        error_text=error_text
    )
    session.add(error_log)
    session.commit()

def read_qr_from_image(image_path):
    image = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Increase contrast
    enhanced = cv2.addWeighted(blur, 1.5, gray, -0.5, 0)
    
    # Resize image if needed
    scale_percent = 150  # Percent of original size
    width = int(enhanced.shape[1] * scale_percent / 100)
    height = int(enhanced.shape[0] * scale_percent / 100)
    resized = cv2.resize(enhanced, (width, height), interpolation=cv2.INTER_LINEAR)
    
    decoded_objects = pyzbar.decode(resized)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return None

def process_images(directory):
    image_files = [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(image_files)
    
    for i, filename in enumerate(image_files):
        image_path = os.path.join(directory, filename)
        qr_content = read_qr_from_image(image_path)
        if qr_content:
            try:
                process_input(qr_content, filename)
                print(Fore.GREEN + f"Image {i+1} of {total_images}: processed")
            except ValueError as e:
                print(Fore.RED + f"Image {i+1} of {total_images}: error - {e}")
                save_error(filename, str(e))
        else:
            error_message = "No QR code found"
            print(Fore.RED + f"Image {i+1} of {total_images}: error - {error_message}")
            save_error(filename, error_message)

# Specify the directory containing the images
image_directory = '../actas'
process_images(image_directory)
