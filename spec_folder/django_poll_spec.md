# Polls List Page - UI Specification

## 🌐 URL
**Page URL:** [http://127.0.0.1:8000/polls/list/](http://127.0.0.1:8000/polls/list/)

---

## Overview
This page displays a list of polls with options to sort, search, and add new polls. It is the landing page after login.

> **Note:** Authentication is required to access this page. Users must be logged in to view or interact with the landing page content.
---

## Header

- **Logo**: Abstract bar graph icon on the left.
- **Navigation Links (Left-Aligned)**:
  - `Home`: Navigates to the home page.
  - `Polls`: Navigates to the polls listing page.
- **Navigation Links (Right-Aligned)**:
  - `My Polls`: Navigates to user's created polls.
  - `Logout`: Logs the user out.

---

## Main Section

### Title
- Centered large text: `Welcome to polls List!`

### Controls (Horizontally Centered)
- **Sorting Buttons** (Blue Buttons):
  - `Name` with sort icon (⇅)
  - `Date` with clock icon (🕒)
  - `Vote` with bar chart icon (📊)
  
- **Search Box**:
  - Input field with placeholder `Search`
  - Search button with magnifying glass icon (🔍)

- **Add Poll Button**:
  - Label: `Add +`
  - Positioned to the right of the sorting controls
  - Styled in blue

---

## Behavior

- Clicking sort buttons will reorder the polls list.
- The search box filters polls based on keywords.
- `Add +` button opens a form to create a new poll.
- Navigation links update the view accordingly.

