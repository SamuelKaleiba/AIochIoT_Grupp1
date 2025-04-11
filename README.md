# 🍇 Smart WineMaking – AI & IoT för hållbar vinodling

**Ett AI- och IoT-projekt från YH-utbildningen "AI och IoT" (BK24TR)**  
**Gruppmedlemmar:** Agne Dimaisate, Therese Andersson, Daniel Karlsson, Axel Gummesson  

---

## 🌱 Projektöversikt

Smart WineMaking är en **Minimum Viable Product (MVP)** som visar hur svenska druvodlare kan fatta datadrivna beslut med hjälp av AI och IoT. Genom simulering av sensorflöden och bildanalys demonstreras ett beslutstödsystem som kan upptäcka sjukdomar, optimera bevattning och förbättra skördekvalitet – även i klimat med korta växtsäsonger och höga fuktnivåer.

*Obs: Projektet använder mockup-sensordata i växthusmiljö för att simulera ett verkligt scenario.*

---

## 🎯 Projektmål

- ✅ Tidig upptäckt av sjukdomar med AI-bildanalys  
- ✅ Optimerad resursanvändning via sensordata och väderprognoser  
- ✅ Förbättrad druvkvalitet och stabil avkastning  
- ✅ Minskad miljöpåverkan  

---

## 🧠 Systemets huvudkomponenter

### 📷 AI för sjukdomsdetektion
- **Amazon Rekognition Custom Labels**  
  → Bilder laddas upp till S3  
  → Triggers med Lambda  
  → Resultat lagras i RDS (Microsoft SQL Server)

### 📡 IoT-infrastruktur (mockad)
- Sensorer (simulerade): markfuktighet, temperatur, luftfuktighet, ljus  
- **AWS IoT Core** hanterar mockup-data i realtid  
- Kommunikationen är simulerad för demonstration

### ☁️ Molntjänster och datahantering
- **Amazon S3** – lagring av bilder  
- **Amazon RDS** – lagring av sensorvärden och AI-resultat  

### 🤖 Chatbot och gränssnitt
- **Amazon Lex** – AI-chat för användarfrågor  
- **AWS Lambda** – logik och integration med väder- och sensor-API  
- **Frontend** – byggd i Streamlit

### 🌐 Externa API:er
- **SMHI** – väderdata baserat på koordinater  
- **OpenCage** – platsnamn → lat/long  

---

## 🧱 Arkitekturöversikt

Systemet bygger på tre nivåer:  
1. **Data Collection:** Mockup IoT-sensorer och användarens bilder  
2. **Cloud Services:** AI, API-anrop och datalagring  
3. **User Interaction:** Dashboard, chatbot och automatiska rekommendationer

---

## ⚠️ Identifierade utmaningar

- Begränsad datamängd för AI-träning  
- Internetuppkoppling i fält  
- Användares tillit till AI-rekommendationer  
- Robusthet hos hårdvara i växthusmiljö  

---

## 🧪 Exempel på användning

> _"Risk för mögel i sektion B – hög luftfuktighet och temperatur kombinerat med regnprognos. Rekommenderad åtgärd: besprutning inom 24h."_
