import os
import random
import pandas as pd

random.seed(42)

EASY_TARGET = 700   # easy/clear templates per class per language
HARD_TARGET = 300   # ambiguous/hard templates per class per language
TARGET = EASY_TARGET + HARD_TARGET  # 1000 total

def fill(template, slots):
    s = template
    for key, values in slots.items():
        s = s.replace("{" + key + "}", random.choice(values), 1)
    return s

def generate(templates, target):
    used, results = set(), []
    attempts = 0
    while len(results) < target and attempts < target * 200:
        tmpl, slots = random.choice(templates)
        sentence = fill(tmpl, slots)
        if sentence not in used:
            used.add(sentence)
            results.append(sentence)
        attempts += 1
    if len(results) < target:
        print(f"  Warning: only generated {len(results)}/{target}")
    return results


# ── Hard templates ── break keyword shortcuts by using emergency words in
# benign context (Routine hard) and minimizing language for real emergencies
# (Emergency hard) and borderline cases (Urgent hard).

EN_EMERGENCY_HARD = [
    # Atypical / minimized presentations — still true emergencies
    ("Patient reports {vague} in {loc} for {dur}, {context}", {
        "vague": ["mild discomfort","pressure","tightness","a funny feeling","an ache","heaviness"],
        "loc": ["the chest","the jaw","the left arm","the upper back","the epigastric region"],
        "dur": ["20 minutes","half an hour","the past hour","45 minutes","the last 30 minutes"],
        "context": ["now sweating and pale","with new onset nausea","feeling lightheaded","arm feels weak","teeth are aching too"],
    }),
    ("Elderly {sex} who {denial} but {finding}", {
        "sex": ["woman","man","patient","female","male"],
        "denial": ["denies any chest pain","says it is nothing serious","refuses to lie down","insists they are fine","wants to go home"],
        "finding": ["found to be diaphoretic","BP 80/50 on arrival","has been vomiting for one hour","is short of breath at rest","EMS reports witnessed loss of consciousness"],
    }),
    ("Sudden {s1} while {activity}, {s2}", {
        "s1": ["extreme fatigue","profound weakness","dizziness","near-fainting","confusion"],
        "activity": ["sitting quietly","watching television","lying in bed","eating dinner","talking on the phone"],
        "s2": ["unable to stand","speech became slurred","right side of face drooped","lost vision in one eye briefly","could not lift left arm"],
    }),
    ("Patient brought by family who noticed {s1} and {s2} at home", {
        "s1": ["slurred speech","confusion","inability to recognize them","one-sided weakness","unsteady gait suddenly"],
        "s2": ["patient minimizing symptoms","patient insisting they are fine","patient refusing care","patient saying it will pass","patient asking to leave"],
    }),
    ("{s1} with {s2} — patient rates pain only {score} out of 10 but {finding}", {
        "s1": ["Chest heaviness","Jaw discomfort","Arm tingling","Back pressure","Epigastric pain"],
        "s2": ["mild nausea","slight sweating","some fatigue","feeling cold","shortness of breath on exertion"],
        "score": ["3","4","2","3-4"],
        "finding": ["EKG shows ST elevation","troponin elevated","BP 88/60","oxygen saturation 88%","patient is a diabetic with silent MI risk"],
    }),
]

EN_URGENT_HARD = [
    # Urgent cases using 'severe' or scary words — but not immediately life-threatening
    ("{sev} dental pain with {s1} for {dur}", {
        "sev": ["Severe","Excruciating","Extreme","Unbearable"],
        "loc": ["lower jaw","upper molar","wisdom tooth area","right side of mouth"],
        "s1": ["facial swelling","cheek swelling","trismus","difficulty opening mouth fully","submandibular swelling"],
        "dur": ["2 days","3 days","since yesterday","48 hours","24 hours"],
    }),
    ("Severe {type} pain rated {score}/10 with {s1}, {s2}", {
        "type": ["flank","side","back","rib","lower back"],
        "score": ["8","9","9-10","8-9"],
        "s1": ["nausea","vomiting once","sweating","restlessness"],
        "s2": ["colicky in nature","comes in waves","patient pacing the room","unable to find comfortable position","radiating to groin"],
    }),
    ("{age} with {condition} presenting with {s1} and {s2} — vitals stable", {
        "age": ["55-year-old","62-year-old","48-year-old","70-year-old"],
        "condition": ["controlled hypertension","known COPD","type 2 diabetes","history of kidney stones"],
        "s1": ["worsening shortness of breath for 2 days","increased wheezing","productive cough with green sputum","burning chest discomfort on exertion"],
        "s2": ["no ST changes on EKG","troponin negative","oxygen 94%","temperature 38.5C","blood pressure 150/95"],
    }),
    ("Sudden severe {s1} after {trigger}, {s2}", {
        "s1": ["eye pain","vision change in one eye","red eye","eye discharge"],
        "trigger": ["chemical splash","foreign body entry","welding flash","sun exposure","contact lens use"],
        "s2": ["photophobia present","tearing heavily","visual acuity reduced","cornea appears cloudy","significant pain with movement"],
    }),
    ("Chest pain {char} for {dur} — {context}", {
        "char": ["reproducible with palpation","worsened by deep breath","positional","pleuritic","sharp and stabbing"],
        "dur": ["2 days","3 days","one day","since this morning"],
        "context": ["troponin pending","EKG normal so far","no radiation","no diaphoresis","vital signs stable but pain 8/10"],
    }),
]

EN_ROUTINE_HARD = [
    # Routine cases using emergency-sounding words in clearly benign context
    ("History of {condition} — currently {status}, here for {reason}", {
        "condition": ["stroke three years ago, fully recovered","heart attack two years ago, now asymptomatic",
                      "COPD, well controlled on inhaler","hypertension, on medication","diabetes, well managed"],
        "status": ["feeling well","completely asymptomatic","stable on current medications","doing well",
                   "no new symptoms","back to normal activities","no complaints"],
        "reason": ["routine medication refill","annual check-up","blood pressure check","follow-up labs","prescription renewal"],
    }),
    ("Chest wall {type} that {char} — {context}", {
        "type": ["pain","soreness","tenderness","discomfort"],
        "char": ["is reproducible with palpation","worsens with certain movements","appeared after exercise",
                 "is tender to touch","came on after carrying heavy bags","started after coughing"],
        "context": ["no shortness of breath","no diaphoresis","pain clearly musculoskeletal","no radiation","vital signs normal","no cardiac risk factors"],
    }),
    ("Mild shortness of breath that {char} — {context}", {
        "char": ["resolved completely on arrival","improved with rest","comes only with 4 flights of stairs",
                 "has been present for months unchanged","patient is a smoker, chronic baseline"],
        "context": ["oxygen saturation 99%","no acute distress","lungs clear to auscultation","no chest pain","no recent change from baseline","patient feels well now"],
    }),
    ("Patient concerned about {scary_symptom} but on evaluation {finding}", {
        "scary_symptom": ["chest pain","difficulty breathing","fast heartbeat","arm numbness","headache"],
        "finding": ["pain is musculoskeletal and reproducible","oxygen 99% and lungs clear","heart rate 78 and regular",
                    "sensation is tingling from sleeping on arm, resolved","tension headache responding to ibuprofen",
                    "anxiety-related symptoms, vitals normal","no objective findings","palpitations lasted seconds only"],
    }),
    ("{qual} headache — {context} — no {s1}", {
        "qual": ["Mild","Dull","Tension-type","Mild bilateral","Frontal"],
        "context": ["similar to usual migraines","same as previous episodes","patient recognizes pattern",
                    "started after long screen time","after skipping meals today","stress-related"],
        "s1": ["vomiting","fever","neck stiffness","vision changes","sudden onset","worst-ever quality"],
    }),
]

ES_EMERGENCY_HARD = [
    ("Paciente refiere {vague} en {loc} desde hace {dur}, {context}", {
        "vague": ["leve molestia","presion","tension","sensacion rara","pesadez"],
        "loc": ["el pecho","la mandibula","el brazo izquierdo","la espalda","el epigastrio"],
        "dur": ["20 minutos","media hora","la ultima hora","45 minutos"],
        "context": ["ahora sudando y palido","con nauseas nuevas","mareado","brazo debil","dolor dental tambien"],
    }),
    ("Anciano {sex} que {denial} pero {finding}", {
        "sex": ["mujer","hombre","paciente","senora","senor"],
        "denial": ["niega dolor en el pecho","dice que no es nada grave","quiere irse a casa","insiste en que esta bien"],
        "finding": ["esta diaforetico","PA 80/50 al llegar","ha vomitado una hora","tiene disnea en reposo","paramedicos reportan perdida de conocimiento"],
    }),
    ("Debilidad subita {s1} mientras {activity}, {s2}", {
        "s1": ["extrema","profunda","marcada","repentina"],
        "activity": ["estaba sentado","veia television","estaba en cama","estaba cenando","estaba hablando"],
        "s2": ["incapaz de ponerse de pie","habla incoherente","lado derecho del rostro cayo","perdio vision en un ojo brevemente","no pudo levantar el brazo izquierdo"],
    }),
    ("Familia llevo al paciente por {s1} y {s2} en casa", {
        "s1": ["habla incoherente","confusion","debilidad de un lado","marcha inestable subita"],
        "s2": ["paciente minimiza sintomas","paciente insiste en que esta bien","paciente se niega a recibir atencion"],
    }),
    ("{s1} con {s2} — paciente valora dolor solo {score} de 10 pero {finding}", {
        "s1": ["Pesadez en el pecho","Molestia en la mandibula","Hormigueo en el brazo","Presion en la espalda"],
        "s2": ["leve nausea","sudoracion leve","algo de fatiga","sensacion de frio"],
        "score": ["3","4","2","3-4"],
        "finding": ["EKG muestra elevacion del ST","troponina elevada","PA 88/60","saturacion de oxigeno 88%"],
    }),
]

ES_URGENT_HARD = [
    ("{sev} dolor dental con {s1} desde hace {dur}", {
        "sev": ["Severo","Intenso","Insoportable","Muy fuerte"],
        "s1": ["hinchazon facial","hinchazon de mejilla","trismo","dificultad para abrir la boca","hinchazon submandibular"],
        "dur": ["2 dias","3 dias","desde ayer","48 horas"],
    }),
    ("Dolor {type} intenso {score}/10 con {s1} y {s2}", {
        "type": ["en flanco","lateral","lumbar","costal"],
        "score": ["8","9","8-9"],
        "s1": ["nauseas","vomito unico","sudoracion","inquietud"],
        "s2": ["de caracter colico","que va y viene","irradia a la ingle","no encuentra posicion comoda"],
    }),
    ("Paciente con {condition} con {s1} y {s2} — signos vitales estables", {
        "condition": ["HTA controlada","EPOC conocido","diabetes tipo 2"],
        "s1": ["disnea que empeora desde hace 2 dias","sibilancias en aumento","tos productiva con esputo verde"],
        "s2": ["sin cambios en EKG","troponina negativa","saturacion 94%","temperatura 38.5C"],
    }),
    ("Dolor de {s1} subito tras {trigger}, {s2}", {
        "s1": ["ojo","vision en un ojo","ojo rojo"],
        "trigger": ["salpicadura quimica","cuerpo extrano","destello de soldadura","uso de lentes de contacto"],
        "s2": ["fotofobia presente","lagrimeo abundante","agudeza visual reducida","dolor con los movimientos oculares"],
    }),
    ("Dolor toracico {char} desde hace {dur} — {context}", {
        "char": ["reproducible con palpacion","empeora con inspiracion profunda","posicional","pleuritico","punzante"],
        "dur": ["2 dias","3 dias","desde esta manana"],
        "context": ["troponina pendiente","EKG normal por ahora","sin irradiacion","sin diaforesis","signos vitales estables"],
    }),
]

ES_ROUTINE_HARD = [
    ("Antecedente de {condition} — actualmente {status}, consulta por {reason}", {
        "condition": ["ACV hace tres anos totalmente recuperado","infarto hace dos anos sin sintomas actuales",
                      "EPOC bien controlado con inhalador","hipertension con medicacion","diabetes bien controlada"],
        "status": ["se encuentra bien","completamente asintomatico","estable con medicacion actual","sin nuevas quejas"],
        "reason": ["renovacion de receta","chequeo anual","control de tension arterial","analisis de seguimiento"],
    }),
    ("Dolor de pared toracica que {char} — {context}", {
        "char": ["es reproducible con palpacion","empeora con ciertos movimientos","aparecio tras ejercicio","duele al tocar"],
        "context": ["sin dificultad respiratoria","sin diaforesis","claramente musculoesqueletico","sin irradiacion","signos vitales normales"],
    }),
    ("Leve dificultad respiratoria que {char} — {context}", {
        "char": ["se resolvio al llegar","mejoro con reposo","solo aparece al subir 4 pisos","lleva meses igual sin cambios"],
        "context": ["saturacion 99%","sin dificultad aguda","pulmones limpios","sin dolor en el pecho","sin cambio respecto a la situacion basal"],
    }),
    ("Paciente preocupado por {scary_symptom} pero en la evaluacion {finding}", {
        "scary_symptom": ["dolor en el pecho","dificultad para respirar","corazon acelerado","entumecimiento del brazo","cefalea"],
        "finding": ["el dolor es musculoesqueletico y reproducible","saturacion 99% y pulmones limpios",
                    "ritmo cardiaco 78 y regular","hormigueo por dormir sobre el brazo ya resuelto",
                    "cefalea tensional que cede con ibuprofeno","sintomas por ansiedad con signos vitales normales"],
    }),
    ("Cefalea {qual} — {context} — sin {s1}", {
        "qual": ["leve","sorda","tensional","bilateral leve","frontal","occipital leve","pulsatil leve"],
        "context": ["similar a sus migranas habituales","igual que episodios previos","tras larga jornada frente a pantalla",
                    "por saltarse las comidas","despues de estres laboral","por deshidratacion leve","tras dormir mal"],
        "s1": ["vomitos","fiebre","rigidez de nuca","cambios visuales","inicio subito","intensidad maxima","fotofobia"],
    }),
    ("Paciente refiere {s1} leve que {char} — {context}", {
        "s1": ["fatiga","cansancio","malestar general","debilidad leve","somnolencia"],
        "char": ["mejora con reposo","cede con vitaminas","ha mejorado esta semana","es habitual en el","es habitual en ella"],
        "context": ["sin fiebre","sin perdida de peso","analisis recientes normales","sin linfadenopatias","exploracion normal","sin cambios recientes"],
    }),
]

HI_EMERGENCY_HARD = [
    ("Mariz ne bataya {vague} {loc} mein {dur} se, {context}", {
        "vague": ["halka sa dard","dabaav","khinchav","anjaani feeling","bhaari pan"],
        "loc": ["seene mein","jawde mein","baaye haath mein","peethe mein","upar pet mein"],
        "dur": ["20 minute","aadhe ghante","pichle ghante","45 minute"],
        "context": ["ab pasina aa raha hai aur chehre par palor","nai matli ke saath","chakkar aa rahe hain","haath kamzor ho gaya hai","daant mein bhi dard hai"],
    }),
    ("Bujurg {sex} jo {denial} lekin {finding}", {
        "sex": ["mahila","purush","mariz","behen","bhai"],
        "denial": ["seene mein koi dard nahi kehte","kehte hai kuch serious nahi","ghar jaana chahte hain","theek hone ka dawa karte hain"],
        "finding": ["pasina bahut aa raha hai","BP 80/50 milaa","ek ghante se ulti ho rahi hai","aaram se saans nahi le pa rahe","ambulance waale ne battaya ke behosh ho gaye the"],
    }),
    ("Achanak {s1} jab {activity} kar rahe the, {s2}", {
        "s1": ["bahut thakaan","bahut kamzori","chakkar","behoshi jaisi feeling","ghabrahat"],
        "activity": ["chup baithe the","TV dekh rahe the","lete hue the","khaana kha rahe the","baat kar rahe the"],
        "s2": ["khade nahi ho sake","bolne mein ladkhalahat aayi","chehre ka daahina hissa latka","ek aankhon se kuch der ke liye nahi dikha","baaya haath uthaa nahi pa rahe"],
    }),
    ("Parivaar ne laaya mariz ko ghar mein {s1} aur {s2} dekhkar", {
        "s1": ["bolne mein ladkhalahat","bheega hua confusion","ek taraf kamzori","achanak dhandhla chalna"],
        "s2": ["mariz khud theek bol raha hai","mariz treatment se mana kar raha hai","mariz ghar jaana chahta hai","mariz kehta hai apne aap theek ho jaayega"],
    }),
    ("{s1} aur {s2} ke saath — mariz dard sirf {score} mein se bata raha lekin {finding}", {
        "s1": ["Seene mein bhaari pan","Jawde mein halki takleef","Haath mein jhunjhunahat","Peethe mein dabaav"],
        "s2": ["halki matli","thoda sa pasina","thakaan"],
        "score": ["3","4","2"],
        "finding": ["EKG mein ST elevation hai","troponin badhi hui hai","BP 88/60 hai","oxygen 88 percent"],
    }),
]

HI_URGENT_HARD = [
    ("{sev} daant ka dard {s1} ke saath {dur} se", {
        "sev": ["Bahut tez","Asahniya","Bahut gambhir","Aniyantrit"],
        "s1": ["chehra sujan gaya","gaala sujan gaya","muh kam khul raha","dono jagah sujan"],
        "dur": ["2 din","3 din","kal se","48 ghante"],
    }),
    ("{type} mein bahut tez dard {score}/10 {s1} aur {s2} ke saath", {
        "type": ["kamar","ek taraf","pet ki taraf","paanch ki taraf"],
        "score": ["8","9","9-10"],
        "s1": ["matli","ek baar ulti","pasina","chain nahi"],
        "s2": ["lehriyaan aati hain","aa jaa karta hai","groyn tak failta hai","koi position aaramdaayak nahi"],
    }),
    ("{age} mariz jo {condition} ka {s1} aur {s2} — vital signs stable", {
        "age": ["55 saal ke","62 saal ke","48 saal ke","70 saal ke"],
        "condition": ["controlled BP ka","COPD ka","diabetes 2 ka"],
        "s1": ["2 din se saans fulna badh gaya","seeti ki awaaz zyada","haari balgam"],
        "s2": ["EKG mein koi badlaav nahi","troponin negative","oxygen 94 percent","temperature 38.5C"],
    }),
    ("Achanak {s1} {trigger} ke baad, {s2}", {
        "s1": ["aankhon mein dard","aankhon mein roshni","aankhon mein lali"],
        "trigger": ["chemical khule","aankhon mein kuch pada","welding ki roshni","contact lens se"],
        "s2": ["roshni se takleef","aankhon se paani","drishti thodi kami","aankhon ko hilane mein dard"],
    }),
    ("Seene mein dard {char} {dur} se — {context}", {
        "char": ["dabane se aata hai","gehri saans se badhtaa","position pe depend karta","ek taraf ka"],
        "dur": ["2 din","3 din","aaj subah se"],
        "context": ["troponin aaya nahi abhi","EKG theek hai abhi tak","kahin nahi jaata dard","pasina nahi","vital signs theek hain"],
    }),
]

HI_ROUTINE_HARD = [
    ("{condition} ki history — abhi {status}, aaye hain {reason} ke liye", {
        "condition": ["3 saal pehle stroke tha poori tarah theek","2 saal pehle heart attack tha ab koi lakshan nahi",
                      "COPD hai inhaler se control mein","BP hai dawa se control","diabetes hai theek manage"],
        "status": ["bilkul theek","koi lakshan nahi","dawa se stable","sab kuch theek","koi nayi takleef nahi"],
        "reason": ["dawa diwane","routine check-up","BP check","test karwane","prescription renew"],
    }),
    ("Seene ki deewar mein {type} jo {char} — {context}", {
        "type": ["dard","pida","takleef","bhaaripan"],
        "char": ["dabane se aata hai","kuch harakaton se badhtaa","vyayam ke baad shuru hua","haath lagane se dard"],
        "context": ["saans lene mein koi takleef nahi","pasina nahi","clearly musculoskeletal","kahin nahi jaata","vital signs normal"],
    }),
    ("Halka saans fulna jo {char} — {context}", {
        "char": ["aate hi theek ho gaya","aaram se theek ho gaya","4 manzil chadne par hi hota","mahino se aisa hi hai koi badlaav nahi"],
        "context": ["oxygen 99 percent","koi acute distress nahi","saans ki awaaz saaf","seene mein dard nahi","baseline se koi fark nahi"],
    }),
    ("Mariz {scary_symptom} se dara tha lekin jaanch mein {finding}", {
        "scary_symptom": ["seene mein dard","saans lene mein takleef","dil ki dhadkan tez","haath mein jhunjhunahat","sardard"],
        "finding": ["muscular dard hai aur dabane se milta hai","oxygen 99 aur saans bilkul saaf",
                    "dhadkan 78 aur regular","haath ke neechle hisse par sone se tha ab theek","tension headache ibuprofen se theek hua",
                    "anxiety se related koi objective finding nahi"],
    }),
    ("{qual} sardard — {context} — koi {s1} nahi", {
        "qual": ["Halka","Sust","Tension wala","Dono taraf halka","Aage ki taraf"],
        "context": ["pehle bhi aise hota tha","baar baar aisa hota hai","zyada der screen dekhne se","khaana chhodne se"],
        "s1": ["ulti","bukhar","gardan mein akadahat","najar mein badlaav","achanak shuru","jeevan ka sabse bada"],
    }),
]

BN_EMERGENCY_HARD = [
    ("Rogir bolle {vague} {loc} e {dur} dhore, {context}", {
        "vague": ["halka batha","chaap","khinchano","anjaana anubhab","bhari batha"],
        "loc": ["buke","chomale","bam hate","pitthe","pete upar"],
        "dur": ["20 minute","adha ghanta","shesh ghanta dhore","45 minute"],
        "context": ["ekhon ghaam hochhe o mukh shada hochhe","notun bomi bomi bhab er shathe","matha ghurochhe","haat durbolo hoyeche","dant e o batha achhe"],
    }),
    ("Brishkhor {sex} je {denial} kintu {finding}", {
        "sex": ["mahila","purush","rogi","didimoni","dadamoni"],
        "denial": ["buke kono batha nei bolen","bolen kono shomoshsha nei","barite jete chan","thik achen bolen"],
        "finding": ["ghaam hochhe o chaara hochhe","BP 80/50 pelam","ek ghanta dhore bomi hochhe","bishire shas nite parchhen na","ambulance bollen je ajnaan hoye gechen"],
    }),
    ("Hothat {s1} jakhon {activity} korchhilen, {s2}", {
        "s1": ["onek thaka","prochur durbolta","matha ghora","ajnaan er moto","ghabarani"],
        "activity": ["chup boshe chilen","television dekhchilen","shue chilen","raat er khana khachilen","kotha bolchilen"],
        "s2": ["darate parchhen na","kotha joriye geche","mukher dan dik jhule porche","ek chokhe kichu kshhoner jonne dekha geche na","bam haat tulte parchhen na"],
    }),
    ("Poribar niye eseche karon badi te {s1} o {s2} dekheche", {
        "s1": ["kotha joriye jachhhe","gholano confusion","ek dike durbolta","hothat dhandhla hata"],
        "s2": ["rogi nijeye thik bolen","rogi chikitsha nite raji na","rogi barite jete chan","rogi bolen nije theek hoye jabe"],
    }),
    ("{s1} o {s2} er shathe — rogi batha shudhu {score} bolen kintu {finding}", {
        "s1": ["Buke bhari laagchhe","Chomale halka batha","Hate jhimjhim","Pitthe chaap"],
        "s2": ["halka bomi bomi bhab","thoda ghaam","thaka laagchhe"],
        "score": ["3","4","2"],
        "finding": ["EKG e ST elevation achhe","troponin barche","BP 88/60","oxygen 88 percent"],
    }),
]

BN_URGENT_HARD = [
    ("{sev} danter batha {s1} er shathe {dur} dhore", {
        "sev": ["Khub tez","Ashoho","Otyonto","Atyanto beshi"],
        "s1": ["mukh fulon gechhe","gaal fulon gechhe","muh kom khulchhe","dui dike fulon"],
        "dur": ["dui din","tin din","gotokal theke","48 ghanta"],
    }),
    ("{type} te khub beshi batha {score}/10 {s1} o {s2} er shathe", {
        "type": ["kaanghare","ek dike","pete dike","paash e"],
        "score": ["8","9","9-10"],
        "s1": ["bomi bomi bhab","ekbar bomi hoyeche","ghaam hochhe","ashantho"],
        "s2": ["dhole dhole ase","aase jaye","groyne chharhiye jachhhe","kono obosthane aaram nai"],
    }),
    ("{age} rogi je {condition} er {s1} o {s2} — vital signs stable", {
        "age": ["55 bochhorer","62 bochhorer","48 bochhorer","70 bochhorer"],
        "condition": ["controlled BP er","COPD er","type 2 diabetes er"],
        "s1": ["dui din dhore shas fulanor beshi","ghanghor seetir awaaz","shobuj balgom er kashi"],
        "s2": ["EKG e kono badlaav nei","troponin negative","oxygen 94 percent","temperature 38.5C"],
    }),
    ("Hothat {s1} {trigger} er pore, {s2}", {
        "s1": ["chokhe batha","chokhe alo","chokh laal"],
        "trigger": ["chemical chhite porle","chokhe kichu porle","welding er alo theke","contact lens er karone"],
        "s2": ["aloy koshto hochhe","chokh theke paani porhchhe","drishti kom hochhe","chokh holatei batha hochhe"],
    }),
    ("Buke batha {char} {dur} dhore — {context}", {
        "char": ["chaap dilei hochhe","ghono shas nile barhchhe","position er upor norbhor kore","ek dike"],
        "dur": ["dui din","tin din","shokal theke"],
        "context": ["troponin esheni ekhono","EKG thik ache ekhono porjonto","kothao jachhhe na batha","ghaam hochhe na","vital signs thik ache"],
    }),
]

BN_ROUTINE_HARD = [
    ("{condition} er itihas achhe — ekhon {status}, eshechen {reason} er jonne", {
        "condition": ["tin bochhorer aage stroke hoyechilo pooro shoree thik","dui bochhorer aage heart attack ekhon kono laakhhon nei",
                      "COPD achhe inhaler e theek ache","BP achhe dawa te niyontrone","diabetes achhe theek manage"],
        "status": ["bhalo achhen","kono laakhhon nei","dawa te stable","shob theek","kono notun koshto nei"],
        "reason": ["dawa neoar","routine check","BP dekhar","test korar","prescription noboyon"],
    }),
    ("Buker deoale {type} je {char} — {context}", {
        "type": ["batha","peeda","koshto","bhari laagchhe"],
        "char": ["chaap dilei hochhe","kono kaje barhchhe","byayam er pore shuru hoyeche","haath lagale batha"],
        "context": ["shas neoay kono koshto nei","ghaam hochhe na","shoshposhto musculoskeletal","kothao jachhhe na","vital signs normal"],
    }),
    ("Halka shas fulano je {char} — {context}", {
        "char": ["ese thikthak hoe gechhe","bishrame theek hoe gechhe","4 tala uthlei hoy shudhu","moaser por theke emon konodin badhaay ni"],
        "context": ["oxygen 99 percent","kono acute koshto nei","shas er awaaz porishtho","buke batha nei","baseline theke kono pariborton nei"],
    }),
    ("Rogi {scary_symptom} niye chintiyo chilen kintu parikkkhay {finding}", {
        "scary_symptom": ["buke batha","shas neoay koshto","dil tez dhukchhe","hate jhimjhim","mathabatha"],
        "finding": ["muscular batha chaap dilei hochhe","oxygen 99 o shas porishtho",
                    "heart rate 78 o regular","ghume hate shuye thaka theke jhimjhim ekhon theek",
                    "tension mathabatha paracetamol e kome gechhe","anxiety theke vital signs thik"],
    }),
    ("{qual} mathabatha — {context} — kono {s1} nei", {
        "qual": ["Halka","Sust","Tension er","Dui dike halka","Shmukhe"],
        "context": ["ageo erokomo hoto","baar baar hochhe","onek kkhhon screen er shamne"],
        "s1": ["bomi","jor","gharer shoktohat","drishti badlaav","hothat shuru","jiboner shobcheye kharap"],
    }),
]

# ═══════════════════════════════════════════════════════════════
#  ENGLISH
# ═══════════════════════════════════════════════════════════════

EN_EMERGENCY = [
    ("{sev} chest pain radiating to {loc} with {s1} and {s2}", {
        "sev": ["Severe","Acute","Crushing","Excruciating","Intense","Sudden severe","Extreme"],
        "loc": ["the left arm","the jaw","the back","the left shoulder","both arms","the neck","the right arm"],
        "s1": ["sweating","cold sweats","diaphoresis","profuse sweating","clammy skin","pallor"],
        "s2": ["nausea","vomiting","shortness of breath","dizziness","weakness","extreme fatigue","palpitations"],
    }),
    ("Sudden {q} loss of consciousness, {r}", {
        "q": ["complete","unexplained","witnessed","unwitnessed","prolonged","brief"],
        "r": ["unresponsive to stimulation","not responding to verbal commands","unable to be aroused",
              "found collapsed on floor","no response to pain stimulus","eyes fixed and unresponsive"],
    }),
    ("{sev} difficulty breathing with {s1} and {s2}", {
        "sev": ["Severe","Extreme","Critical","Acute","Life-threatening","Progressive"],
        "s1": ["inability to complete sentences","speaking in single words","lips turning blue",
               "oxygen saturation critically low","use of accessory muscles","visible respiratory distress"],
        "s2": ["cyanotic fingertips","audible stridor","respiratory rate above 30","severe hypoxia",
               "paradoxical breathing","tracheal deviation"],
    }),
    ("Severe allergic reaction with {s1} and {s2} after {trigger} exposure", {
        "s1": ["throat swelling","tongue angioedema","facial swelling","airway compromise","uvula swelling"],
        "s2": ["unable to swallow","unable to breathe","blood pressure crashing","widespread urticaria","anaphylactic shock"],
        "trigger": ["bee sting","peanut ingestion","shellfish","penicillin","latex","contrast dye","wasp sting","aspirin"],
    }),
    ("Sudden {q} headache described as {desc} with {s1}", {
        "q": ["severe","thunderclap","explosive","worst-ever","maximal-intensity"],
        "desc": ["worst of life","never experienced before","a lightning bolt","an explosion in the head","10 out of 10"],
        "s1": ["neck stiffness","photophobia and vomiting","altered consciousness","neck rigidity","fever and rash"],
    }),
    ("Stroke symptoms: {s1}, {s2} and {s3}", {
        "s1": ["right-sided facial droop","left-sided facial droop","sudden facial asymmetry","mouth drooping to one side"],
        "s2": ["right arm weakness","left arm weakness","arm drift on extension","sudden arm paralysis"],
        "s3": ["slurred speech","aphasia","unable to speak","garbled speech","global aphasia","expressive aphasia"],
    }),
    ("Uncontrolled {type} bleeding from {source} not responding to {treatment}", {
        "type": ["severe","profuse","arterial","massive","pulsatile"],
        "source": ["deep laceration","penetrating wound","abdominal stab wound","leg wound","scalp laceration","femoral area"],
        "treatment": ["direct pressure","tourniquet","wound packing","pressure dressing","manual compression"],
    }),
    ("High fever {temp} with {s1} lasting {dur}", {
        "temp": ["104F","105F","40.2C","40.5C","103.9F","40C"],
        "s1": ["generalized tonic-clonic seizure","febrile convulsion","absence seizure","focal seizure","status epilepticus"],
        "dur": ["3 minutes","5 minutes","over 2 minutes","approximately 4 minutes","more than 5 minutes"],
    }),
    ("Severe abdominal pain with {s1} and {s2}", {
        "s1": ["board-like rigidity","guarding throughout","rebound tenderness","peritoneal signs","involuntary guarding"],
        "s2": ["vomiting blood","hematemesis","melena","bloody diarrhea","coffee ground emesis","signs of perforation"],
    }),
    ("{age} found {state} with {s1}", {
        "age": ["Elderly patient","Young adult","Middle-aged male","Pediatric patient","Teenager","Infant","Toddler"],
        "state": ["unresponsive","collapsed","unconscious on floor","not breathing normally","pulseless","cyanotic"],
        "s1": ["no palpable pulse","absent respirations","agonal breathing","fixed dilated pupils","cyanotic lips"],
    }),
    ("Massive {type} trauma with {s1} and {s2}", {
        "type": ["head","chest","abdominal","spinal","pelvic","multi-system"],
        "s1": ["GCS of 3","loss of consciousness","altered mental status","confusion and combativeness","unresponsiveness"],
        "s2": ["active arterial bleeding","visible deformity","signs of internal hemorrhage","hemodynamic instability","shock"],
    }),
    ("Diabetic patient with glucose {level} presenting with {s1} and {s2}", {
        "level": ["over 600 mg/dL","below 30 mg/dL","critically low","500 mg/dL","25 mg/dL","700 mg/dL"],
        "s1": ["altered consciousness","generalized seizure","unresponsiveness","aggressive confusion","coma"],
        "s2": ["diaphoresis","Kussmaul breathing","fruity breath odor","severe weakness","cardiovascular collapse"],
    }),
    ("Suspected {type} overdose with {s1} and {s2}", {
        "type": ["opioid","benzodiazepine","tricyclic antidepressant","mixed substance","stimulant"],
        "s1": ["pinpoint pupils","respiratory depression","loss of consciousness","tonic-clonic seizures","cardiac arrhythmia"],
        "s2": ["cyanosis","bradycardia","hypotension","unresponsive to naloxone","respiratory arrest"],
    }),
    ("Aortic dissection suspected with {s1} radiating to {loc} and {s2}", {
        "s1": ["tearing chest pain","ripping back pain","sudden severe chest pain","knife-like pain"],
        "loc": ["the back","the abdomen","between shoulder blades","the neck"],
        "s2": ["pulse differential between arms","blood pressure difference","syncope","lower limb paralysis"],
    }),
    ("Pulmonary embolism suspected with {s1}, {s2} and {s3}", {
        "s1": ["sudden pleuritic chest pain","acute dyspnea","sudden chest tightness"],
        "s2": ["oxygen saturation 80%","severe hypoxia","tachycardia 140 bpm","tachycardia"],
        "s3": ["recent long-haul flight","recent surgery","deep vein thrombosis history","immobility for 3 weeks"],
    }),
]

EN_URGENT = [
    ("High fever {temp} with {s1} and {s2}", {
        "temp": ["102F","103F","39.5C","39C","102.8F","38.9C"],
        "s1": ["severe sore throat","difficulty swallowing","inability to open mouth fully","marked tonsillar swelling","cervical lymphadenopathy"],
        "s2": ["drooling","voice change","hot potato voice","referred ear pain","odynophagia"],
    }),
    ("{qual} abdominal pain in {loc} with {s1}", {
        "qual": ["Moderate","Significant","Worsening","Persistent","Intermittent severe"],
        "loc": ["right lower quadrant","right upper quadrant","left lower quadrant","epigastric region","periumbilical area"],
        "s1": ["nausea and vomiting","anorexia","rebound tenderness","guarding","low-grade fever"],
    }),
    ("Suspected {bone} fracture after {mechanism} with {s1} and {s2}", {
        "bone": ["wrist","radius","ankle","forearm","clavicle","finger","toe"],
        "mechanism": ["fall on outstretched hand","direct impact","sports injury","fall from height","twisting injury"],
        "s1": ["significant swelling","marked swelling","immediate swelling"],
        "s2": ["bruising","ecchymosis","tenderness on palpation","inability to move joint","deformity"],
    }),
    ("Persistent vomiting for {dur} with {s1}", {
        "dur": ["6 hours","8 hours","12 hours","the past day","over 10 hours"],
        "s1": ["inability to keep fluids down","signs of dehydration","dry mucous membranes","decreased urine output","electrolyte imbalance concern"],
    }),
    ("{type} ear pain with {s1} and {s2}", {
        "type": ["Severe","Throbbing","Persistent","Worsening"],
        "s1": ["purulent discharge","bloody discharge","clear discharge","greenish discharge"],
        "s2": ["decreased hearing","significant hearing loss","tinnitus","dizziness","facial nerve involvement"],
    }),
    ("Urinary symptoms with {s1}, {s2} and {s3}", {
        "s1": ["burning on urination","severe dysuria","painful urination"],
        "s2": ["blood in urine","gross hematuria","pink-tinged urine","frank blood"],
        "s3": ["lower back pain","flank pain","costovertebral angle tenderness","fever 38.5C"],
    }),
    ("Migraine with {s1}, {s2} and {s3}", {
        "s1": ["visual aura","scintillating scotoma","zigzag lines in vision","hemianopia"],
        "s2": ["vomiting","nausea unresponsive to medication","projectile vomiting"],
        "s3": ["severe photophobia","phonophobia","unresponsive to usual medications","lasting over 72 hours"],
    }),
    ("{body} sprain with {s1} and {s2} after {mechanism}", {
        "body": ["Ankle","Knee","Wrist","Shoulder","Elbow"],
        "s1": ["significant swelling","immediate swelling","marked edema"],
        "s2": ["inability to bear weight","inability to move","severe pain on palpation","ecchymosis"],
        "mechanism": ["twisting injury","sports collision","fall","direct blow","awkward landing"],
    }),
    ("Rash {pattern} with {s1} and {s2}", {
        "pattern": ["spreading across torso","spreading to extremities","appearing on face and trunk","covering large body area"],
        "s1": ["low-grade fever","mild fever 38C","temperature of 37.8C"],
        "s2": ["joint pain","arthralgia","lymphadenopathy","pruritus","desquamation"],
    }),
    ("Child with fever {temp} for {dur} with {s1}", {
        "temp": ["103F","102.5F","39C","39.5C","38.9C"],
        "dur": ["2 days","3 days","48 hours","72 hours","the past 2 days"],
        "s1": ["decreased urine output","no wet diapers for 8 hours","signs of dehydration","lethargy","irritability"],
    }),
    ("Laceration requiring sutures on {loc} with {s1}", {
        "loc": ["forehead","chin","hand","arm","leg","scalp","lip"],
        "s1": ["wound gaping more than 1cm","unable to achieve hemostasis","exposed subcutaneous tissue","foreign body present","tendon visible"],
    }),
    ("Asthma exacerbation with {s1} and {s2}", {
        "s1": ["moderate wheeze","audible wheeze","diffuse wheeze","persistent wheeze"],
        "s2": ["peak flow 50% predicted","poor response to bronchodilator","increased work of breathing","oxygen saturation 92%"],
    }),
    ("Cellulitis of {loc} with {s1} and {s2}", {
        "loc": ["lower leg","forearm","face","periorbital area","hand","foot"],
        "s1": ["spreading erythema","advancing red margin","warmth and induration","significant swelling"],
        "s2": ["fever 38.5C","lymphangitis","tender lymph nodes","failure to improve with oral antibiotics"],
    }),
    ("First trimester pregnancy with {s1} and {s2}", {
        "s1": ["vaginal bleeding","heavy spotting","significant bleeding"],
        "s2": ["cramping","lower abdominal pain","pelvic pain","right-sided pelvic pain","shoulder tip pain"],
    }),
    ("Hypertensive urgency with blood pressure {bp} and {s1}", {
        "bp": ["180/110","190/120","200/115","185/110","175/115"],
        "s1": ["severe headache","visual disturbance","nosebleed","chest discomfort","palpitations"],
    }),
]

EN_ROUTINE = [
    ("{qual} cough for {dur} with {s1}", {
        "qual": ["Mild","Dry","Productive","Intermittent","Persistent mild","Low-grade","Occasional"],
        "dur": ["3 days","4 days","5 days","one week","a few days","2 days","6 days"],
        "s1": ["no fever","no shortness of breath","mild throat irritation","clear sputum","no systemic symptoms",
               "improving gradually","no wheezing","mild congestion","resolving spontaneously"],
    }),
    ("Skin {type} on {loc} with {s1}", {
        "type": ["rash","lesion","patch","eruption","bump"],
        "loc": ["forearm","upper arm","lower leg","back","neck","abdomen"],
        "s1": ["no systemic symptoms","mild pruritus","no fever","stable for 2 days","not spreading"],
    }),
    ("{qual} lower back pain after {cause} improving with {treatment}", {
        "qual": ["Mild","Dull","Aching","Mild to moderate"],
        "cause": ["lifting heavy objects","prolonged sitting","gardening","bending","exercise"],
        "treatment": ["rest","lying down","over-the-counter ibuprofen","heat application","change in position"],
    }),
    ("Runny nose and {s1} consistent with {type}", {
        "s1": ["sneezing","nasal congestion","post-nasal drip","watery eyes","itchy eyes","mild cough"],
        "type": ["seasonal allergies","allergic rhinitis","common cold","viral upper respiratory infection"],
    }),
    ("{qual} headache responding to {treatment}", {
        "qual": ["Mild","Tension-type","Mild frontal","Bilateral mild","Dull"],
        "treatment": ["over-the-counter ibuprofen","paracetamol","rest in dark room","hydration","ibuprofen 400mg"],
    }),
    ("Minor {type} on {loc} that has {status}", {
        "type": ["cut","laceration","abrasion","scratch","wound"],
        "loc": ["finger","hand","arm","leg","foot","knee"],
        "status": ["stopped bleeding","been cleaned","been bandaged","clotted naturally","minimal bleeding"],
    }),
    ("Constipation for {dur} with {s1}", {
        "dur": ["3 days","4 days","5 days","several days"],
        "s1": ["no vomiting","mild cramping","no blood in stool","no fever","mild abdominal discomfort"],
    }),
    ("{qual} fatigue for {dur} with {s1}", {
        "qual": ["Mild","Moderate","Generalized","Persistent"],
        "dur": ["one week","several days","5 days","a few days"],
        "s1": ["no other symptoms","adequate sleep","normal appetite","no fever","no weight loss"],
    }),
    ("{qual} sore throat with {s1}", {
        "qual": ["Mild","Scratchy","Irritating","Low-grade"],
        "s1": ["no fever","no difficulty swallowing","no exudate","no lymphadenopathy","mild discomfort only"],
    }),
    ("Insomnia for {dur} with {s1}", {
        "dur": ["one week","several nights","5 days","over a week"],
        "s1": ["no other symptoms","stress-related","no medication side effects","otherwise feeling well","affecting daily function mildly"],
    }),
    ("{qual} nausea for {dur} without {s1}", {
        "qual": ["Mild","Intermittent","Low-grade"],
        "dur": ["one day","2 days","several hours"],
        "s1": ["vomiting","diarrhea","fever","significant pain","systemic symptoms"],
    }),
    ("Mild {type} rash on {loc} present for {dur}", {
        "type": ["itchy","dry","scaly","red","pink"],
        "loc": ["hands","feet","neck","chest","back"],
        "dur": ["2 days","3 days","one week","several days"],
    }),
    ("Request for routine {type} refill with no acute complaints", {
        "type": ["blood pressure medication","diabetes medication","thyroid medication","asthma inhaler","allergy medication"],
    }),
    ("Mild {type} pain rated {score} out of 10 not interfering with {activity}", {
        "type": ["knee","shoulder","wrist","hip","neck","elbow"],
        "score": ["2","3","2-3","3-4"],
        "activity": ["daily activities","sleep","walking","work"],
    }),
    ("Follow-up for {condition} with {s1}", {
        "condition": ["controlled hypertension","well-managed diabetes","seasonal allergies","mild eczema"],
        "s1": ["no new complaints","stable symptoms","good medication compliance","no side effects reported"],
    }),
]

# ═══════════════════════════════════════════════════════════════
#  SPANISH
# ═══════════════════════════════════════════════════════════════

ES_EMERGENCY = [
    ("{sev} dolor en el pecho que se irradia hacia {loc} con {s1} y {s2}", {
        "sev": ["Dolor intenso","Dolor aplastante","Dolor severo","Dolor agudo","Dolor insoportable","Presion intensa"],
        "loc": ["el brazo izquierdo","la mandibula","la espalda","el hombro izquierdo","ambos brazos","el cuello"],
        "s1": ["sudoracion profusa","sudoracion fria","diaforesis","palidez marcada"],
        "s2": ["nauseas","vomitos","dificultad para respirar","mareos","debilidad extrema"],
    }),
    ("Perdida {q} del conocimiento con {r}", {
        "q": ["repentina","completa","inexplicable","presenciada","breve","prolongada"],
        "r": ["sin respuesta a estimulos","sin respuesta a llamados verbales","no puede ser despertado",
              "encontrado en el suelo","sin respuesta al dolor"],
    }),
    ("{sev} dificultad para respirar con {s1} y {s2}", {
        "sev": ["Severa","Extrema","Critica","Aguda","Progresiva"],
        "s1": ["incapacidad para terminar oraciones","solo puede decir palabras sueltas","labios azulados","saturacion de oxigeno muy baja"],
        "s2": ["cianosis en dedos","estridor audible","frecuencia respiratoria muy alta","uso de musculos accesorios"],
    }),
    ("Reaccion alergica grave con {s1} y {s2} tras exposicion a {trigger}", {
        "s1": ["hinchazon de garganta","angioedema lingual","hinchazon facial","compromiso de la via aerea"],
        "s2": ["imposibilidad de deglutir","imposibilidad de respirar","presion arterial en descenso","urticaria generalizada"],
        "trigger": ["picadura de abeja","mani","mariscos","penicilina","latex","medio de contraste","aspirina"],
    }),
    ("Dolor de cabeza {q} descrito como {desc} con {s1}", {
        "q": ["severo","explosivo","el peor de la vida","de inicio subito","tipo trueno"],
        "desc": ["el peor de su vida","nunca antes experimentado","una explosion en la cabeza","intensidad maxima"],
        "s1": ["rigidez de nuca","fotofobia y vomitos","alteracion de conciencia","fiebre y erupcion"],
    }),
    ("Sintomas de accidente cerebrovascular: {s1}, {s2} y {s3}", {
        "s1": ["caida facial del lado derecho","caida facial del lado izquierdo","asimetria facial subita"],
        "s2": ["debilidad del brazo derecho","debilidad del brazo izquierdo","paralisis de extremidad superior"],
        "s3": ["habla incoherente","afasia","incapacidad para hablar","dislalia severa"],
    }),
    ("Sangrado {type} incontrolable de {source} que no cede con {treatment}", {
        "type": ["severo","profuso","arterial","masivo"],
        "source": ["herida profunda","herida penetrante","herida abdominal","herida en pierna"],
        "treatment": ["presion directa","torniquete","taponamiento de herida","vendaje compresivo"],
    }),
    ("Fiebre muy alta de {temp} con {s1} durante {dur}", {
        "temp": ["40C","40.5C","41C","40.2C"],
        "s1": ["convulsiones generalizadas","crisis convulsiva febril","movimientos tonico-clonicos"],
        "dur": ["3 minutos","5 minutos","mas de 2 minutos","aproximadamente 4 minutos"],
    }),
    ("Dolor abdominal intenso con {s1} y {s2}", {
        "s1": ["abdomen en tabla","rigidez abdominal marcada","signo de rebote positivo","defensa muscular involuntaria"],
        "s2": ["vomito con sangre","hematemesis","melena","heces con sangre","signos de perforacion"],
    }),
    ("{age} hallado {state} con {s1}", {
        "age": ["Paciente anciano","Adulto joven","Paciente de mediana edad","Nino","Adolescente"],
        "state": ["sin respuesta","colapsado","inconsciente en el suelo","sin respiracion normal","sin pulso"],
        "s1": ["sin pulso palpable","ausencia de respiracion","respiracion agonica","pupilas fijas dilatadas","cianosis"],
    }),
    ("Traumatismo grave de {type} con {s1} y {s2}", {
        "type": ["craneo","torax","abdomen","columna vertebral","pelvis"],
        "s1": ["Glasgow de 3","perdida de conciencia","estado mental alterado","confusion y agitacion"],
        "s2": ["sangrado activo","deformidad visible","signos de hemorragia interna","shock hemodinamico"],
    }),
    ("Paciente diabetico con glucemia {level} con {s1} y {s2}", {
        "level": ["mayor de 600","menor de 30","criticamente baja","500 mg/dL","700 mg/dL"],
        "s1": ["conciencia alterada","convulsion generalizada","sin respuesta","confusion severa"],
        "s2": ["diaforesis","respiracion de Kussmaul","aliento frutal","debilidad severa"],
    }),
    ("Sospecha de embolia pulmonar con {s1}, {s2} y {s3}", {
        "s1": ["dolor toracico pleuritico subito","disnea aguda severa","taquicardia de 140"],
        "s2": ["saturacion de oxigeno del 80%","hipoxia grave","cianosis periferica"],
        "s3": ["antecedente de vuelo largo","cirugia reciente","trombosis venosa profunda previa"],
    }),
    ("Sobredosis de {type} con {s1} y {s2}", {
        "type": ["opiaceos","benzodiacepinas","antidepresivos triciclicos","sustancia desconocida"],
        "s1": ["pupilas puntiformes","depresion respiratoria","perdida de conciencia","convulsiones"],
        "s2": ["cianosis","bradicardia","hipotension","paro respiratorio"],
    }),
    ("Preeclampsia severa con {s1}, {s2} y {s3}", {
        "s1": ["presion arterial 170/110","hipertension severa","presion 180/120"],
        "s2": ["cefalea intensa","vision borrosa","epigastralgia","dolor en barra"],
        "s3": ["edema generalizado","convulsiones","proteinuria masiva","oliguria"],
    }),
]

ES_URGENT = [
    ("Fiebre alta de {temp} con {s1} y {s2}", {
        "temp": ["39C","39.5C","39.2C","38.9C","39.8C","40C","38.8C","39.3C"],
        "s1": ["dolor de garganta severo","dificultad para deglutir","odinofagia intensa","amigdalas inflamadas"],
        "s2": ["babeo","cambio de voz","ganglios cervicales dolorosos","dificultad para abrir la boca"],
    }),
    ("Dolor abdominal {qual} en {loc} con {s1}", {
        "qual": ["moderado","significativo","persistente","intermitente severo","en aumento"],
        "loc": ["fosa iliaca derecha","hipocondrio derecho","hipocondrio izquierdo","region epigastrica","area periumbilical"],
        "s1": ["nauseas y vomitos","anorexia","fiebre leve","defensa muscular","rebote leve"],
    }),
    ("Posible fractura de {bone} tras {mechanism} con {s1} y {s2}", {
        "bone": ["muneca","radio","tobillo","antebrazo","clavicula","dedo"],
        "mechanism": ["caida sobre mano extendida","impacto directo","lesion deportiva","caida de altura"],
        "s1": ["edema importante","hematoma extenso","deformidad visible"],
        "s2": ["incapacidad de movilizar","dolor intenso a la palpacion","crepitacion"],
    }),
    ("Vomitos persistentes durante {dur} con {s1}", {
        "dur": ["6 horas","8 horas","12 horas","todo el dia","mas de 10 horas"],
        "s1": ["imposibilidad de mantener liquidos","signos de deshidratacion","mucosas secas","oliguria","desequilibrio electrolitico"],
    }),
    ("Otalgia {qual} con {s1} y {s2}", {
        "qual": ["intensa","pulsatil","persistente","en aumento"],
        "s1": ["secrecion purulenta","secrecion sanguinolenta","secrecion verdosa"],
        "s2": ["hipoacusia","acufenos","mareos","paralisis facial"],
    }),
    ("Sintomas urinarios con {s1}, {s2} y {s3}", {
        "s1": ["ardor al orinar","disuria severa","micciones frecuentes y dolorosas"],
        "s2": ["hematuria macroscopica","orina rosada","sangre en orina"],
        "s3": ["dolor lumbar","dolor en fosa renal","punopierna positiva","fiebre de 38.5C"],
    }),
    ("Migrana con {s1}, {s2} y {s3}", {
        "s1": ["aura visual","escotoma centelleante","hemianopsia","lineas en zigzag"],
        "s2": ["vomitos","nauseas que no ceden","vomitos en proyectil"],
        "s3": ["fotofobia intensa","fonofobia","sin respuesta a medicacion habitual","mas de 72 horas"],
    }),
    ("Esguince de {body} con {s1} y {s2} tras {mechanism}", {
        "body": ["tobillo","rodilla","muneca","hombro"],
        "s1": ["edema importante","hematoma extenso","hinchazon inmediata"],
        "s2": ["imposibilidad de apoyar","imposibilidad de caminar","dolor severo a la presion"],
        "mechanism": ["torcedura","lesion deportiva","caida","impacto directo"],
    }),
    ("Erupcion cutanea {pattern} con {s1} y {s2}", {
        "pattern": ["que se extiende por el torso","que avanza hacia extremidades","en cara y tronco"],
        "s1": ["fiebre leve de 38C","temperatura de 37.8C","febricula"],
        "s2": ["dolor articular","adenopatias","prurito intenso","descamacion"],
    }),
    ("Nino con fiebre {temp} durante {dur} con {s1}", {
        "temp": ["39C","39.5C","38.9C","39.2C"],
        "dur": ["2 dias","3 dias","48 horas","72 horas"],
        "s1": ["disminucion de diuresis","sin panales mojados en 8 horas","signos de deshidratacion","letargia","irritabilidad"],
    }),
    ("Celulitis de {loc} con {s1} y {s2}", {
        "loc": ["pierna","antebrazo","cara","zona periorbital","mano","pie"],
        "s1": ["eritema que avanza","borde rojo progresivo","calor e induracion"],
        "s2": ["fiebre de 38.5C","linfangitis","ganglios dolorosos","sin respuesta a antibioticos orales"],
    }),
    ("Crisis asmatica con {s1} y {s2}", {
        "s1": ["sibilancias moderadas","sibilancias audibles","sibilancias difusas"],
        "s2": ["flujo espiratorio al 50%","mala respuesta a broncodilatador","aumento del trabajo respiratorio"],
    }),
    ("Infeccion del tracto urinario superior con {s1} y {s2}", {
        "s1": ["fiebre alta","escalofrios","temblores intensos"],
        "s2": ["dolor en flanco","punopierna derecha positiva","punopierna izquierda positiva","nauseas"],
    }),
    ("Sospecha de apendicitis con {s1} y {s2}", {
        "s1": ["dolor que inicio periumbilical y migro a FID","McBurney positivo","dolor en fosa iliaca derecha"],
        "s2": ["anorexia","fiebre leve","nauseas","vomito unico","signo de Rovsing positivo"],
    }),
    ("Sangrado vaginal {q} en {trimester} con {s1}", {
        "q": ["moderado","abundante","intermitente"],
        "trimester": ["primer trimestre","segundo trimestre","tercer trimestre"],
        "s1": ["calambres","dolor pelvico","dolor abdominal bajo","dolor en hombro","presion pelvica"],
    }),
]

ES_ROUTINE = [
    ("Tos {qual} durante {dur} con {s1}", {
        "qual": ["leve","seca","productiva","intermitente","persistente leve","ocasional","escasa"],
        "dur": ["3 dias","4 dias","5 dias","una semana","varios dias","2 dias","6 dias","10 dias"],
        "s1": ["sin fiebre","sin dificultad respiratoria","leve irritacion de garganta","flema clara",
               "sin sintomas sistemicos","mejorando progresivamente","sin sibilancias","congestion leve"],
    }),
    ("{type} cutaneo en {loc} con {s1}", {
        "type": ["Sarpullido","Lesion","Erupcion","Mancha"],
        "loc": ["antebrazo","brazo","pierna","espalda","cuello","abdomen"],
        "s1": ["sin sintomas sistemicos","leve prurito","sin fiebre","estable desde hace 2 dias","no se extiende"],
    }),
    ("Dolor lumbar {qual} tras {cause} que mejora con {treatment}", {
        "qual": ["leve","sordo","moderado leve"],
        "cause": ["levantar objetos pesados","estar sentado mucho tiempo","jardineria","flexion"],
        "treatment": ["reposo","ibuprofeno sin receta","calor local","cambio de postura"],
    }),
    ("Rinorrea y {s1} compatibles con {type}", {
        "s1": ["estornudos","congestion nasal","goteo postnasal","ojos llorosos","ojos pruriginosos"],
        "type": ["alergias estacionales","rinitis alergica","resfriado comun","infeccion viral de vias altas"],
    }),
    ("Cefalea {qual} que responde a {treatment}", {
        "qual": ["leve","tensional","frontal leve","bilateral leve","sorda"],
        "treatment": ["ibuprofeno sin receta","paracetamol","reposo en habitacion oscura","hidratacion"],
    }),
    ("Herida {type} en {loc} que ya {status}", {
        "type": ["pequena","superficial","leve","menor"],
        "loc": ["dedo","mano","brazo","pierna","pie","rodilla"],
        "status": ["dejo de sangrar","fue limpiada","fue vendada","coagulo sola"],
    }),
    ("Estrenimiento durante {dur} con {s1}", {
        "dur": ["3 dias","4 dias","5 dias","varios dias"],
        "s1": ["sin vomitos","calambres leves","sin sangre en heces","sin fiebre","leve incomodidad abdominal"],
    }),
    ("Cansancio {qual} durante {dur} con {s1}", {
        "qual": ["leve","moderado","generalizado","persistente"],
        "dur": ["una semana","varios dias","5 dias"],
        "s1": ["sin otros sintomas","buen apetito","sin fiebre","sin perdida de peso"],
    }),
    ("Dolor de garganta {qual} con {s1}", {
        "qual": ["leve","rasquido","irritativo","leve molestia"],
        "s1": ["sin fiebre","sin dificultad para deglutir","sin exudado","sin adenopatias"],
    }),
    ("Insomnio durante {dur} con {s1}", {
        "dur": ["una semana","varias noches","5 dias","mas de una semana"],
        "s1": ["sin otros sintomas","relacionado con estres","sin efectos secundarios de medicacion","por lo demas se encuentra bien"],
    }),
    ("Nauseas {qual} durante {dur} sin {s1}", {
        "qual": ["leves","intermitentes","moderadas"],
        "dur": ["un dia","2 dias","varias horas"],
        "s1": ["vomitos","diarrea","fiebre","dolor significativo"],
    }),
    ("Erupcion {type} en {loc} presente desde hace {dur}", {
        "type": ["pruriginosa","seca","descamativa","eritematosa"],
        "loc": ["manos","pies","cuello","pecho","espalda"],
        "dur": ["2 dias","3 dias","una semana","varios dias"],
    }),
    ("Control de tension arterial con {s1} y {s2}", {
        "s1": ["medicacion bien tolerada","sin efectos secundarios","cifras controladas"],
        "s2": ["sin nuevas quejas","cumplimiento adecuado","sin cefalea","sin mareos"],
    }),
    ("Dolor {type} leve valorado en {score} sobre 10 sin {s1}", {
        "type": ["de rodilla","de hombro","de muneca","de cadera","de cuello"],
        "score": ["2","3","3-4","2-3"],
        "s1": ["limitacion funcional","alteracion del sueno","limitacion de la marcha"],
    }),
    ("Seguimiento de {condition} con {s1}", {
        "condition": ["hipertension controlada","diabetes bien manejada","alergias estacionales","eccema leve"],
        "s1": ["sin nuevas quejas","sintomas estables","buen cumplimiento","sin efectos adversos"],
    }),
]

# ═══════════════════════════════════════════════════════════════
#  HINDI (Romanized)
# ═══════════════════════════════════════════════════════════════

HI_EMERGENCY = [
    ("{sev} seene ka dard jo {loc} tak failta hai, saath mein {s1} aur {s2}", {
        "sev": ["Tivra","Gambhir","Asahniya","Bahut tez","Bahut gambhir","Aniyantrit"],
        "loc": ["baaye haath","jawde","peeth","baaye kandhe","dono haath","gardan"],
        "s1": ["bahut pasina","thanda pasina","diaforesis","palor"],
        "s2": ["matli","ulti","saans lene mein takleef","chakkar","bahut kamzori","behoshi jaisi feeling"],
    }),
    ("Achanak {q} behoshi, {r}", {
        "q": ["mukammal","anjaani","dekhne waalon ke saamne","choti","lambi"],
        "r": ["kisi uttejana par koi pratikriya nahi","awaaz sunne par koi jawab nahi","jagaana mushkil hai",
              "zameen par gire mile","dard par bhi koi pratikriya nahi"],
    }),
    ("{sev} saans lene mein taklif, {s1} aur {s2}", {
        "sev": ["Bahut gambhir","Atyant","Janleva","Tivra","Badti hui"],
        "s1": ["poore vaakya bol nahi pa raha","sirf ek ek shabd bol pa raha","honth neele pad rahe hain","oxygen bahut kam hai"],
        "s2": ["ungliyan neeli pad rahi hain","saans ki awaaz aa rahi hai","bahut tez saans chal rahi hai","saans lene mein bahut mehnat"],
    }),
    ("{sev} allergic pratikriya, {s1} aur {s2}, {trigger} ke baad", {
        "sev": ["Gambhir","Janleva","Atyant","Bahut tez"],
        "s1": ["gala sujna","jeebh sujna","chehra sujna","saans raaste mein rukaavat"],
        "s2": ["nigal nahi pa raha","saans nahi le pa raha","blood pressure girta ja raha hai","poore sharir par daane"],
        "trigger": ["makkhi ke kaatne","moongfali","machli","penicillin","latex","wasp ke daank"],
    }),
    ("{q} sardard jo {desc} tha, saath mein {s1}", {
        "q": ["Achanak aaya bahut tez","Tivra","Atyant","Jeevan ka sabse bada"],
        "desc": ["jeevan mein kabhi itna nahi hua tha","bijli giri jaisa","sir mein dhamaka jaisa","zyada se zyada takleef"],
        "s1": ["gardan akad gayi","roshni se takleef aur ulti","hosh mein badlaav","gardan mein akadahat aur bukhar"],
    }),
    ("Stroke ke lakshan: {s1}, {s2} aur {s3}", {
        "s1": ["chehre ka daahina hissa latakna","chehre ka baaya hissa latakna","achanak chehre ki asymmetry"],
        "s2": ["daahine haath mein kamzori","baaye haath mein kamzori","haath uthane mein takleef"],
        "s3": ["bolne mein ladkhalahat","bolne mein takleef","kuch bol nahi pa raha","shabd dhundhne mein pareshani"],
    }),
    ("{type} khoon beh raha hai {source} se jo {treatment} se nahi ruk raha", {
        "type": ["Gambhir","Bahut zyada","Dhamni ka","Aniyantrit"],
        "source": ["gehre ghav se","pedu ke ghav se","pet ke ghav se","taang ke ghav se","sar ke ghav se"],
        "treatment": ["seedha dabaav se","tourniquet se","ghav bharke bhi","dabav ki patti se"],
    }),
    ("Bahut tez bukhar {temp} ke saath {s1} jo {dur} raha", {
        "temp": ["104F","105F","40.5C","40C","41C"],
        "s1": ["daure pade","mirchhiyan aayi","puri body kaanpne lagi","focal daure"],
        "dur": ["3 minute","5 minute","2 minute se zyada","lagbhag 4 minute"],
    }),
    ("Pet mein asahniya dard {s1} aur {s2} ke saath", {
        "s1": ["pet bilkul kathor ho gaya","pura pet tight ho gaya","rebound tenderness","sabhi jagah guarding"],
        "s2": ["ulti mein khoon","hematemesis","aankhon se khoon","kale rang ka mala","perforashion ke lakshan"],
    }),
    ("{age} ko {state} mein paya {s1} ke saath", {
        "age": ["Bujurg mariz","Yuva vayask","Adhyavayas mard","Bacha","Kismaar"],
        "state": ["behosh","gira hua","zameen par behosh","seedhi saans nahi le raha","nabs nahi"],
        "s1": ["nabs nahi mil rahi","saans nahi aa rahi","mautiyani saans","aankhein band ho gayi","honth neele"],
    }),
    ("{type} gambhir chot ke saath {s1} aur {s2}", {
        "type": ["Sir mein","Sine mein","Pet mein","Reedh ki haddi mein","Pelvis mein"],
        "s1": ["GCS 3","behoshi","dimagi halat kharaab","confusion aur utkantha"],
        "s2": ["khoon beh raha hai","haddi dikhti hai","andar khoon behne ke lakshan","shock"],
    }),
    ("Diabetic mariz ka blood glucose {level} aur {s1} aur {s2}", {
        "level": ["600 se zyada","30 se kam","bahut kam","500 mg/dL","700 mg/dL"],
        "s1": ["hosh nahi raha","daure pade","koi pratikriya nahi","bahut bheegi confusion"],
        "s2": ["bahut pasina","Kussmaul wali saans","saanson mein meethi badboo","bahut kamzori"],
    }),
    ("Opioid ki zyada matra se {s1} aur {s2}", {
        "s1": ["aankhein bilkul chhoti","saans bahut dheemi","hosh nahi","mirchi aa gayi"],
        "s2": ["cyanosis","dil ki dhadkan bahut dheemi","blood pressure bahut kam","saans ruk rahi hai"],
    }),
    ("Aortic dissection ka shak: {s1} jo {loc} tak failta hai aur {s2}", {
        "s1": ["seene mein tezaab jaisa dard","peeth mein phaad jaisi takleef","achanak tez seene mein dard"],
        "loc": ["peeth tak","pet tak","kandhe ki haddiyon ke beech tak","gardan tak"],
        "s2": ["dono haaton mein alag alag blood pressure","chakkar aakar gire","taangon mein kamzori"],
    }),
    ("Pulmonary embolism ka shak: {s1}, {s2} aur {s3}", {
        "s1": ["achanak pleuritic chest pain","tez dyspnea","achanak seene mein khinchav"],
        "s2": ["oxygen 80 percent","bahut tez heart rate","cyanosis"],
        "s3": ["lambi flight ke baad","surgery ke baad","pehle se DVT tha","bahut der tak leta raha"],
    }),
]

HI_URGENT = [
    ("Tez bukhar {temp} ke saath {s1} aur {s2}", {
        "temp": ["102F","103F","39.5C","39C","102.8F","104F","38.9C","39.3C","39.8C","39.6C","38.8C","40C"],
        "s1": ["gale mein bahut dard","nigalne mein takleef","tonsil suji hue","kaan mein dard bhi"],
        "s2": ["thook tapakna","awaaz badal gayi","gardan ke ganthe suji","daant nahi khul rahe"],
    }),
    ("{qual} dard {loc} mein {s1} ke saath", {
        "qual": ["Madhyam","Badta hua","Lagaataar","Tez se tez hota"],
        "loc": ["neeche daahini taraf","upar daahini taraf","upar bayi taraf","pet ke beech mein"],
        "s1": ["matli aur ulti","bhookh nahi lagi","halki bukhar","guarding","rebound takleef"],
    }),
    ("{bone} mein sambhavit fracture {mechanism} ke baad {s1} aur {s2} ke saath", {
        "bone": ["kalai mein","tobhde mein","ankle mein","collarbone mein","ungli mein"],
        "mechanism": ["haath phailake girne ke baad","seedhi chot ke baad","khel mein chot lagne ke baad","unchaai se girne"],
        "s1": ["bahut sujan","foran sujan aa gayi"],
        "s2": ["neela pad gaya","chune par dard","hilaa nahi sakta","tedha dikhta hai"],
    }),
    ("Lagaataar ulti {dur} se {s1} ke saath", {
        "dur": ["6 ghante","8 ghante","12 ghante","poore din","10 ghante se zyada"],
        "s1": ["paani bhi nahi ruk raha","dehydration ke lakshan","muh sukha","peshab kam ho gaya"],
    }),
    ("Kaan mein {qual} dard {s1} aur {s2} ke saath", {
        "qual": ["bahut tez","dhadkanta","lagaataar","badhta hua"],
        "s1": ["peela discharge","khoon aa raha hai","haare rang ka discharge"],
        "s2": ["sunai kam de raha hai","kaan mein awaaz","chakkar aa rahe hain"],
    }),
    ("Peshab ki takleef {s1}, {s2} aur {s3} ke saath", {
        "s1": ["jalan ke saath peshab","bahut dard ke saath peshab","baar baar peshab"],
        "s2": ["peshab mein khoon","laal rang ka peshab","khoon dikhta hai"],
        "s3": ["kamar mein dard","peethe mein dard","seene ke neechle hisse mein dard","bukhar 38.5C"],
    }),
    ("Migraine {s1}, {s2} aur {s3} ke saath", {
        "s1": ["aankhon ke aage roshni chamakti hai","scintillating scotoma","adhi ankh andheri"],
        "s2": ["ulti","dawa kaam nahi kar rahi","projective vomiting"],
        "s3": ["roshni se bahut takleef","awaaz se takleef","72 ghante se zyada","usual dawa kaam nahi ki"],
    }),
    ("{body} mein moch {mechanism} ke baad {s1} aur {s2} ke saath", {
        "body": ["Takhne","Ghutne","Kalai","Kandhe"],
        "mechanism": ["mochne ke baad","khel mein chot","girne ke baad"],
        "s1": ["bahut sujan","foran sujan"],
        "s2": ["chalna nahi ho raha","hilana nahi ho raha","dabane par bahut dard","neela pad gaya"],
    }),
    ("Daane {pattern} {s1} aur {s2} ke saath", {
        "pattern": ["poore torso par failte","haath paon tak faile","chehra aur tane par"],
        "s1": ["halki bukhar 38C","temperature 37.8C","hafif bukhar"],
        "s2": ["jodon mein dard","lymph nodes suji","khujli","chamdi ubhar rahi"],
    }),
    ("Bachche ko {temp} bukhar {dur} se {s1} ke saath", {
        "temp": ["103F","102.5F","39C","39.5C"],
        "dur": ["2 din","3 din","48 ghante","72 ghante"],
        "s1": ["peshab kam ho gaya","8 ghante se diaper nahi bheega","dehydration ke lakshan","sust hai","bahut rona"],
    }),
    ("Cellulitis {loc} mein {s1} aur {s2} ke saath", {
        "loc": ["taang mein","baanh mein","chehra mein","haath mein","paaon mein"],
        "s1": ["laal rang badh raha hai","barhti laal rekha","garmahat aur sujan"],
        "s2": ["bukhar 38.5C","lymphangitis","ganthe suji","oral antibiotic kaam nahi ki"],
    }),
    ("Asthma ka daura {s1} aur {s2} ke saath", {
        "s1": ["moderate saans ki seeti","saans lene mein seeti ki awaaz","diffuse seetis"],
        "s2": ["peak flow 50%","bronchodilator kaam nahi kiya","saans lene mein bahut mehnat"],
    }),
    ("Urinary tract infection upper parts mein {s1} aur {s2} ke saath", {
        "s1": ["tez bukhar","thakaan","kaampna"],
        "s2": ["kamar mein dard","daahine peethe mein dard","matli"],
    }),
    ("Appendicitis ka shak {s1} aur {s2} ke saath", {
        "s1": ["pehle naabhi ke paas dard tha ab neeche daahini taraf","neeche daahini taraf takleef","McBurney positive"],
        "s2": ["bhookh nahi","halki bukhar","matli","ek baar ulti"],
    }),
    ("Vaginal bleeding {q} {trimester} mein {s1} ke saath", {
        "q": ["madhyam","bahut zyada","baar baar"],
        "trimester": ["pehli trimester mein","doosri trimester mein","teesri trimester mein"],
        "s1": ["marod","lower abdomen mein dard","pelvic dard","kandhe mein dard","pelvic pressure"],
    }),
    ("{qual} sir dard {loc} mein {dur} se {s1} ke saath", {
        "qual": ["Tez","Moderate","Lagaataar","Tez se tez hota"],
        "loc": ["ek taraf","dono taraf","saamne ki taraf","peeche ki taraf","sir ke upar"],
        "dur": ["2 ghante","kuch ghante","subah se","kal se","kuch din"],
        "s1": ["matli ke saath","roshni se takleef","awaaz se takleef","dawa se aaram nahi","ulti ke saath"],
    }),
    ("Peeth mein {qual} dard {dur} se {s1} ke saath", {
        "qual": ["tez","badta hua","lagaataar","ek taraf ka"],
        "dur": ["2 din se","kal se","subah se","ek ghante se","kuch ghante se"],
        "s1": ["bukhaar bhi hai","peshab mein jalan bhi","chalne mein takleef","aaram karne se aaram nahi"],
    }),
    ("{age} ko {type} mein chot {mechanism} ke baad {s1}", {
        "age": ["Bachche","Bujurg","Yuva","Khiladi"],
        "type": ["sir","haath","taang","kandhe","peeth"],
        "mechanism": ["girne ke baad","khelne mein","dabbe se","cycle se girne ke baad"],
        "s1": ["sujan aur dard","hilane mein takleef","neela pad gaya","dard ka ehsaas badh raha hai"],
    }),
]

HI_ROUTINE = [
    ("{qual} khansi {dur} se {s1} ke saath", {
        "qual": ["Halki","Sukhi","Balgam wali","Baar baar","Thodi si","Kabhi kabhi","Kam"],
        "dur": ["3 din","4 din","5 din","ek hafte","kuch dinon","2 din","6 din","10 din"],
        "s1": ["bukhar nahi","saans lene mein koi takleef nahi","gale mein thodi si jalan","saaf balgam",
               "koi systemic lakshan nahi","dheere dheere theek ho raha","koi seeti ki awaaz nahi","thodi naak band"],
    }),
    ("{type} {loc} mein {s1} ke saath", {
        "type": ["Daane","Chamdi par nishan","Khujli"],
        "loc": ["baanh par","kamar par","taang par","peethe par","gardan par","pet par"],
        "s1": ["koi aur lakshan nahi","thodi khujli","bukhar nahi","2 din se stable","failte nahi"],
    }),
    ("{qual} kamar mein dard {cause} ke baad {treatment} se theek hota", {
        "qual": ["Halka","Sust","Thoda sa"],
        "cause": ["bhaari saman uthane ke baad","zyada der baithne ke baad","baagbaani ke baad"],
        "treatment": ["aaram karne se","bina nuskhe wali dawa se","garmi lagane se","posture badalne se"],
    }),
    ("Naak beh rahi hai aur {s1} {type} ki tarah lag raha hai", {
        "s1": ["chhinkein aa rahi hain","naak band hai","aankhon se paani","aankhon mein khujli"],
        "type": ["mausami allergy","nasal allergy","sardi jaisi","viral infection jaisi"],
    }),
    ("{qual} sardard jo {treatment} se theek ho jaata hai", {
        "qual": ["Halka","Tension wala","Aage ki taraf halka","Dono taraf halka"],
        "treatment": ["bina nuskhe ki dawa se","paracetamol se","andheri kamre mein aaram se","paani peene se"],
    }),
    ("{loc} par {type} jo {status}", {
        "type": ["chhhota sa kat","khuraach","ghaaon"],
        "loc": ["ungli","haath","baanh","taang","paaon","ghutna"],
        "status": ["khoon band ho gaya","saaf kar diya","patti bandh li","apne aap ruk gaya"],
    }),
    ("{dur} se kabz {s1} ke saath", {
        "dur": ["3 din","4 din","5 din","kuch dinon"],
        "s1": ["ulti nahi","thoda si ainth","stool mein khoon nahi","bukhar nahi","thodi si takleef"],
    }),
    ("{qual} thakaan {dur} se {s1} ke saath", {
        "qual": ["Halki","Thodi si","Saari body mein","Lagaataar"],
        "dur": ["ek hafte","kuch dinon","5 din"],
        "s1": ["koi aur lakshan nahi","khana theek se kha raha","bukhar nahi","weight loss nahi"],
    }),
    ("{qual} gale mein dard {s1} ke saath", {
        "qual": ["Halka","Kharkharahat","Thoda sa irritation","Halki takleef"],
        "s1": ["bukhar nahi","nigalne mein koi takleef nahi","koi phulaa hissa nahi","koi ganth nahi"],
    }),
    ("Neend nahi aa rahi {dur} se {s1}", {
        "dur": ["ek hafte","kaafi raaton se","5 din","ek hafte se zyada"],
        "s1": ["koi aur takleef nahi","tension ki wajah se","dawa ka koi asar nahi","baaki sab theek hai"],
    }),
    ("{qual} matli {dur} se bina {s1} ke", {
        "qual": ["Halki","Baar baar","Thodi si"],
        "dur": ["ek din","2 din","kuch ghante"],
        "s1": ["ulti ke","dast ke","bukhar ke","kisi bade dard ke"],
    }),
    ("{type} daane {loc} par jo {dur} se hain", {
        "type": ["khujli wale","sukhe","laal rang ke","gulaabi"],
        "loc": ["haath par","paaon par","gardan par","sine par","peethe par"],
        "dur": ["2 din","3 din","ek hafte","kuch dinon"],
    }),
    ("Blood pressure ki routine check-up {s1} ke saath", {
        "s1": ["dawa theek se chal rahi hai","koi side effects nahi","BP control mein hai","koi nai shikayat nahi"],
    }),
    ("{type} mein halka dard jo {score} mein se {score_val} hai aur {activity} mein koi takleef nahi", {
        "type": ["ghutne","kandhe","kalai","kamar","gardan"],
        "score": ["10"],
        "score_val": ["2","3","3-4","2-3"],
        "activity": ["roz ke kaam","chalna","sona","kaam karna"],
    }),
    ("{condition} ka follow-up {s1} ke saath", {
        "condition": ["controlled BP","theek se manage diabetes","mausami allergy","halki eczema"],
        "s1": ["koi nayi shikayat nahi","lakshan stable hain","dawa theek se le raha","koi side effects nahi"],
    }),
    ("Aankhon mein {s1} jo {dur} se hai aur {s2}", {
        "s1": ["halki jalan","thodi si lali","paani aana","khujli","thoda sa dard"],
        "dur": ["kal se","2 din se","subah se","kuch ghante se","3 din se"],
        "s2": ["koi vision mein badlaav nahi","roshni se koi takleef nahi","sujan nahi","bilkul halka hai"],
    }),
    ("Haath ya paaon mein {s1} jo {dur} se {s2}", {
        "s1": ["thodi si sujan","halka dard","thoda sa akadahat","halki khujli"],
        "dur": ["kal se","2 din se","kuch ghante se","subah se","3 din se"],
        "s2": ["bilkul halka hai","chal phir sakta hai","koi numbness nahi","dheere dheere theek ho raha"],
    }),
]

# ═══════════════════════════════════════════════════════════════
#  BENGALI (Romanized)
# ═══════════════════════════════════════════════════════════════

BN_EMERGENCY = [
    ("{sev} buke batha {loc} porjonto chharhiye jachhhe, shathe {s1} o {s2}", {
        "sev": ["Tibra","Gambhir","Ashoho","Khub tez","Bhoyaboh"],
        "loc": ["bam hate","chomale","pitthe","bam kandhe","dui hate","ghare"],
        "s1": ["profuse ghaam hochhe","thanda ghaam hochhe","diaforesis","paandur"],
        "s2": ["bomi bomi lagchhe","bomi hochhe","shash nite koshto hochhe","matha ghurochhe","khub durbolta"],
    }),
    ("Hothat {q} ajnaan hoyeche, {r}", {
        "q": ["mukkhyo","akasmik","shakkhider shomakhe","chomka","lambasmay"],
        "r": ["kono uddipanay sara dichhen na","dak shune kono uttoro nai","jagano jachhhe na",
              "morete pore pai","bedhona dileyo sara dichhen na"],
    }),
    ("{sev} shash neoar koshto, {s1} o {s2}", {
        "sev": ["Tibra","Otyonto","Jibonomarokar","Acute","Barhte thaka"],
        "s1": ["pouro baakyo bolte parchen na","ekta ekta shabd bolchen","thoth neel hochhe","oxygen khub kom"],
        "s2": ["anguler aga neel hochhe","shash neoar awaaz hochhe","shasher hare khub beshi","porashonar shorira"],
    }),
    ("{sev} allergic protikriya, {s1} o {s2}, {trigger} er pore", {
        "sev": ["Gambhir","Jibonomarokar","Otyonto","Bhoyaboh"],
        "s1": ["gola fuley gechhe","jib fuley gechhe","mukh fuley gechhe","shasher raasta bondho hochhe"],
        "s2": ["gilte parchhen na","shas nite parchhen na","BP pore jachhhe","shara gaaye daana"],
        "trigger": ["modhumakor kaad","badam","machh","penicillin","latex","dhoroner daank"],
    }),
    ("{q} mathabatha jeta {desc} chilo, shathe {s1}", {
        "q": ["Hothat tibra","Jiboner shobcheye baro","Veetikor","Otyonto"],
        "desc": ["jiboner shobcheye kharap","khonokaalo anubhob hoyni","bijli pore jaoar moto","shomosto shoktimatay"],
        "s1": ["ghaar shokto hoyeche","aloay koshto o bomi","ghosh poribortito hoyeche","ghaar shokto o jor"],
    }),
    ("Stroke er laakhhon: {s1}, {s2} o {s3}", {
        "s1": ["mukher dan dik jhule porechhe","mukher bam dik jhule porechhe","hothat mukher boshom hoyeche"],
        "s2": ["dan hate durbolta","bam hate durbolta","hate tulte parchhen na"],
        "s3": ["kotha joriye jachhhe","kotha bolte parchhen na","kichhu bolte parchhen na","shabd khujte parchhen na"],
    }),
    ("{type} roktopaat {source} theke {treatment} e bonto hocchhe na", {
        "type": ["Tibra","Atyadhik","Dhamani theke","Maatratirikto"],
        "source": ["gabhir ghot theke","khancho r ghot theke","peter ghot theke","paer ghot theke"],
        "treatment": ["seedha chap diye","tornikiyet lagiye","ghot bhore","chaap er potti die"],
    }),
    ("Khub beshi jor {temp} er shathe {s1} jo {dur} dhore chilo", {
        "temp": ["40C","40.5C","41C","40.2C"],
        "s1": ["khichhuni hoyeche","shara gae kaanpuni hoyeche","focal khichhuni hoyeche"],
        "dur": ["teen minute","paanch minute","dui minuter beshi","chaar minute er moto"],
    }),
    ("Pete ashoho batha {s1} o {s2} er shathe", {
        "s1": ["pet shokto hoyeche","sharo pete shokto","rebount shoho batha","shobarkhane guarding"],
        "s2": ["roktobomi hochhe","hematemesis hochhe","kaalo potkhana","rokto diye potkhana","perforashioner laakhhon"],
    }),
    ("{age} ke {state} obosthay paoa gelo {s1} er shathe", {
        "age": ["Brishkhoro rogir","Jubok er","Madhyabayoshi manusher","Shishur","Kishorer"],
        "state": ["ajnaan","pore","morete ajnaan","shadharon shash nite parchhen na","nabs nei"],
        "s1": ["nabs paoa jachhhe na","shas asche na","mrityukalin shas","chokh bondho hoyeche","thoth neel"],
    }),
    ("{type} gambhir aaghater shathe {s1} o {s2}", {
        "type": ["Mathay","Buke","Pete","Merorodonde","Pelvis e"],
        "s1": ["GCS 3","ajnaan","mansik obostha kharap","confusion o oboirogyo"],
        "s2": ["rokto porchhhe","haddi dekhha jachhhe","bhitorot rokto porrar laakhhon","shock"],
    }),
    ("Diabetis er rogir roktoshorkara {level} o {s1} o {s2}", {
        "level": ["600 er beshi","30 er kom","khub kom","500 mg/dL","700 mg/dL"],
        "s1": ["ajnaan","khichhuni hoyeche","kono protikriya nei","gambhir confusion"],
        "s2": ["khub ghaam hochhe","Kussmaul er shas","misthigondho shas","khub durbolta"],
    }),
    ("Opioid er atirikto matra theke {s1} o {s2}", {
        "s1": ["chokher tara khub chhoto","shas khub dheeme","ajnaan","khichhuni"],
        "s2": ["cyanosis","hridoy khub aaste","BP khub kom","shas bondho hochhe"],
    }),
    ("Aortic dissection er shondeho: {s1} {loc} porjonto o {s2}", {
        "s1": ["buke teekhono katar moto batha","pitthe phaad jaoa takleef","hothat buke tibra batha"],
        "loc": ["pitthe","pote","kandher haddir moddhe","ghare"],
        "s2": ["dono haater BP alag alag","chokker moto pore gelo","paer durbolta"],
    }),
    ("Pulmonary embolism er shondeho: {s1}, {s2} o {s3}", {
        "s1": ["hothat pleuritic chest pain","tibra dyspnea","hothat buke chaap"],
        "s2": ["oxygen 80 percent","khub tez heart rate","cyanosis"],
        "s3": ["lambasmay flight er pore","surgery er pore","aager DVT","onek din shuye chilo"],
    }),
]

BN_URGENT = [
    ("Beshi jor {temp} er shathe {s1} o {s2}", {
        "temp": ["39C","39.5C","39.2C","38.9C","39.8C","40C","38.8C","39.3C","39.6C","39.1C","39.7C","38.7C"],
        "s1": ["gole tibra batha","gilte koshto hochhe","tonsil fuley gechhe","kaan e batha o"],
        "s2": ["thook porhchhe","awaaz bodole gechhe","gharer ganthe fulechhe","daant khulte parchhen na"],
    }),
    ("{qual} batha {loc} e {s1} er shathe", {
        "qual": ["Madhyom","Ullo kheyaLo","Lagaataar","Tez theke teztar hota"],
        "loc": ["nicher dan dike","upar dan dike","upar bam dike","pete r moddhe"],
        "s1": ["bomi bomi bhab o bomi","khide nei","halka jor","guarding","rebound batha"],
    }),
    ("{bone} e shombhaby fhatal {mechanism} er pore {s1} o {s2} er shathe", {
        "bone": ["kobji","ankle","anubahu","collar bone","angulay"],
        "mechanism": ["haath sar kore porar pore","seedha aaghater pore","khela dhula te aaghater pore"],
        "s1": ["khub fulon","eki shathe fulon"],
        "s2": ["kaalo dag porche","chaap dilei batha","holatei parchhen na","tedha dekhaachhe"],
    }),
    ("Lagaataar bomi {dur} dhore {s1} er shathe", {
        "dur": ["chhoy ghanta","aath ghanta","baro ghanta","shara din","dash ghantarer beshi"],
        "s1": ["paanio rakhte parchhen na","dehydration er laakhhon","mukh shukno","proshrab kom hochhe"],
    }),
    ("Kaane {qual} batha {s1} o {s2} er shathe", {
        "qual": ["khub tez","dhak dhak","lagaataar","barhte thaka"],
        "s1": ["haaluda discharge","rokto berchhhe","shobuj discharge"],
        "s2": ["kom shunchhen","kaane awaaz","matha ghurochhe"],
    }),
    ("Prabab er shomoshsha {s1}, {s2} o {s3} er shathe", {
        "s1": ["proshrab e jvala","khub batha te proshrab","baar baar proshrab"],
        "s2": ["prababe rokto","laal proshrab","rokto dekhha jaachhe"],
        "s3": ["pitthe batha","kaanghare batha","jore er laakhhon","38.5C jor"],
    }),
    ("Migraine {s1}, {s2} o {s3} er shathe", {
        "s1": ["chokhe alo jhilmil","scintillating scotoma","adhaandhor"],
        "s2": ["bomi","dawa kaje aschhe na","projective bomi"],
        "s3": ["aloy khub koshto","shabd e koshto","72 ghantarer beshi","usual dawa kaje laageni"],
    }),
    ("{body} te moch {mechanism} er pore {s1} o {s2} er shathe", {
        "body": ["Ghore","Ghutute","Kobji te","Kandhe"],
        "mechanism": ["mochar pore","khela dhula te","porar pore"],
        "s1": ["khub fulon","ekhoni fulon"],
        "s2": ["hathte parchhen na","holatei parchhen na","chaap dilei batha","kaalo dag"],
    }),
    ("Daana {pattern} {s1} o {s2} er shathe", {
        "pattern": ["shara torso te chharhiye","hate paaye chharhiye","mukh o buke"],
        "s1": ["halka jor 38C","temperature 37.8C","hafif jor"],
        "s2": ["gantey batha","lymph node fula","chulkani","chamra uthchhe"],
    }),
    ("Shishur {temp} jor {dur} dhore {s1} er shathe", {
        "temp": ["39C","39.5C","38.9C","39.2C"],
        "dur": ["dui din","tin din","48 ghanta","72 ghanta"],
        "s1": ["proshrab kom hochhe","8 ghanta diaper bhejeni","dehydration er laakhhon","sust hochhe","khub kaadchhe"],
    }),
    ("Cellulitis {loc} e {s1} o {s2} er shathe", {
        "loc": ["paaye","bahute","mukhe","haate","paer patay"],
        "s1": ["laal rang barhchhe","barhte thaka laal dago","goromi o shorota"],
        "s2": ["38.5C jor","lymphangitis","gantha fula","mukher antibiotic kaje laageni"],
    }),
    ("Asthmar attack {s1} o {s2} er shathe", {
        "s1": ["madhyom saans er seeti","shunchhen saans er seeti","difuse seetis"],
        "s2": ["peak flow 50%","bronchodilator kaje laageni","shas neoay khub koshto"],
    }),
    ("Upper urinary tract infection {s1} o {s2} er shathe", {
        "s1": ["tez jor","onek thanda laagchhe","kaanpuni"],
        "s2": ["kaanghare batha","dan pitthe batha","bomi bomi bhab"],
    }),
    ("Appendicitis er shondeho {s1} o {s2} er shathe", {
        "s1": ["prate nabir kachhe batha chilo ekhon nicher dan dike","nicher dan dike batha","McBurney positive"],
        "s2": ["khide nei","halka jor","bomi bomi bhab","ekbaar bomi hoyeche"],
    }),
    ("Yonibhongo theke rokto porhchhe {q} {trimester} e {s1} er shathe", {
        "q": ["madhyom","atyadhik","baar baar"],
        "trimester": ["prothom trimester e","dwitiya trimester e","tritiyo trimester e"],
        "s1": ["marod hochhe","nicher pote batha","pelvik batha","kandhe batha","pelvik chaap"],
    }),
    ("{qual} mathabatha {loc} e {dur} dhore {s1} er shathe", {
        "qual": ["Tez","Madhyom","Lagaataar","Barhte thaka"],
        "loc": ["ek dike","dui dike","shamne","pichone","mathay upar"],
        "dur": ["dui ghanta","koyekhonta","shokal theke","gotokal theke","koyekdin"],
        "s1": ["bomi bomi lagchhe","aloy koshto hochhe","awaaz e koshto","dawa kaje laagche na","bomi hochhe shathe"],
    }),
    ("Pitthe {qual} batha {dur} dhore {s1} er shathe", {
        "qual": ["tez","barhte thaka","lagaataar","ek diker"],
        "dur": ["dui din dhore","gotokal theke","shokal theke","ek ghonta dhore","koyekhonta dhore"],
        "s1": ["jor o achhe","proshrab e jvala o achhe","hathte koshto hochhe","bishrame kamaachhe na"],
    }),
    ("{age} er {type} e chot {mechanism} er pore {s1}", {
        "age": ["Shishur","Brishkhor manusher","Jubaker","Khilari"],
        "type": ["mathay","haate","paaye","kandhe","pitthe"],
        "mechanism": ["porar pore","khela dhula te","accident e","cycle theke porar pore"],
        "s1": ["fulon o batha achhe","holatei parchhen na","kaalo dag hochhe","batha barhchhe"],
    }),
]

BN_ROUTINE = [
    ("{qual} kashi {dur} dhore {s1} er shathe", {
        "qual": ["Halka","Shukno","Balgom wala","Baar baar","Thoda","Kabhi kabhi","Kom"],
        "dur": ["tin din","char din","paanch din","ek shaptah","koyekdin","dui din","chhoy din","dosh din"],
        "s1": ["jor nei","shas neoay kono koshto nei","gole halka jvala","shaffo balgom",
               "kono systemic laakhhon nei","aaste aaste bhalo hochhe","kono seeti nei","halka naak bondho"],
    }),
    ("{type} {loc} te {s1} er shathe", {
        "type": ["Fushkuri","Daag","Bhar"],
        "loc": ["bahute","kaanghare","paaye","pitthe","ghare","pote"],
        "s1": ["kono aaro laakhhon nei","halka chulkani","jor nei","dui din dhore stable","chharhachhe na"],
    }),
    ("{qual} pitthe batha {cause} er pore {treatment} te bhalo hochhe", {
        "qual": ["Halka","Sust","Thoda"],
        "cause": ["bhari jinish toloar pore","onek kshhon boshe thakar pore","bagan kajar pore"],
        "treatment": ["bishram niye","OTC dawa diye","goromi lagiye","posture bodole"],
    }),
    ("Naak die paani porhchhe o {s1} {type} er moto laagchhe", {
        "s1": ["hhachhi hochhe","naak bondho","chokh theke paani","chokhe chulkani"],
        "type": ["mausumi allergy","nasal allergy","shardi","viral infection"],
    }),
    ("{qual} mathabatha jo {treatment} te kome jay", {
        "qual": ["Halka","Tension wali","Shomukhe halka","Dui dike halka"],
        "treatment": ["OTC dawa te","paracetamol e","andhar ghore bishram niye","paani kheye"],
    }),
    ("{loc} te {type} je {status}", {
        "type": ["chhoto kata","khuchhunor daag","ghoto"],
        "loc": ["angulay","haate","bahute","paaye","ghutute"],
        "status": ["rokto bondho hoyeche","shaffo kora hoyeche","potti bana hoyeche","aponey rokto themeche"],
    }),
    ("{dur} dhore koshthokaththinyo {s1} er shathe", {
        "dur": ["tin din","char din","paanch din","koyekdin"],
        "s1": ["bomi nei","halka petbatha","potkhana te rokto nei","jor nei","halka ashonthi"],
    }),
    ("{qual} klanti {dur} dhore {s1} er shathe", {
        "qual": ["Halka","Madhyom","Shara gaaye","Lagaataar"],
        "dur": ["ek shaptah","koyekdin","paanch din"],
        "s1": ["kono aaro laakhhon nei","thikthak khaachhen","jor nei","wazan kome jaachhe na"],
    }),
    ("{qual} gole koshto {s1} er shathe", {
        "qual": ["Halka","Khakharo laagchhe","Halka jontrona","Thoda"],
        "s1": ["jor nei","gilte kono koshto nei","kono fula nei","kono gantha nei"],
    }),
    ("Ghoom hochhe na {dur} dhore {s1}", {
        "dur": ["ek shaptah","onek raat","paanch din","ek shaptaher beshi"],
        "s1": ["kono aaro koshto nei","tension er karone","doroner kono prabhhab nei","baki shob theek"],
    }),
    ("{qual} bomi bomi bhab {dur} dhore bina {s1} e", {
        "qual": ["Halka","Baar baar","Madhyom"],
        "dur": ["ek din","dui din","koyekhonta"],
        "s1": ["bomi te","dast e","jore te","baro batha te"],
    }),
    ("{type} fushkuri {loc} te je {dur} dhore achhe", {
        "type": ["chulkanir","shukno","laal","gulaabi"],
        "loc": ["haate","paaye","ghare","buke","pitthe"],
        "dur": ["dui din","tin din","ek shaptah","koyekdin"],
    }),
    ("Blood pressure er routine check {s1} er shathe", {
        "s1": ["dawa theek e chalten","kono side effect nei","BP niyontrone achhe","kono notun obhiyog nei"],
    }),
    ("{type} te halka batha je {score} er moddhe {score_val} o {activity} te kono koshto nei", {
        "type": ["ghutute","kandhe","kobji te","kaanghare","ghare"],
        "score": ["10"],
        "score_val": ["2","3","3-4","2-3"],
        "activity": ["protidin er kaaj","hatha","ghum","kaj"],
    }),
    ("{condition} er follow-up {s1} er shathe", {
        "condition": ["niyontrito BP","bhalo manage diabetes","mausumi allergy","halka eczema"],
        "s1": ["kono notun obhiyog nei","laakhhon stable","dawa theek e khachhen","kono side effect nei"],
    }),
    ("Chokhe {s1} je {dur} dhore achhe o {s2}", {
        "s1": ["halka jvala","thoda lali","paani asche","chulkani","halka batha"],
        "dur": ["gotokal theke","dui din dhore","shokal theke","koyekhonta dhore","tin din dhore"],
        "s2": ["drishti te kono badlaav nei","aloy kono koshto nei","fulon nei","khub halka"],
    }),
    ("Haate ba paaye {s1} je {dur} dhore {s2}", {
        "s1": ["halka fulon","thoda batha","halka akodh","thoda chulkani"],
        "dur": ["gotokal theke","dui din dhore","koyekhonta dhore","shokal theke","tin din dhore"],
        "s2": ["khub halka","hathte chalta parchhen","kono numbness nei","aaste aaste bhalo hochhe"],
    }),
]

# ═══════════════════════════════════════════════════════════════
#  GENERATE ALL
# ═══════════════════════════════════════════════════════════════

# ── Config: (easy_templates, hard_templates, label, language) ──
configs = [
    (EN_EMERGENCY, EN_EMERGENCY_HARD, "Emergency", "English"),
    (EN_URGENT,    EN_URGENT_HARD,    "Urgent",    "English"),
    (EN_ROUTINE,   EN_ROUTINE_HARD,   "Routine",   "English"),
    (ES_EMERGENCY, ES_EMERGENCY_HARD, "Emergency", "Spanish"),
    (ES_URGENT,    ES_URGENT_HARD,    "Urgent",    "Spanish"),
    (ES_ROUTINE,   ES_ROUTINE_HARD,   "Routine",   "Spanish"),
    (HI_EMERGENCY, HI_EMERGENCY_HARD, "Emergency", "Hindi"),
    (HI_URGENT,    HI_URGENT_HARD,    "Urgent",    "Hindi"),
    (HI_ROUTINE,   HI_ROUTINE_HARD,   "Routine",   "Hindi"),
    (BN_EMERGENCY, BN_EMERGENCY_HARD, "Emergency", "Bengali"),
    (BN_URGENT,    BN_URGENT_HARD,    "Urgent",    "Bengali"),
    (BN_ROUTINE,   BN_ROUTINE_HARD,   "Routine",   "Bengali"),
]

os.makedirs("dataset", exist_ok=True)

all_rows = []
lang_frames = {}

for easy_tmpl, hard_tmpl, label, language in configs:
    easy = generate(easy_tmpl, EASY_TARGET)
    hard = generate(hard_tmpl, HARD_TARGET)
    combined = easy + hard
    random.shuffle(combined)
    print(f"{language:<10} {label:<12} → {len(easy)} easy + {len(hard)} hard = {len(combined)}")
    for s in combined:
        row = {"text": s, "label": label, "language": language}
        all_rows.append(row)
        if language not in lang_frames:
            lang_frames[language] = []
        lang_frames[language].append(row)

# Save per-language CSVs to dataset/
for language, rows in lang_frames.items():
    lang_df = pd.DataFrame(rows)
    lang_df = lang_df.sample(frac=1, random_state=42).reset_index(drop=True)
    out_path = os.path.join("dataset", f"{language}.csv")
    lang_df.to_csv(out_path, index=False)
    print(f"Saved {out_path}: {len(lang_df)} rows")

df = pd.DataFrame(all_rows)
print(f"\nTotal: {len(df)} rows")
print(df.groupby(["language","label"])["text"].count().unstack())
