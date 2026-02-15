<script setup>
import { ref } from 'vue'

// Liste des langues supportées
const availableLangs = [
  { code: 'fr', name: 'Français' },
  { code: 'en', name: 'Anglais (US)' },
  { code: 'en-uk', name: 'Anglais (UK)' },
  { code: 'es', name: 'Espagnol' },
  { code: 'de', name: 'Allemand' },
  { code: 'zh-CN', name: 'Chinois' },
  { code: 'yo', name: 'Yoruba' },
  { code: 'pt', name: 'Fon (Simulé via PT)' }
]

const isGenerating = ref(false)
const audioUrl = ref(null)

// Les profils de voix avec Genre et Âge !
const voices = ref([
  { id: 'v1', name: 'Narrateur', lang: 'fr', gender: 'male', age: 'adult' },
  { id: 'v2', name: 'Apprenant', lang: 'en', gender: 'female', age: 'young' }
])

const segments = ref([
  { id: 1, voiceId: 'v1', text: 'Écoutez cette conversation.', pause: 1.5 },
  { id: 2, voiceId: 'v2', text: 'Hello, how are you?', pause: 1.0 },
  { id: 3, voiceId: 'v1', text: 'Répétez après le locuteur.', pause: 2.0 }
])

const addVoice = () => {
  voices.value.push({ 
    id: 'v' + Date.now(), 
    name: 'Voix ' + (voices.value.length + 1), 
    lang: 'fr',
    gender: 'female',
    age: 'adult'
  })
}

const removeVoice = (id) => {
  if (voices.value.length > 1) {
    voices.value = voices.value.filter(v => v.id !== id)
  } else {
    alert("Il faut au moins une voix !")
  }
}

const addSegment = () => {
  const lastSeg = segments.value[segments.value.length - 1]
  let nextVoiceId = voices.value[0].id
  
  if (lastSeg && voices.value.length > 1) {
    const currentIndex = voices.value.findIndex(v => v.id === lastSeg.voiceId)
    if (currentIndex !== -1) {
        nextVoiceId = voices.value[(currentIndex + 1) % voices.value.length].id
    }
  }
  
  segments.value.push({ id: Date.now(), voiceId: nextVoiceId, text: '', pause: 2.0 })
}

const removeSegment = (index) => {
  if (segments.value.length > 0) {
    segments.value.splice(index, 1)
  }
}

const generateFullAudio = async () => {
  const fullTextCheck = segments.value.map(s => s.text).join('').trim();
  if (!fullTextCheck) {
    alert("Le script est vide ! Ajoutez du texte.");
    return;
  }

  isGenerating.value = true
  audioUrl.value = null 

  // On envoie la langue, le genre ET l'âge au serveur Python
  const payload = {
    segments: segments.value.map(s => {
      const voice = voices.value.find(v => v.id === s.voiceId)
      return {
        text: s.text,
        lang: voice ? voice.lang : 'fr',
        gender: voice ? voice.gender : 'female',
        age: voice ? voice.age : 'adult',
        pause: s.pause
      }
    })
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error('Erreur serveur Python')

    const blob = await response.blob()
    audioUrl.value = URL.createObjectURL(blob)
    
  } catch (err) {
    console.error("Erreur:", err)
    alert("Impossible de générer l'audio. Vérifiez que app.py tourne bien.")
  } finally {
    isGenerating.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 p-4 md:p-8 text-slate-900 font-sans">
    <div class="max-w-6xl mx-auto">
      
      <header class="mb-10 text-center">
        <div class="inline-flex items-center px-3 py-1 mb-4 rounded-full bg-indigo-50 text-indigo-600 text-[10px] font-bold uppercase tracking-widest border border-indigo-100">
          Studio de Production v3 (Voix Humaines)
        </div>
        <h1 class="text-4xl font-black tracking-tight text-slate-800 mb-2">
          PIMSLEUR <span class="text-indigo-600">MAKER</span>
        </h1>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <div class="lg:col-span-4 xl:col-span-4 space-y-6">
          <div class="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 sticky top-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="font-bold text-lg text-slate-800">Casting (Voix)</h2>
              <button @click="addVoice" class="w-8 h-8 bg-indigo-600 text-white rounded-full cursor-pointer hover:bg-indigo-700">+</button>
            </div>
            
            <div class="space-y-4">
              <div v-for="voice in voices" :key="voice.id" class="p-4 bg-slate-50 rounded-2xl border border-slate-100 relative group">
                <button @click="removeVoice(voice.id)" class="absolute -top-2 -right-2 w-6 h-6 bg-white text-slate-400 hover:text-red-500 rounded-full border shadow-sm cursor-pointer">&times;</button>
                
                <input v-model="voice.name" class="font-bold text-sm outline-none bg-transparent w-full mb-3 border-b focus:border-indigo-300" placeholder="Nom du personnage" />
                
                <div class="grid grid-cols-2 gap-2 mb-2">
                  <div>
                    <label class="block text-[9px] font-bold text-slate-400 uppercase">Langue</label>
                    <select v-model="voice.lang" class="w-full bg-white border rounded px-2 py-1 text-xs">
                      <option v-for="l in availableLangs" :key="l.code" :value="l.code">{{ l.name }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-[9px] font-bold text-slate-400 uppercase">Genre</label>
                    <select v-model="voice.gender" class="w-full bg-white border rounded px-2 py-1 text-xs">
                      <option value="male">Homme</option>
                      <option value="female">Femme</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label class="block text-[9px] font-bold text-slate-400 uppercase">Âge</label>
                  <select v-model="voice.age" class="w-full bg-white border rounded px-2 py-1 text-xs">
                    <option value="child">Enfant</option>
                    <option value="young">Jeune Adulte</option>
                    <option value="adult">Adulte</option>
                    <option value="old">Personne Âgée</option>
                  </select>
                </div>

              </div>
            </div>
          </div>
        </div>

        <div class="lg:col-span-8 xl:col-span-8">
          <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-200 min-h-[600px] flex flex-col">
            
            <div class="flex justify-between items-center mb-8">
              <h2 class="font-bold text-xl text-slate-800">Scénario de la leçon</h2>
              <button @click="addSegment" class="bg-slate-900 text-white px-5 py-2.5 rounded-xl font-bold text-sm cursor-pointer hover:bg-slate-800 border-none flex items-center gap-2">
                + Ajouter un dialogue
              </button>
            </div>

            <div class="flex-1 space-y-4 mb-8 overflow-y-auto pr-2 custom-scrollbar">
              <div v-for="(seg, index) in segments" :key="seg.id" class="flex gap-4 p-5 rounded-2xl border border-slate-100 bg-white">
                
                <div class="flex-1 space-y-3">
                  <div class="flex items-center gap-3">
                      <select v-model="seg.voiceId" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg border-none outline-none cursor-pointer">
                        <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.name }}</option>
                      </select>
                      <span class="text-[10px] text-slate-400 uppercase font-bold">Dit :</span>
                  </div>
                  <textarea v-model="seg.text" placeholder="Tapez le texte ici..." rows="2" class="w-full font-medium text-lg outline-none bg-transparent resize-none"></textarea>
                </div>

                <div class="flex flex-col items-center justify-between border-l border-slate-50 pl-4">
                  <div class="flex flex-col items-center bg-slate-50 px-2 py-2 rounded-xl border w-16">
                    <span class="text-[9px] font-bold text-slate-400 uppercase text-center mb-1">Silence<br>(sec)</span>
                    <input type="number" step="0.5" min="0" v-model="seg.pause" class="w-full text-center bg-transparent border-none font-black text-indigo-600 outline-none" />
                  </div>
                  <button @click="removeSegment(index)" class="text-slate-300 hover:text-red-500 cursor-pointer bg-transparent border-none mt-2">X</button>
                </div>
              </div>
            </div>

            <div class="pt-6 border-t border-slate-100 sticky bottom-0 bg-white">
              <button @click="generateFullAudio" :disabled="isGenerating" class="w-full py-4 rounded-2xl font-bold text-white transition-all cursor-pointer" :class="isGenerating ? 'bg-slate-300' : 'bg-indigo-600 hover:bg-indigo-700'">
                {{ isGenerating ? 'Production en cours...' : 'Générer la leçon MP3' }}
              </button>
              <div v-if="audioUrl" class="mt-6 p-4 bg-green-50 rounded-2xl border border-green-100 flex flex-col items-center gap-3">
                <audio :src="audioUrl" controls class="w-full h-10"></audio>
                <a :href="audioUrl" download="lecon_pimsleur.mp3" class="text-[10px] font-bold text-green-600 uppercase hover:underline">Télécharger le fichier</a>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #f1f5f9; border-radius: 20px; }
</style>