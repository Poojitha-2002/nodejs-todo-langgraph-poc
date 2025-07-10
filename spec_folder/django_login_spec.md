# ✅ UI Specification Document: Login Page

## 🎯 Purpose:
A clean and centered login form to authenticate users into the system using their username and password.

---

## 🌐 Endpoint & Default Values:

- **Login URL:** `http://127.0.0.1:8000/accounts/login/`
- **Default Username:** `Manasa_konduru`
- **Default Password:** `123456`
- **Post-login Redirect URL:** `http://127.0.0.1:8000/`

---

## 🖼️ Layout Overview:
The login form is presented in a bordered box, centered horizontally on the page. A top navigation bar is also included for basic navigation.

---

## 🧩 Components:

### 1. Top Navigation Bar
- **Left Side:**
  - **Logo:** Small icon (possibly a chart or dashboard icon)
  - **Label:** `Home`
- **Right Side:**
  - `Login` link  
  - `Register` link  
- **Style:** Horizontal navbar with minimal padding and gray text links

---

### 2. Login Form (Centered Card)
- **Box Style:** 
  - Centered on the screen  
  - Thin blue border  
  - White background  

#### 🔷 Title
- **Text:** `Login`  
- **Style:** Blue, bold, centered, medium-large font

#### 🔲 Input Fields

| Field     | Type     | Placeholder     | Required | Default Value |
|-----------|----------|-----------------|----------|----------------|
| Username  | Text     | Enter Username  | Yes      | `testuser`     |
| Password  | Password | Password        | Yes      | `Test@1234`    |

- Both fields have blue-bordered rectangular input boxes

---

#### 🔘 Button
- **Label:** `Login`  
- **Type:** Submit button  
- **Style:** Solid blue background with white text  

---

### 🔐 Browser Password Suggestion
- Shown below the password field (automatically by browser)  
- Includes saved credentials and "Manage passwords" option

---

## 🎨 Styling Notes:
- **Font:** Sans-serif  
- **Alignment:** Centered form  
- **Input Field Borders:** Blue outline on focus  
- **Text Colors:**  
  - Headings: Blue  
  - Labels: Black  
  - Links: Gray  

---

## 📱 Responsiveness (Assumptions):
- Form should stay centered on different screen sizes  
- Navigation bar elements should collapse or wrap on small devices  

---

## 🔘 Interactions:
- Login button triggers form submission to `http://127.0.0.1:8000/accounts/login/`  
- On successful authentication with:
  - **Username:** `Manasa_konduru`
  - **Password:** `123456`
  - User is redirected to: `http://127.0.0.1:8000/`  
- Saved browser credentials may appear in password field  
- Links in navbar redirect to their respective routes  

---

## 💡 Suggestions for Enhancement:
- Add “Forgot Password?” link  
- Include validation and error messages  
- Use icons inside input fields for better UX  
- Make the form mobile-responsive  
