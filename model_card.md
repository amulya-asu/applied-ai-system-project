# Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

This recommender suggests songs from a small music catalog.
It tries to find songs that match a user's favorite genre, mood, and energy level.
The goal is not to predict the perfect song.
The goal is to simulate how a simple recommender system works.

---

## 3. Data Used

The dataset has 20 songs.
Each song has a title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.
I used the provided CSV file and did not add new songs.
One limit is that the catalog is very small.
Another limit is that some genres appear only once, so the system does not represent all music tastes equally well.

---

## 4. Algorithm Summary

The system gives each song a score.
It checks if the genre matches the user preference.
It checks if the mood matches the user preference.
It also compares the song's energy to the user's target energy.
Songs with a closer energy level get a higher score.
After scoring all songs, the system sorts them from highest to lowest and returns the top results.

---

## 5. Observed Behavior / Biases

One pattern I noticed is that energy has a strong effect on the ranking.
Because of that, high-energy songs can rank well even when the mood or genre is not a perfect fit.
For example, `Gym Hero` can appear for users who want happy pop because it matches pop and has strong energy.
Another limitation is that the system depends on exact labels.
That means similar genres like `pop` and `indie pop` are treated as different.
The small dataset also creates bias because some kinds of users have more close matches than others.

---

## 6. Evaluation Process

I tested the system with three user profiles: `Dance on Beat`, `Silent Getaway`, and `Midnight Steel`.
These profiles were made to represent different tastes.
I ran the recommender in the terminal and looked at the top 5 songs for each one.
I compared whether the outputs matched the expected vibe of each profile.
I also ran a sensitivity experiment where I lowered the genre weight and increased the energy weight.
That test showed me that the recommendations can change a lot when one feature becomes more important.

---

## 7. Intended Use and Non-Intended Use

This system is meant for classroom learning and simple experimentation.
It is useful for showing how recommender systems turn user preferences into ranked outputs.
It is not meant for real music apps.
It should not be used to make important decisions about users or their identity.
It also should not be treated as a personalized model of real human taste.

---

## 8. Ideas for Improvement

- Add more songs and more balanced genre coverage.
- Use more flexible matching for similar genres and moods.
- Add a diversity rule so the top 5 results are not too repetitive.

---

## 9. Personal Reflection

This project helped me see that even a simple recommender can feel smart at first.
At the same time, small design choices can shape the results a lot.
I learned that recommendation systems are not just about code.
They also reflect the data, labels, and assumptions built into them.
