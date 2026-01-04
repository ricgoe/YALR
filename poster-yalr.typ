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
  #pop.column-box(heading: "Motivation")[
    - *Barrierefreiheit:* Unterstützung für Menschen mit auditiven oder sprachlichen Beeinträchtigungen.
    - *Audioausfälle:* Rekonstruktion gesprochener Inhalte bei fehlender, gestörter oder stark verrauschter Tonspur.
    - *Ethische Bedenken:* Einsatz in Überwachungsszenarien.
    - *Ziel:* Evaluation eines vortrainierten AV-HuBERT-Modells für rein visuelle Satz-Spracherkennung im Real-World-Setting.
  ]

  // #pop.column-box(heading: "Ansatz")[
  //   - *End-to-End Inferenz-Pipeline* für Satz-Level Lipreading
  //   - Video #sym.arrow.r Mund-ROI @wiki:ROI #sym.arrow.r Modell #sym.arrow.r Text
  //   - Fokus auf stabile Inferenz und Demo-Tauglichkeit
  // ]

  #pop.column-box(heading: [CV/ML-Pipeline ])[
    Das Modell erfordert *standardisierte* Eingangsgrößen (geglätteter Auschnitt der Mund-Region \[96x96 px\]).
    1. *ROI-Extraktion:* Mund-Crop mit Hilfe von Gesichtslandmarken @mediapipe_guide.
    #v(5pt)
    #figure(caption: [
      Augenwinkel und Nasenspitze definieren T-Zone, aus der Verkrümmung und Ausschnitt der Mundregion berechnet werden.
    ])[
      #image("assets/landmarks.png", height: 300pt, width: 400pt)
    ]
    #v(8pt)
    2. *Sequenzaufbereitung:* Skalierung und Normalisierung der Crops.
    3. *Modellanwendung:* Inferenz mit dem vortrainierten AV-HuBERT-Modell.
    4. *Ausgabe:* Generierte Satztranskriptionen.
    #let arrow = bytes(read("assets/arrow.svg").replace("__c1__", mainColor.to-hex()))
    #let nn = bytes(read("assets/nn.svg").replace("__c1__", mainColor.to-hex()))
    #let paps = bytes(read("assets/paper.svg").replace("__c1__", mainColor.to-hex()))
    #figure(caption: [
        Exemplarische CV/ML-Pipeline (Beispielaufnahmen aus @lrs3).
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
    - Erhebung eines eigenen Datensatzes mit drei Sprecher:innen 
      - je 175 Sätze aus dem alltäglichen Gebrauch @sentences_ds
    - Überprüfung des Modells auf Einsatz in Realszenarien
    - Modell: AV-HuBERT Large (pretrained, LRS3-433h+Self-Training) @avpresentation
    #v(4pt)
    #figure(
    caption: [
    Auswertung des Modells mittels Wort- und Zeichenerrorraten [%] mit #strong("S")ubstitutionen, #strong("D")eletionen, #strong("I")nsertionen und Referenzlänge (*N*).
    ])[
    #stack(dir: ltr, spacing: 50pt,
      $ text("WER/ CER") = (S + D + I) / N $
    )
]
  ]

  #let wer_cer = read("assets/wer_cer.svg").replace("__c1__", mainColor.to-hex()).replace("__c2__", secColor.to-hex())
  #pop.column-box(heading: "Ergebnisse")[
    // - *Status:* Quantitative Auswertung *noch ausstehend*
    #figure(caption: [
      Vergleich von WER und CER für den eigenen Datensatz einschließlich Durchschnitt; Baseline nach @avpresentation.
    ])[
      #image(bytes(wer_cer), height: 330pt)
    ]
  ]

  #pop.column-box(heading: "Diskussion & Ausblick")[
    Typische Fehlerquellen:
    - *Viseme Ambiguität* (ähnliche Lippenformen #sym.arrow.r verschiedene Laute) @Bear_2017
    - *nicht-labiale Laute* wie *glottale Laute* nicht ohne Ton trennbar @lindner
    - *Profilaufnahme / Bewegungsunschärfe / Beleuchtung*
    - *Okklusion* (Hand, Bart, Mikrofon, Maske)

    #figure(caption: [
      Beispielhafte Darstellung der Viseme Ambiguität.
    ])[
      #stack(dir: ltr, spacing: 40pt,
        ..range(1, 4).map(i =>
          image("assets/"+str(i)+"-error.png", height: 170pt)
        )
      )
    ]

    *Ausblick*:
    - @avpresentation zeigt, dass eine Hinzunahme auditiver Informationen auf dem verwendeten Datensatz @lrs3 die WER deutlich reduziert (1.3 % vs. 26.9 %).
    - Replikation ähnlicher Verbesserungen für eigenen Datensatz noch ausstehend.

      
  ]

  #colbreak()

  #pop.column-box(heading: "Webbasierter Demonstrator")[
    - Webbasierter Demonstrator zur satzweisen visuellen Spracherkennung
    - Backend-Integration eines vortrainierten AV-HuBERT-Large-Modells
    - Pretrained Checkpoint: LRS3-433h (EN) + VoxCeleb2 (EN)
    - Live-Videoeingabe mit automatischer Satztranskription
    - Hashbasiertes Caching vorverarbeiteter Video-Crops zur Beschleunigung der Verarbeitung
    #figure(caption: [
        YALR-WebTool //@wiki:File:Treron_vernans_male_-_Kent_Ridge_Park.jpg
      ])[
        #image("assets/yalr-tool.png", height: 630pt)
      ]
  ]

  #pop.column-box(heading: "Links / Referenzen")[
    #bibliography("tbib.bib")
  ]

])

