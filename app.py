from flask import Flask
from flask_vite import Vite


app = Flask("vite")
vite = Vite(app)
