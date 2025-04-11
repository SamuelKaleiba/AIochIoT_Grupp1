# Steg-för-steg-guide för att träna en Amazon Rekognition Custom Labels-modell för vinrankor

Denna guide beskriver hur ni kan samla in, organisera, märka upp och förbereda era bilder av vinrankor för att träna en modell med Amazon Rekognition Custom Labels. Målet är att kunna skilja på sjuka och friska vinrankor, varpå modellens output i kombination med mock-sensordata kan användas för att ge rekommendationer om exempelvis bevattning.

---

## Steg 1: Samla in och välja bilder

### 1.1 Bilder på sjuka vinrankor  
- Använd de bilder ni redan har i er S3-bucket.
- Välj ut exempel som tydligt visar sjukdomstecken.

### 1.2 Bilder på friska vinrankor  
- Samla in bilder på friska vinrankor.  
- Säkerställ att bilderna är av god kvalitet och representerar olika ljus- och väderförhållanden.

---

## Steg 2: Namnge bilderna konsekvent

### 2.1 För sjuka vinrankor  
- Använd ett namnformat såsom:
  - `sick_vine_001.jpg`
  - `sick_vine_002.jpg`
  
### 2.2 För friska vinrankor  
- Använd ett namnformat såsom:
  - `healthy_vine_001.jpg`
  - `healthy_vine_002.jpg`
  
### 2.3 Prefix  
- Prefixen `sick_` respektive `healthy_` hjälper er att enkelt identifiera och sortera bilderna.

---

## Steg 3: Strukturera upp filerna i S3

### 3.1 Organisera i mappar  
- Skapa separata mappar (prefix) i er S3-bucket:
  - **sick/** för bilder på sjuka vinrankor.
  - **healthy/** för bilder på friska vinrankor.
  
### 3.2 Ladda upp bilder  
- Ladda upp respektive kategori av bilder till sin specifika mapp.

---

## Steg 4: Förbered datasetet för Rekognition Custom Labels

### 4.1 Starta ett nytt projekt  
- Logga in i AWS Management Console.
- Gå till **Amazon Rekognition** och välj **Custom Labels**.
- Skapa ett projekt, t.ex. "Vinrankor_Sjukdomsdetektion".

### 4.2 Importera datasetet  
- När ni importerar bilderna, peka på er S3-bucket och ange de två mapparna (`sick/` och `healthy/`).
- Dela upp datasetet i:
  - **Träningsdataset:** Exempelvis 80% av bilderna.
  - **Validerings-/Testdataset:** Exempelvis 20% av bilderna.

### 4.3 Etikettering  
- Eftersom ni använder **bildnivåklassificering**:
  - Alla bilder i mappen `sick/` ska märkas som **"sick"** eller **"sjuk"**.
  - Alla bilder i mappen `healthy/` ska märkas som **"healthy"** eller **"frisk"**.
- Detta alternativ kräver inte att ni manuellt ritar bounding boxes, vilket sparar tid.

---

## Steg 5: Träna och validera modellen

### 5.1 Starta modellträningen  
- Efter att datasetet importerats startar ni träningsprocessen i Konsolen.
- Konfigurera träningen enligt era preferenser och projektets krav.

### 5.2 Övervaka prestanda  
- Efter träningen kommer ni få tillgång till prestandamått (precision, recall, F1-score).
- Se till att både tränings- och valideringsdatasetet ger acceptabla resultat.

### 5.3 Utvärdera modellen  
- Använd en uppsättning testbilder som inte använts under träningen för att utvärdera modellens generaliseringsförmåga.

---

## Steg 6: Integrera med sensordata och ge rekommendationer

### 6.1 Kombinera bildanalys och sensordata  
- När modellen klassificerar en bild som "sick" (sjuk), kombinera resultatet med den mock-sensordata ni genererar.
- Skapa en logik som exempelvis kontrollerar om en sjuk bild och låga fuktvärden leder till en rekommendation om ökad bevattning.

### 6.2 Presentation av data  
- Designa ert gränssnitt (t.ex. konsolutskrift eller en enkel webbapp) där både bilderna, sensoravläsningarna och rekommendationerna visas.

---

## Sammanfattning

1. **Samla in bilder:** Välj ut representativa bilder för både sjuka och friska vinrankor.
2. **Konsekvent namngivning:** Använd tydliga namn med prefixen `sick_` och `healthy_`.
3. **Struktur i S3:** Organisera bilderna i separata mappar.
4. **Förbered datasetet:** Importera bilder till Rekognition Custom Labels och dela upp i tränings- och valideringsdata.
5. **Träna modellen:** Starta modellträning och utvärdera prestanda.
6. **Integrera med sensordata:** Kombinera modellens output med sensordata för att ge konkreta handlingsrekommendationer.

---

## Användning

1. **Spara filen:** Kopiera ovanstående text till en fil med namnet `instructions.md`.
2. **Konvertera till PDF:** Använd ett verktyg som Pandoc. Exempelkommando:

