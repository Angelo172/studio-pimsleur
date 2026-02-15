from flask import Flask, request, send_file
from flask_cors import CORS
from pydub import AudioSegment
import edge_tts
import asyncio
import os
import uuid

app = Flask(__name__)
CORS(app)

# Dictionnaire des voix Neurales de Microsoft (Ultra-réalistes)
VOICES = {
    'fr': {'female': 'fr-FR-DeniseNeural', 'male': 'fr-FR-HenriNeural'},
    'en': {'female': 'en-US-AriaNeural', 'male': 'en-US-GuyNeural'},
    'en-uk': {'female': 'en-GB-SoniaNeural', 'male': 'en-GB-RyanNeural'},
    'es': {'female': 'es-ES-ElviraNeural', 'male': 'es-ES-AlvaroNeural'},
    'de': {'female': 'de-DE-KatjaNeural', 'male': 'de-DE-KillianNeural'},
    'zh-CN': {'female': 'zh-CN-XiaoxiaoNeural', 'male': 'zh-CN-YunxiNeural'},
    'yo': {'female': 'yo-NG-EkaetteNeural', 'male': 'yo-NG-AbeoNeural'},
    'pt': {'female': 'pt-PT-RaquelNeural', 'male': 'pt-PT-DuarteNeural'} # Fallback pour Fon
}

# Fonction pour générer une voix avec Edge-TTS
async def generate_human_voice(text, lang, gender, age, filename):
    # 1. Trouver la bonne voix (Homme ou Femme dans la bonne langue)
    voice_name = VOICES.get(lang, VOICES['fr']).get(gender, 'fr-FR-DeniseNeural')
    
    # 2. Ajuster l'âge en modifiant la hauteur de la voix (Pitch)
    pitch_adjustment = "+0Hz" # Adulte par défaut
    if age == 'child':
        pitch_adjustment = "+30Hz" # Voix plus aiguë
    elif age == 'young':
        pitch_adjustment = "+10Hz" # Légèrement plus aiguë
    elif age == 'old':
        pitch_adjustment = "-15Hz" # Voix plus grave
        
    # Création du fichier MP3
    communicate = edge_tts.Communicate(text, voice_name, pitch=pitch_adjustment)
    await communicate.save(filename)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    segments_data = data.get('segments', [])
    
    combined_audio = AudioSegment.empty()
    temp_files = []

    try:
        for seg in segments_data:
            text = seg.get('text', '').strip()
            lang = seg.get('lang', 'fr')
            gender = seg.get('gender', 'female')
            age = seg.get('age', 'adult')
            pause_duration = float(seg.get('pause', 0)) * 1000 

            if text:
                filename = f"temp_{uuid.uuid4()}.mp3"
                
                # Exécuter Edge-TTS de façon asynchrone
                asyncio.run(generate_human_voice(text, lang, gender, age, filename))
                temp_files.append(filename)
                
                # Mixer le son
                segment_audio = AudioSegment.from_mp3(filename)
                combined_audio += segment_audio
            
            # Ajouter la pause
            if pause_duration > 0:
                silence = AudioSegment.silent(duration=pause_duration)
                combined_audio += silence

        # Exporter
        output_path = "final_lesson.mp3"
        combined_audio.export(output_path, format="mp3")
        
        return send_file(output_path, as_attachment=True)

    finally:
        # Nettoyer les fichiers temporaires
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

if __name__ == '__main__':
    app.run(debug=True, port=5000)