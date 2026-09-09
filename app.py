from flask import Flask, render_template, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/convertir", methods=["POST"])
def convertir():

    fichier = request.files.get("video")
    qualite = request.form.get("qualite", "192k")

    if not fichier:
        return "Aucune vidéo sélectionnée.", 400

    nom_unique = str(uuid.uuid4())

    extension = os.path.splitext(fichier.filename)[1].lower()

    video_path = os.path.join(
        UPLOAD_FOLDER,
        nom_unique + extension
    )

    audio_path = os.path.join(
        OUTPUT_FOLDER,
        nom_unique + ".mp3"
    )

    fichier.save(video_path)

    commande = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-codec:a", "libmp3lame",
        "-b:a", qualite,
        "-y",
        audio_path
    ]

    try:
        resultat = subprocess.run(
            commande,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if resultat.returncode != 0 or not os.path.exists(audio_path):
            return "Erreur pendant la conversion.", 500

        return send_file(
            audio_path,
            as_attachment=True,
            download_name="SoundX.mp3"
        )

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

        if os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)