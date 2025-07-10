
# ✅ UI Specification Document: Todos Dashboard

## 🎯 Project Overview:
A task management web application dashboard for users to manage their **pending**, **completed**, and **all tasks**. The interface is sleek, dark-themed, and uses icons and color indicators for task categorization and progress.

---

## 🖼️ Layout Sections:

### 1. Top Navigation Bar
- **Logo & Title:**  
  - Icon: Clipboard or checklist icon.  
  - Text: `Todos.` (with a colored period).
- **Actions:**  
  - `Login` (Text button)  
  - `Sign Up` (Outlined button)

---

### 2. Left Sidebar
- Title: `collection` (in lowercase, gray color)
- Navigation Items:
  - `Pending Tasks` (highlighted in red)
  - `Completed Tasks`
  - `All Tasks`

---

### 3. Main Dashboard (Center Area)
- **Section Title:**  
  - Greeting: `Good Afternoon,`  
  - Heading: `Here Your All Tasks To Complete`
- **Sub-section:**  
  - Label: `Pending Tasks`
  - Button: `ADD NEW TASKS` (Pink button with white uppercase text)

#### 🗂️ Task Categories:
Each category is a card with:
- **Icon** and **Label**
- **Pending Task Count**

| Category   | Icon      | Pending Count |
|------------|-----------|----------------|
| Work       | 💼         | 0              |
| Personal   | 👤         | 81             |
| Shopping   | 🛒         | 0              |
| Others     | 📦 or 🧩   | 0              |

---

### 4. Right Sidebar (User Profile Panel)
- **Greeting Section:**
  - Text: `Hello,`
  - Profile Avatar: Illustrated male avatar
  - Vertical Ellipsis (⋮) for options

- **Task Statistics:**
  - **Total Tasks:** `213` (Blue vertical line indicator)
  - **Completed Tasks:** `132` (Green)
  - **Pending Tasks:** `81` (Red)

---

## 🎨 Color Scheme:
- **Background:** #111 or dark gray
- **Text:** White or Light Gray
- **Accent Colors:**
  - Red: Pending task highlights
  - Green: Completed tasks
  - Blue: Total tasks
  - Pink: Add Task button

---

## 🔤 Fonts & Typography:
- **Main Font:** Sans-serif (e.g., Poppins or Inter)
- **Weights:**
  - Bold for headings
  - Medium for category labels
  - Regular for stats
- **Special Styling:** 
  - “Todos.” has stylized period and icon
  - “Here Your All Tasks…” is large and bold

---

## 📱 Responsiveness (Assumptions):
- Sidebar collapses on smaller screens
- Cards stack vertically on mobile
- Sticky navbar at the top

---

## 🔘 Interactions:
- `ADD NEW TASKS` → Opens task input modal/form
- Sidebar menu items → Change content in main view
- Profile icon / ellipsis → Opens profile options or settings

---

## 🧩 Component Breakdown:
| Component               | Type             |
|------------------------|------------------|
| Navbar                 | Shared Component |
| Sidebar Menu           | Shared Component |
| Dashboard Heading      | Page-Specific    |
| Task Category Cards    | Reusable Component |
| User Profile Sidebar   | Shared Component |
| Statistics Block       | Reusable Component |