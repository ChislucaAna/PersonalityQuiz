// Mirrors the backend's app/models.py response shapes.

export interface Answer {
  question_id: string;
  answer_id: string;
}

export interface Traits {
  scores: Record<string, number>; // axis -> 0..1
  interests: string[];
}

export interface Label {
  name: string;
  blurb: string;
}

export interface Style {
  palette: string;
  art_style: string;
  mood: string;
  setting: string;
  figure: string;
  motifs: string[];
}

export interface AnalyzeResponse {
  image_url: string;
  traits: Traits;
  label: Label;
  style?: Style | null;
  prompt?: string | null;
}
