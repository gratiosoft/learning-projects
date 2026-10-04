# Hands-On Learning Projects for a Junior Developer

This document presents project ideas, roadmaps, and enhancements. It’s designed to be engaging for a young beginner developer, while teaching Airtable (Free plan features), AWS Lambda, AWS S3, and even the Spotify API.

## 🚀 Project Ideas Overview

### 1. Game Collection Tracker
- **Airtable Web API**: Store video games (title, platform, rating, completion status).
- **Airtable Interfaces**: Dashboard showing progress (e.g., % completed).
- **Airtable Forms**: Add new games via a form.
- **Airtable Automations**: Notify when a new game is added.
- **AWS Lambda + S3**: Fetch cover art from an API, save to S3, link in Airtable.

👉 Fun because it ties into gaming interests and teaches API + storage integration.

---

### 2. Music Playlist Curator
- **Airtable Web API**: Store songs with artist, genre, mood tags.
- **Airtable Interfaces**: Playlist generator filtering by mood.
- **Airtable Forms**: Friends submit song recommendations.
- **Airtable Automations**: Auto‑tag new songs as “unreviewed.”
- **AWS Lambda + S3**: Fetch album art or previews, save to S3, link in Airtable.

👉 Exciting because it feels like building a mini‑Spotify.

---

### 3. Personal Fitness Log
- **Airtable Web API**: Track workouts (exercise, reps, sets, duration).
- **Airtable Interfaces**: Weekly progress charts.
- **Airtable Forms**: Quick workout logging.
- **Airtable Automations**: Motivational messages when milestones are hit.
- **AWS Lambda + S3**: Generate weekly PDF summaries, store in S3, link in Airtable.

👉 Engaging because it connects coding with health and self‑improvement.

---

### 4. Mini Movie Review Site
- **Airtable Web API**: Store movie titles, ratings, reviews.
- **Airtable Interfaces**: “Top 10 Movies” leaderboard.
- **Airtable Forms**: Friends submit reviews.
- **Airtable Automations**: Auto‑calculate average ratings.
- **AWS Lambda + S3**: Fetch posters, save to S3, link in Airtable.

👉 Fun because it’s social and creative.

---

### 5. Digital Art Portfolio
- **Airtable Web API**: Store artwork titles, descriptions, tags.
- **Airtable Interfaces**: Gallery view of portfolio.
- **Airtable Forms**: Upload new artwork details.
- **Airtable Automations**: Notify when new artwork is added.
- **AWS Lambda + S3**: Handle image uploads, store in S3, link in Airtable.

👉 Exciting because it feels like building a real product.

---

## 🕹 Project 1 Roadmap: Game Collection Tracker

### Phase 1: Airtable Setup
1. Create a base with fields: `Title`, `Platform`, `Genre`, `Completion Status`, `Rating`, `Cover Art URL`.
2. Build a form for adding new games.
3. Create an interface dashboard showing totals, % completed, average rating.

### Phase 2: Airtable Automations
4. Automation: notify when a new game is added.
5. Automation: auto‑tag new games as “Unreviewed.”

### Phase 3: Airtable Web API
6. Script to fetch all games via API.
7. Script to add new games programmatically.

### Phase 4: AWS Lambda + S3
8. Create S3 bucket for cover art.
9. Lambda function: fetch cover art from API, upload to S3, return URL.
10. Update Airtable with S3 link.

### Phase 5: Polish & Share
11. Upgrade interface with gallery view and filters.
12. Share with friends for submissions.

**Learning Outcomes**: Airtable mastery, AWS basics, integration skills, motivation through gaming.

---

## 🎵 Project 2 Roadmap: Music Playlist Curator

### Phase 1: Airtable Setup
1. Create a base with fields: `Song Title`, `Artist`, `Genre`, `Mood`, `Spotify Track ID`, `Album Art URL`, `Preview URL`.
2. Build a form for song recommendations.

### Phase 2: Airtable Interfaces
3. Playlist dashboard filtering by mood.
4. Show album art and preview links.

### Phase 3: Airtable Automations
5. Auto‑tag new songs as “Unreviewed.”
6. Notify when new songs are added.

### Phase 4: Spotify API Integration
7. Register at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) for Client ID/Secret.
8. Script: search songs via Spotify API, return track ID, album art, preview URL.
9. Update Airtable with Spotify data.

### Phase 5: AWS Lambda + S3
10. Deploy Spotify search script as Lambda.
11. Optional: save album art in S3, link in Airtable.

### Phase 6: Polish & Share
12. Upgrade interface with gallery view and filters.
13. Share with friends for submissions.

**Learning Outcomes**: Real API integration, playlist management, AWS backend power, fun factor of building a mini‑Spotify.

---

## 🎯 Final Thoughts

These projects are designed to be:
- **Personalized**: Games, music, movies, fitness, art.  
- **Practical**: Airtable Free plan + AWS basics.  
- **Exciting**: Shareable with friends, interactive, creative.  
- **Progressive**: Each roadmap builds skills step by step.  

Together, they form a learning journey that feels like building real apps, not just toy examples.
