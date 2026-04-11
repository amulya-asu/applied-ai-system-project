# Music Recommender Simulation

## Project Summary

This project is a small CLI-first music recommender simulation.
It loads songs from a CSV file, compares them to user preferences, and returns the top matches.
The recommender uses simple scoring rules based on genre, mood, and energy.

---

## How The System Works

Each song includes features like genre, mood, energy, tempo, valence, danceability, and acousticness.
The user profile focuses on genre, mood, and energy.
The recommender gives each song a score based on how well those features match the user preferences.
After that, it sorts the songs by score and shows the top recommendations in the terminal with short explanations.

---

## Getting Started

### Setup

1. Create a virtual environment if you want:

```bash
python -m venv .venv
source .venv/bin/activate
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run tests with:

```bash
pytest
```

---

## Experiments You Tried

I tested the recommender with multiple user profiles, including `Dance on Beat`, `Silent Getaway`, and `Midnight Steel`.
I also ran a sensitivity experiment where I lowered the genre weight and increased the energy weight.
This helped me see how much the rankings changed when one feature became more important.

---

## Limitations and Risks

The system only works on a very small catalog of 20 songs.
It depends on exact labels, so similar genres like `pop` and `indie pop` are treated as different.
It can also over-prioritize energy, which means some songs rank high even when the overall vibe does not feel quite right.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

My biggest learning moment during this project was understanding content-based filtering and why it matters when new users are onboarded. I saw that even with only a few features like genre, mood, and energy, the system can still start making recommendations right away. That helped me understand why content-based filtering is useful when there is not much user history yet.

AI tools helped me check my logic and think through whether my scoring system was matching songs in a reasonable way. At the same time, I still needed to double-check the results myself, especially when the outputs looked mathematically correct but did not fully match musical intuition. What surprised me most was that such a simple algorithm could still feel like a real recommender. A few formulas were enough to produce suggestions that seemed believable, even without a large dataset. If I keep extending this project, I want to explore my own music taste more deeply, include more genres, and model different listening situations. For example, someone driving does not always want upbeat music, so I would like the system to understand context better instead of assuming one mood fits every situation.
