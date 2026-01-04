#import "@preview/peace-of-posters:0.5.6" as pop

#set page("a0", margin: 0.8cm, flipped: true)
#set text(size: 30pt)
#let box-spacing = 0.7em
#set columns(gutter: box-spacing)
#set block(spacing: box-spacing)

#let mainColor = rgb("#500045")
#let secColor = rgb("#5f0000")
#let color = gradient.linear(mainColor,secColor)
#let radius = 16pt
#let inset = 30pt
#let default = (
  "body-box-args": (
    inset: inset,
    width: 100%,
    radius: (
      bottom-left: radius,
      bottom-right: radius
    )
  ),
  "body-text-args": (:),
  "heading-box-args": (
    inset: inset,
    width: 100%,
    fill: color,
    stroke: rgb(25, 25, 25),
    radius: (
      top-left: radius,
      top-right: radius
    )
  ),
  "heading-text-args": (
    font: "HSD Sans",
    fill: white,
  ),
  "title-box-args": (
    inset: inset,
    width: 100%,
    fill: color,
    stroke: rgb(25, 25, 25),
    radius: radius
  ),
  "title-text-args": (
    font: "HSD Sans",
    fill: white,
  )
)

#pop.set-theme(default)

#let logo_svg = bytes(read("assets/lips.svg").replace("__c1__", secColor.to-hex()))
#pop.title-box(
  "YALR - Yet Another Lip Reader",
  authors: "Richard Bihlmeier, Jannis Bollien",
  institutes: "ZDD @ HSD",
  keywords: "Lipreading · AV-HuBERT · MediaPipe · LRS2",
  logo: rotate(-20deg, circle(align(horizon, image(logo_svg)), fill: white, radius: 155pt, inset: -10pt)),
  title-size: 90pt,
  authors-size: 50pt,
  institutes-size: 50pt,
  keywords-size: 30pt
)

#columns(3,[
  #pop.column-box(heading: "Motivation / Problem")[
    - *Barrierefreiheit:* Unterstützung für gehörlose / schwerhörige Menschen
    - *Audioausfälle:* robust, wenn Audio fehlt, verrauscht oder gestört ist
    - *Sicherheitstechnik:* z. B. Einsatz-/Überwachungsszenarien ohne verwertbares Audio
    - *Ziel:* Satz-Level Lipreading: *Video (Mundbewegungen) #sym.arrow.r Text*
  ]

  // #pop.column-box(heading: "Ansatz")[
  //   - *End-to-End Inferenz-Pipeline* für Satz-Level Lipreading
  //   - Video #sym.arrow.r Mund-ROI @wiki:ROI #sym.arrow.r Modell #sym.arrow.r Text
  //   - Fokus auf stabile Inferenz und Demo-Tauglichkeit
  // ]

  #pop.column-box(heading: [Pipeline (Video #sym.arrow.r Mund-ROI #sym.arrow.r Text)])[
    Das Modell erwartet *standartisierte* Eingangsgrößen. (geglätteter Auschnitt der Mund-Region \[96x96 px\])
    1. *ROI-Extraktion:* Mund-Crop aus Landmarks mit *MediaPipe* @mediapipe_guide @mediapipe_pypi
    #v(5pt)
    #figure(caption: [
      *Augenecken* & *Nasenspitze* bilden T-Zone, mittels der Verkrümmung und Auschnitt berechnet werden 
    ])[
      #image("assets/landmarks.png", height: 300pt, width: 400pt)
    ]
    #v(5pt)
    2. *Vorverarbeitung:* Skalierung / Normalisierung der Crops, Sequenzaufbereitung
    3. *Inference:* AV-HuBERT im *evaluation mode*
    4. *Output:* Satzweise Textvorhersage (aktuell Englisch, wie Pretraining)
    #let arrow = bytes(read("assets/arrow.svg").replace("__c1__", mainColor.to-hex()))
    #let nn = bytes(read("assets/nn.svg").replace("__c1__", mainColor.to-hex()))
    #let paps = bytes(read("assets/paper.svg").replace("__c1__", mainColor.to-hex()))
    #figure(caption: [
        Pipeline (Datensatz für Beispiele: LRS3-TED @lrs3
      ])[
        #let h = 160pt
        #let ah = 80pt
        #let aw = 70pt
        #align(horizon,
          stack(dir: ltr, spacing: 5pt,
            for i in range(1, 4) {
              image("assets/p" + str(i) + ".png", height: h)
            },
            image(arrow, height:ah, width: aw, fit: "stretch"),
            for i in range(1, 4) {
              image("assets/p" + str(i) + "-markers.png", height: h)
            },
            image(arrow, height:ah, width: aw, fit: "stretch"),
            for i in range(1, 4) {
              image("assets/p" + str(i) + "-roi.png", height: h)
            },
            image(arrow, height:ah, width: aw, fit: "stretch"),
            image(nn, height: 140pt),
            image(arrow, height:ah, width: aw, fit: "stretch"),
            image(paps, height: 100pt),
          )
        )
      ]
  ]

  #colbreak()
  #pop.column-box(heading: "Methodik")[
    - Eigenen Datensatz mit 3 Sprecher je 175 Sätze
      - Sätze aus dem alltäglichen Gebrauch
    - Überprüfung des Modells auf Einsatz in Realszenarien
    - Modell: AV-HuBERT Large (pretrained, LRS3-433h) @avpresentation
    #v(4pt)
    #figure(caption: "Auswertung des Modells durch Error Rates [%]")[
      #stack(dir: ltr, spacing: 50pt,
        $ text("WER") = (S + D + I) / N $,
        $ text("CER") = (S + D + I) / N $
      )
    ]
  ]

  #let wer_cer = read("assets/wer_cer.svg").replace("__c1__", mainColor.to-hex()).replace("__c2__", secColor.to-hex())
  #pop.column-box(heading: "Ergebnisse")[
    - *Task:* Satz-Level Lipreading (Video #sym.arrow.r Text)
    - *Metrik:* Word Error Rate (WER) & Character Error Rate (CER)
    

    // - *Status:* Quantitative Auswertung *noch ausstehend*
    #figure(caption: [
      Auswertung //@wiki:File:Treron_vernans_male_-_Kent_Ridge_Park.jpg
    ])[
      #image(bytes(wer_cer), height: 330pt)
    ]
  ]

  #pop.column-box(heading: "Fehleranalyse")[
    Typische Fehlerquellen:
    - *Viseme-Ambiguität* (ähnliche Lippenformen #sym.arrow.r verschiedene Laute)
    - *Pose / Bewegungsunschärfe / Beleuchtung*
    - *Okklusion* (Hand, Bart, Mikrofon, Maske)

    #figure(caption: [
      Auswertung //@wiki:File:Treron_vernans_male_-_Kent_Ridge_Park.jpg
    ])[
      #stack(dir: ltr, spacing: 40pt,
        ..range(1, 4).map(i =>
          image("assets/"+str(i)+"-error.png", height: 170pt)
        )
      )
    ]

    *Ausblick*:
    - *nicht-labialen Lauten* wie *glottale Laute* nicht ohne Ton trennbar @lindner
    - kaum Gefahr vor "externer" Überwachung durch KI-gestützte Kamerasysteme
      - allerdings Deutlich Bessere ergebnisse mit Ton+Bild @avpresentation
      #sym.arrow.r *WER*: 26.9%
      
  ]

  #colbreak()

  #pop.column-box(heading: "Contribution")[
    - Einsatz von *AV-HuBERT (Large, pretrained)* @avpresentation
    - Pretrained Checkpoint: *LRS3-433h (EN)* + VoxCeleb2 (EN)
    - *Live-Demo im Saal* (Video #sym.arrow.r Satz-Transkription)
    #figure(caption: [
        YALR-WebTool //@wiki:File:Treron_vernans_male_-_Kent_Ridge_Park.jpg
      ])[
        #image("assets/yalr-tool.png", height: 716pt)
      ]
  ]

  #pop.column-box(heading: "Links / Referenzen")[
    #bibliography("bibliography.bib")
  ]

])

