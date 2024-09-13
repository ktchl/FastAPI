from fastapi import FastAPI
import pandas as pd 
from pydantic import BaseModel
import random
from fastapi import Header
from fastapi import HTTPException, Depends
import base64
from fastapi.security import HTTPBasic, HTTPBasicCredentials

api = FastAPI()

df = pd.read_csv("questions.csv")
df = df.replace({float('nan'): None})

identifiants = [("admin", "4dm1N"), ("kenny","123")]
identifiants_encoded = []
#username = "kenny"
#password = "123"

for element in identifiants:
    encoder = f"{element[0]}:{element[1]}"
    encoded_credentials = base64.b64encode(encoder.encode()).decode()
    identifiants_encoded.append(encoded_credentials)


print(identifiants_encoded)

@api.get('/')
def get_index():
    return {
        'data': dict(df)
    }

@api.get('/verify')
def get_index():
    return {
        "L'application est fonctionnelle"
    }


subject = list(set(dict(df).get("subject")))
use = list(set(dict(df).get("use")))
nbr_question = [5,10,20]

class Quiz(BaseModel):
    test_type: str
    categories: str
    nbr_questions : int

@api.post('/generate_quiz/')
def post_item(quiz: Quiz, authorization = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization manquante")

    try:
      
        username, password = authorization.split()

        if username.lower() != "basic":
            raise HTTPException(status_code=401, detail="Authentification invalide")

        decoded_credentials = base64.b64decode(password).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)

        if (username, password) not in identifiants:
            raise HTTPException(status_code=401, detail="Authentification incorrecte")
        
    except ValueError:

        raise HTTPException(status_code=400, detail="Invalid authorization format")


    if quiz.nbr_questions not in nbr_question:

        raise HTTPException(status_code=400, detail="Incorrecte, entrez valeur 5, 10 ou 20")

    else:
        if(quiz.nbr_questions > len(df[(df["subject"] == quiz.test_type) & (df["use"] == quiz.categories)])):

            return df[(df["subject"] == quiz.test_type) & (df["use"] == quiz.categories)].sample(len(df[(df["subject"] == quiz.test_type) & (df["use"] == quiz.categories)]))


        return df[(df["subject"] == quiz.test_type) & (df["use"] == quiz.categories)].sample(quiz.nbr_questions)


class CreateQuestions(BaseModel):
    admin_username: str
    admin_password: str
    question: str
    subject: str
    correct: str
    use: str
    responseA: str
    responseB: str
    responseC: str
    responseD: str
    
    

@api.post('/create_question/')
def post_item(colonnes: CreateQuestions):
    
    questions = []

    if (colonnes.admin_username, colonnes.admin_password) in (identifiants):

        questions.append(colonnes.question)
        questions.append(colonnes.subject)
        questions.append(colonnes.correct)
        questions.append(colonnes.use)
        questions.append(colonnes.responseA)
        questions.append(colonnes.responseB)
        questions.append(colonnes.responseC)
        questions.append(colonnes.responseD)
        questions.append(None)
        df.loc[len(df)] = questions

    return {"message": "Question créée avec succès."}




