# Model Card: Social Music Recommender MVP

## 1. Model Name

**Social Music Recommender MVP**

---

## 2. Goal / Task

This system recommends songs for users in an invite-only social music app.
It is designed to help in two cases:
- recommend songs for established users with listening history
- recommend songs for newly invited users with very little history

The goal is to simulate how a real recommender can combine personal taste and social influence instead of relying on a single signal.

---

## 3. Data Used

The system uses five CSV datasets:
- `songs.csv`
- `users.csv`
- `friendships.csv`
- `recommendations.csv`
- `listening_history.csv`

The song catalog includes fictional tracks with attributes such as genre, mood, energy, tempo, valence, and duration.
The user dataset stores starter preferences, onboarding status, and invite source.
The social datasets track friend relationships, direct song recommendations, and listening behavior.

This data is synthetic and small, which makes it good for classroom experimentation but not representative of real music platforms.

---

## 4. Algorithm Summary

The recommender uses a weighted scoring system.
Each candidate song receives:

- a `personal score` based on genre, mood, energy, tempo, and valence match
- a `social score` based on friend likes, direct friend recommendations, and friend similarity
- a `cold-start adjustment` for new users so social signals count more heavily when listening history is limited

After scoring all candidate songs, the system ranks them and returns the top recommendations.
It also generates short explanations and a confidence score for each result.

---

## 5. Observed Behavior / Biases

One clear pattern is that active friends can become highly influential.
If a connected friend likes many songs or frequently sends recommendations, that friend can affect rankings more than quieter users.

Another limitation is that the system depends on structured labels such as genre and mood.
That means subtle musical differences are flattened into a few categories.
For example, two songs labeled `indie` may sound very different, but the system treats them as similar.

The cold-start logic is useful, but it can also import bias from the user's network.
If a new user joins through a narrow social circle, the early recommendations may overrepresent that group's taste before the system learns the new user's own preferences.

---

## 6. Evaluation Process

I evaluated the system in two ways.

First, I ran automated tests with `pytest` to confirm that:
- the original starter recommender behavior still works
- a new invited user can receive onboarding recommendations
- the reliability checks pass on the seed dataset

Second, I ran the full application and inspected sample outputs for:
- `Ava`, an established user
- `Zara`, a newly invited user in cold-start mode

The application also runs integrated reliability checks that confirm:
- new users receive recommendations
- established users get preference-aligned results
- invited users are connected to the friend network
- recommendation records point to valid songs

In the latest verified run, `4 / 4` tests passed and `4 / 4` reliability checks passed.

---

## 7. Intended Use and Non-Intended Use

This system is intended for:
- classroom learning
- demonstrating recommendation logic
- exploring cold-start onboarding and social influence
- showing how reliability checks can be integrated into an AI-style system

It is not intended for:
- real commercial music recommendation
- inferring deep social compatibility between people
- making high-stakes decisions about users
- treating social data as a complete picture of a person's taste or identity

---

## 8. Reliability and Guardrails

The project includes several reliability features:
- automated tests
- confidence scoring in recommendation output
- integrated reliability checks in the main application flow
- logging setup in the application

The main guardrail is that the system explains why recommendations appear instead of returning only opaque rankings.
This makes it easier to spot when the recommender is leaning too heavily on one factor such as friend activity.

---

## 9. Limitations, Risks, and Misuse

- The catalog is small, so recommendation diversity is limited.
- The social graph is synthetic and much simpler than a real platform.
- Friend influence can overpower individual taste if weights are not tuned carefully.
- Anonymous recommendations reduce transparency because users cannot judge the source directly.
- A user could misuse the system by spamming recommendations and artificially shaping what others see.

One way to reduce misuse in a future version would be to limit how much one friend can influence a ranking or to add diversity constraints.

---

## 10. Ideas for Improvement

- Expand the song catalog and make genre coverage more balanced.
- Add diversity rules so the top recommendations are less repetitive.
- Track whether social recommendations actually improve long-term user satisfaction.
- Add a dedicated evaluation script that compares profile-only and profile-plus-social recommendations.
- Add more visible logging around why one friend had strong influence on a result.

---

## 11. Reflection on AI Collaboration

One helpful AI suggestion during this project was the idea to frame the final system around a cold-start onboarding problem instead of only friend-to-friend sharing. That made the project more coherent and helped connect the social feature to a real recommender challenge.

One flawed suggestion earlier was trying to keep the project too broad by mixing song recommendation, people recommendation, and activity matching all at once. That would have made the project harder to explain and test, so I narrowed the scope back to song recommendation first.

This project taught me that AI systems are not only about generating outputs. They also need clear structure, evaluation, and limits. Even a small recommender becomes much more believable when it explains its decisions and checks whether its behavior is consistent.
