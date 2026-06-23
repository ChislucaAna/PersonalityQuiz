// Adaptive quiz (mirrors Intrebari.txt).
//
// 5 main yes/no questions. Each has 3 follow-ups that are shown ONLY when the
// user answered "yes" to the main. Every (question_id, answer_id) below matches a
// key in the backend SCORING dict (app/analysis/trait_scorer.py):
//   - main questions:  id "1".."5",  answer_id "yes" | "no"
//   - follow-ups:      id "1a".."5c", answer_id "a" | "b" | "c" | "d"
//
// Quiz CONTENT is Romanian (as provided); UI chrome stays English (per wireframe).

export interface QuizOption {
  answer_id: string;
  text: string;
}

export interface FollowUp {
  id: string;
  text: string;
  options: QuizOption[];
}

export interface MainQuestion {
  id: string;
  category: string;
  text: string;
  options: QuizOption[]; // yes / no
  followUps: FollowUp[];
}

const YES_NO: QuizOption[] = [
  { answer_id: "yes", text: "Da" },
  { answer_id: "no", text: "Nu" },
];

export const QUIZ: MainQuestion[] = [
  {
    id: "1",
    category: "natura",
    text: "Ti-ar placea sa petreci mai mult timp in natura decat in oras?",
    options: YES_NO,
    followUps: [
      {
        id: "1a",
        text: "Ce moment din natura te incarca cel mai mult?",
        options: [
          { answer_id: "a", text: "Rasaritul — liniste si inceput" },
          { answer_id: "b", text: "Furtuna — haos si energie" },
          { answer_id: "c", text: "Noaptea instelata — infinit si mister" },
          { answer_id: "d", text: "Apusul — caldura si sfarsit de zi" },
        ],
      },
      {
        id: "1b",
        text: "Unde te simti cel mai liber?",
        options: [
          { answer_id: "a", text: "In varful unui munte" },
          { answer_id: "b", text: "La marginea marii" },
          { answer_id: "c", text: "Intr-o padure densa" },
          { answer_id: "d", text: "Pe un camp deschis, fara niciun obstacol" },
        ],
      },
      {
        id: "1c",
        text: "Cum esti tu in natura?",
        options: [
          { answer_id: "a", text: "Stau si observ, absorb tot in tacere" },
          { answer_id: "b", text: "Ma misc, explorez, vreau sa vad ce e dupa" },
          { answer_id: "c", text: "Ma asez si ma pierd in ganduri" },
          { answer_id: "d", text: "Vreau sa am pe cineva alaturi cu care sa impart momentul" },
        ],
      },
    ],
  },
  {
    id: "2",
    category: "sport",
    text: "Sportul si miscarea fac parte din viata ta?",
    options: YES_NO,
    followUps: [
      {
        id: "2a",
        text: "Cum preferi sa te misti?",
        options: [
          { answer_id: "a", text: "Solo — sala, alergat, antrenament propriu" },
          { answer_id: "b", text: "Cu altii — sport de echipa, clase de grup" },
          { answer_id: "c", text: "In natura — hiking, ciclism, inot" },
          { answer_id: "d", text: "Liber — dans, yoga, ceva fara reguli fixe" },
        ],
      },
      {
        id: "2b",
        text: "Ce cauti cand faci sport?",
        options: [
          { answer_id: "a", text: "Sa imi golesc mintea — nu mai gandesc la nimic" },
          { answer_id: "b", text: "Sa imi depasesc limitele — vreau sa fiu mai bun" },
          { answer_id: "c", text: "Sa simt adrenalina si energia" },
          { answer_id: "d", text: "Sa fiu prezent in corp, sa ma simt viu" },
        ],
      },
      {
        id: "2c",
        text: "Cum te simti dupa un antrenament bun?",
        options: [
          { answer_id: "a", text: "Linistit si resetat — ca dupa o meditatie" },
          { answer_id: "b", text: "Incarcat si energic — gata sa cuceresc lumea" },
          { answer_id: "c", text: "Mandru — am facut ceva pentru mine" },
          { answer_id: "d", text: "Epuizat fizic, dar mental eliberat" },
        ],
      },
    ],
  },
  {
    id: "3",
    category: "ordine",
    text: "Ti-ai dori ca viata ta sa fie mai imprevizibila decat planificata?",
    options: YES_NO,
    followUps: [
      {
        id: "3a",
        text: "Ce tip de imprevizibil te atrage?",
        options: [
          { answer_id: "a", text: "Sa plec undeva fara sa stiu unde" },
          { answer_id: "b", text: "Sa incerc ceva complet nou si necunoscut" },
          { answer_id: "c", text: "Sa las o conversatie sa ma duca unde vrea" },
          { answer_id: "d", text: "Sa imi schimb total directia cand simt ca trebuie" },
        ],
      },
      {
        id: "3b",
        text: "Cand esti in haos, cum reactionezi?",
        options: [
          { answer_id: "a", text: "Ma aprind — haosul ma energizeaza" },
          { answer_id: "b", text: "Ma detasez si observ din exterior" },
          { answer_id: "c", text: "Incerc sa gasesc un fir de sens in mijlocul lui" },
          { answer_id: "d", text: "Ma pierd in el, dar nu ma deranjeaza" },
        ],
      },
      {
        id: "3c",
        text: "Ce simti fata de rutina?",
        options: [
          { answer_id: "a", text: "Ma sufoca — simt ca stagnez" },
          { answer_id: "b", text: "O accept dar incerc mereu sa o rup cu ceva" },
          { answer_id: "c", text: "E un rau necesar, nu ma entuziasmeaza" },
          { answer_id: "d", text: "Depinde de rutina — unele imi plac, altele nu" },
        ],
      },
    ],
  },
  {
    id: "4",
    category: "emotii",
    text: "Crezi ca emotiile tale conduc mai mult decat ratiunea?",
    options: YES_NO,
    followUps: [
      {
        id: "4a",
        text: "Care emotie te defineste cel mai bine?",
        options: [
          { answer_id: "a", text: "Nostalgia — mereu cu un picior in trecut" },
          { answer_id: "b", text: "Dorul — dupa oameni, locuri, versiuni ale mele" },
          { answer_id: "c", text: "Entuziasmul — ma aprind repede de idei si oameni" },
          { answer_id: "d", text: "Melancolia — o tristete frumoasa fara un motiv clar" },
        ],
      },
      {
        id: "4b",
        text: "Cum iti procesezi emotiile puternice?",
        options: [
          { answer_id: "a", text: "Le exprim imediat — trebuie sa iasa" },
          { answer_id: "b", text: "Le tin in mine pana se aseaza singure" },
          { answer_id: "c", text: "Le transform in ceva — scriu, creez, misc" },
          { answer_id: "d", text: "Caut pe cineva cu care sa vorbesc" },
        ],
      },
      {
        id: "4c",
        text: "Ce te misca cel mai tare?",
        options: [
          { answer_id: "a", text: "Muzica — unele melodii ma descompun complet" },
          { answer_id: "b", text: "Oamenii — gesturile mici, sincere" },
          { answer_id: "c", text: "Frumusetea — un peisaj, o imagine, o fraza perfecta" },
          { answer_id: "d", text: "Ideile — cand ceva imi schimba perspectiva" },
        ],
      },
    ],
  },
  {
    id: "5",
    category: "muzica",
    text: "Muzica este o parte importanta din viata ta?",
    options: YES_NO,
    followUps: [
      {
        id: "5a",
        text: "Ce simti cand asculti o melodie care te prinde cu adevarat?",
        options: [
          { answer_id: "a", text: "Ma transport intr-un loc sau moment din trecut" },
          { answer_id: "b", text: "Simt ca cineva a pus in cuvinte ce eu nu am putut" },
          { answer_id: "c", text: "Ma eliberez — corpul se misca singur" },
          { answer_id: "d", text: "Ma inchid in mine si ma pierd in ea" },
        ],
      },
      {
        id: "5b",
        text: "In ce momente ai cea mai mare nevoie de muzica?",
        options: [
          { answer_id: "a", text: "Cand sunt trist sau coplesit — ma tine companie" },
          { answer_id: "b", text: "Cand am nevoie de energie — ma porneste" },
          { answer_id: "c", text: "Cand lucrez sau creez — intra in fundal si ma focuseaza" },
          { answer_id: "d", text: "Mereu — nu concep sa fac ceva fara ea" },
        ],
      },
      {
        id: "5c",
        text: "Ce gen asculti cel mai des?",
        options: [
          { answer_id: "a", text: "Ceva introspectiv — indie, folk, ambient, clasica" },
          { answer_id: "b", text: "Ceva intens — rock, metal, hip-hop, electronic" },
          { answer_id: "c", text: "Depinde total de starea mea — variez mult" },
          { answer_id: "d", text: "Nu am un gen fix — ma misc dupa feeling" },
        ],
      },
    ],
  },
];
