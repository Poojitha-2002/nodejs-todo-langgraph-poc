
# ✅ UI Specification Document: Employee Dashboard (iSpoc)

## 🎯 Purpose:
An employee dashboard that displays profile info, tasks, upcoming holidays, birthdays, and asset allocation. The layout is optimized for daily productivity and HR visibility.

---

## 🖼️ Layout Overview:

- **Top Bar:** Brand logo, user greeting, notifications, profile avatar
- **Sidebar (Left):** Navigation menu
- **Main Content (Center & Right):** Profile card, task list, holidays, birthdays, and asset list

---

## 🧩 Components Breakdown:

### 1. Header / Top Navigation Bar
- **Logo:** iSpoc (top-left)
- **Text:** `Welcome : Konduru Manasa Veena` (top-right)
- **Icons:**
  - Notification bell with badge (count: 74)
  - User avatar
  - Company emblem/logo

---

### 2. Sidebar Navigation
A vertical list of navigation items with icons and expandable menus:
- Dashboard (highlighted in orange)
- Human Resource
- Attendance/Timesheet
  - Attendance
  - Leaves
  - Work From Home (WFH)
  - Time Sheet
- Performance Evaluation
- Forms & Policies
- Meeting Room
- Tickets
- Tutorials
- User Manual

---

### 3. Main Content Area (Cards Layout)

#### a. Profile Card (Left Box)
- **Heading:** `Basic-Info`
- **Fields:**
  - Name: Konduru Manasa Veena
  - Date-of-Birth: 08/03/2002
  - Associate Code: 001043
  - Contact: 8465970113
- **Button:** `View Full Profile` (blue text link)
- **Photo:** Circular profile image

---

#### b. My To-Do Task (Center Box)
- **Title:** My To Do Task
- **List Items:**
  - Punch-In/Punch-Out entry missing (24/06/2025)
  - Timesheet entries missing (multiple dates)
  - Self performance evaluation reminder (June)

---

#### c. Upcoming Holiday (Right Box)
- **Table Columns:** Name | Date | Floating
- **Items:**
  - Independence Day (15/08/2025) - No
  - Gandhi Jayanti & Dussehra (02/10/2025) - No
  - Diwali (20/10/2025) - No
  - Christmas Day (25/12/2025) - No

---

#### d. Upcoming Birthday (Bottom Left)
- **Title:** Upcoming Birthday in this month
- **Table:**
  - Rishi Kumar Saxena – 28 Jun

---

#### e. Assigned Assets (Bottom Right)
- **Title:** Assigned Assets (Personal Use)
- **Table Columns:** Asset Code | Allocated On
- **Items:**
  - HP G2 USB Headphone – 29-Jan-2024
  - LOGITECH WIRED MOUSE – 27-Nov-2024
  - Dell Latitude 3400 – 29-Jan-2024

---

## 🎨 Styling:
- **Theme:** Light with blue highlights
- **Font:** Sans-serif (likely Roboto or similar)
- **Profile/Task Cards:** Drop shadows, white background
- **Active Sidebar Item:** Orange highlight
- **Tables:** Simple grid layout, scrollable if long

---

## 📱 Responsiveness (Assumptions):
- Sidebar collapses into hamburger menu on smaller screens
- Cards stack vertically on mobile
- Tables become scrollable on smaller viewports

---

## 🔘 Interactions:
- Sidebar expands submenus on click
- View Full Profile opens detailed profile
- Scrollable lists for tasks, holidays, assets

---

## 💡 Suggestions:
- Add progress indicators to tasks
- Allow editing or acknowledging tasks
- Enable filters/sorting for tables