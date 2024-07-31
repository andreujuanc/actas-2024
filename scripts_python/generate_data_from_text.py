import os
import re
import pytesseract
import uuid
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from colorama import init, Fore, Style
from datetime import datetime

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

def log_error(image_name, error_text):
    error_log = ErrorLog(
        image_name=image_name,
        error_text=error_text
    )
    session.add(error_log)
    session.commit()

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        # Crop the image from vertical pixels 800 to 1250
        cropped_image = image.crop((0, 700, image.width, 1400))

        # Perform OCR on the cropped image
        text = pytesseract.image_to_string(cropped_image, lang='spa')  # Assuming the text is in Spanish
        
        return text
    except Exception as e:
        log_error(os.path.basename(image_path), str(e))
        return None

def parse_text(text, image_name, i, total_images):
    try:
        data = {
            "pais": "Venezuela",
            "estado": "",
            "municipio": "",
            "parroquia": "",
            "direccion": "",
            "num_electores": ""
        }

        # Normalize the text by replacing potential OCR errors and removing tildes
        text = text.replace('Pals', 'Pais').replace('Páls', 'Pais').replace('Munícipio', 'Municipio').replace('Múnicipio', 'Municipio').replace('Parróguia', 'Parroquia').replace('Parroquía', 'Parroquia').replace('ELECCIÓN PRESMENCIAL', 'ELECCIÓN PRESIDENCIAL')
        text = re.sub(r'[áéíóúÁÉÍÓÚ]', lambda m: {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}[m.group()], text)

        # Define regex patterns for each field
        patterns = {
            "estado": r"Estado\s+(.+)",
            "municipio": r"Municipio\s+(.+)",
            "parroquia": r"Parroquia\s+(.+)",
            "num_colegio": r"(\(?C?\d{8}\)?)",
            "num_electores": r"(\d+)\s+Electores"
        }

        # Extract fields using regex patterns
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                data[field] = match.group(1).strip()

        # Extract address between "parroquia" and "num_colegio"
        address_pattern = r"Parroquia\s+.+?\n(.+?)\n\s*\(?C?\d{8}\)?"
        address_match = re.search(address_pattern, text, re.DOTALL)
        if address_match:
            data["direccion"] = address_match.group(1).replace("\n", " ").strip()

        data["estado"] = data["estado"].split('\n')[0]
        data["municipio"] = data["municipio"].split('\n')[0]
        data["parroquia"] = data["parroquia"].split('\n')[0]

        # Check if we have all required data
        if None in data.values():
            missing_fields = [k for k, v in data.items() if v is None]
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Check if the record exists, if not create it
        vote_record = session.query(RegisterVote).filter_by(image_name=image_name).first()
        if vote_record:
            vote_record.pais = data.get('pais')
            vote_record.estado = data.get('estado')
            vote_record.municipio = data.get('municipio')
            vote_record.parroquia = data.get('parroquia')
            vote_record.escuela = data.get('escuela')
            vote_record.direccion = data.get('direccion')
            vote_record.numero_colegio = data.get('numero_colegio')
            vote_record.num_electores = data.get('num_electores')
        else:
            vote_record = RegisterVote(
                register_num=image_name,
                maduro=0,  # default values
                luis_martinez=0,
                javier_bertucci=0,
                jose_brito=0,
                antonio_ecarri=0,
                claudio_fermin=0,
                daniel_ceballos=0,
                edmundo_gonzalez=0,
                enrique_marquez=0,
                benjamin_rausseo=0,
                image_name=image_name,
                pais=data.get('pais'),
                estado=data.get('estado'),
                municipio=data.get('municipio'),
                parroquia=data.get('parroquia'),
                escuela=data.get('escuela'),
                direccion=data.get('direccion'),
                numero_colegio=data.get('numero_colegio'),
                num_electores=data.get('num_electores')
            )
            session.add(vote_record)

        session.commit()
        print(Fore.GREEN + f"Image {i+1} of {total_images}: processed")
    except Exception as e:
        log_error(image_name, str(e))
        print(Fore.RED + f"Image {i+1} of {total_images}: error - {e}")

def process_images(directory):
    image_files = [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
    total_images = len(image_files)
    
    for i, filename in enumerate(image_files):
        image_path = os.path.join(directory, filename)
        text = extract_text_from_image(image_path)
        if text:
            parse_text(text, filename, i, total_images)
        else:
            log_error(filename, "Failed to extract text from image")
            print(Fore.RED + f"Image {i+1} of {total_images}: error - Failed to extract text from image")


# Specify the directory containing the images
image_directory = '../actas'
process_images(image_directory)
