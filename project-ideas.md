# Hands-On Learning Projects for a Junior Developer

This document presents project ideas, roadmaps, and enhancements. It’s designed to be engaging for a young beginner developer, while teaching Airtable (Free plan features), AWS Lambda, AWS S3, and even the Spotify API.

## Project Ideas Overview

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

## 💪 Project 3 Roadmap: Personal Fitness Log

### Phase 1: Airtable Setup
1. Create a base with fields: `Date`, `Exercise`, `Sets`, `Reps`, `Weight`, `Duration (min)`, `Notes`.
2. Build a quick-log form for workouts.
3. Add a `Workouts This Week` rollup/formula for weekly totals.

### Phase 2: Airtable Interfaces
4. Weekly progress dashboard: workouts per week, total duration, volume (sets × reps × weight).
5. Charts by exercise and by week.

### Phase 3: Airtable Automations
6. Automation: send a motivational message when a milestone is hit (e.g. 10th workout, 5 workouts in a week).
7. Automation: auto-fill `Date` with today if left blank.

### Phase 4: Airtable Web API
8. Script to fetch all workouts for a given week via API.
9. Script to add workouts programmatically.

### Phase 5: AWS Lambda + S3
10. Create S3 bucket for weekly PDF summaries.
11. Lambda function (scheduled weekly): fetch the week's workouts, generate a PDF summary, upload to S3.
12. Update Airtable with the S3 link (new `Weekly Summaries` table).

### Phase 6: Polish & Share
13. Add filters (exercise, date range) to the interface.
14. Share the dashboard with a friend or coach for accountability.

**Learning Outcomes**: Data aggregation, scheduled Lambdas (EventBridge), PDF generation, S3 storage, health-habit motivation.

---

## 🎬 Project 4 Roadmap: Mini Movie Review Site

### Phase 1: Airtable Setup
1. Create two tables: `Movies` (`Title`, `Year`, `Genre`, `Poster URL`, `Average Rating`) and `Reviews` (`Movie` link, `Reviewer`, `Rating`, `Review`).
2. Build a form for friends to submit reviews.

### Phase 2: Airtable Interfaces
3. “Top 10 Movies” leaderboard sorted by average rating.
4. Movie detail page showing poster and all reviews.

### Phase 3: Airtable Automations
5. Auto-calculate average rating per movie (rollup/formula, plus automation if needed).
6. Notify when a new review is submitted.

### Phase 4: Movie Metadata API
7. Register for a free movie API (e.g. [TMDB](https://www.themoviedb.org/settings/api)) and get an API key.
8. Script: search a movie by title, return year, genre, and poster URL.
9. Script to add movies to Airtable programmatically.

### Phase 5: AWS Lambda + S3
10. Create S3 bucket for posters.
11. Lambda function: fetch poster from the API, upload to S3, return URL.
12. Update Airtable with the S3 link.

### Phase 6: Polish & Share
13. Upgrade interface with gallery view and genre filters.
14. Share with friends for reviews.

**Learning Outcomes**: Linked records and rollups, third-party API integration, aggregation logic, S3 asset hosting, social collaboration.

---

## 🎨 Project 5 Roadmap: Digital Art Portfolio

### Phase 1: Airtable Setup
1. Create a base with fields: `Title`, `Description`, `Tags`, `Medium`, `Created Date`, `Image URL`, `Status`.
2. Build a form for adding artwork details.

### Phase 2: Airtable Interfaces
3. Gallery view of the portfolio with tag filters.
4. Artwork detail page with description and image.

### Phase 3: Airtable Automations
5. Notify when new artwork is added.
6. Auto-set `Status` to “Draft” for new entries.

### Phase 4: Airtable Web API
7. Script to fetch all artworks via API.
8. Script to add artwork records programmatically.

### Phase 5: AWS Lambda + S3
9. Create S3 bucket for artwork images.
10. Lambda function: generate a presigned upload URL so images upload directly to S3.
11. Lambda function (S3 trigger): on upload, create a thumbnail and update Airtable with the image and thumbnail links.

### Phase 6: Polish & Share
12. Add a public-facing portfolio page (Airtable shared interface or a small Vite site reading from the API).
13. Share the portfolio link.

**Learning Outcomes**: File upload flows, presigned URLs, S3 event triggers, image processing, building something that feels like a real product.

---

## Final Thoughts

These projects are designed to be:
- **Personalized**: Games, music, movies, fitness, art.  
- **Practical**: Airtable Free plan + AWS basics.  
- **Exciting**: Shareable with friends, interactive, creative.  
- **Progressive**: Each roadmap builds skills step by step.  

Together, they form a learning journey that feels like building real apps, not just toy examples.
