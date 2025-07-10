# ✅ UI Specification Document: iSpoc Login Page

## 🎯 Purpose:
Defines the layout and functionality of the login page for iSpoc (Impressico platform).

---

## 🖼️ Layout Overview:
A vertically and horizontally centered login form for desktop users, styled cleanly.

---

## 🧩 Components

### 1. Logos and Branding

- **Top-Left Logo**: iSpoc logo, placed in the top-left corner.
- **Centered Icon**: Stylized Impressico icon (blue/red person), center-aligned at the top.

---

### 2. Page Titles

- **Main Heading**: "Sign in to iSpoc" — bold, large, centered.
- **Subheading**: "Enter your details below" — smaller font, centered below the heading.

---

### 3. Login Form

- **Username Field**
  - Label: "Employee ID/Username"
  - Type: text
  - Placeholder: "Enter Employee ID/Username"
  - Required: yes

- **Password Field**
  - Label: "Password"
  - Type: password (masked)
  - Placeholder: "Enter password"
  - Required: yes

- **Remember Me**
  - Type: checkbox
  - Label: "Remember me"
  - Default: checked

- **Forgot Password Link**
  - Text: "Forgot Password?"
  - Type: hyperlink
  - Alignment: right-aligned near password field
  - Clickable: yes

- **Submit Button**
  - Label: "Submit"
  - Type: button
  - Action: triggers form submission
  - Style: pink background (#D9537F), rounded corners, hover effect

---

## 🎨 Styling

- **Fields**: White background, light gray border
- **Font**: Modern sans-serif
- **Text Colors**: Dark gray for text, blue for links
- **Layout**: Center-aligned form, stacked vertically
- **Button**: Rounded, styled with hover effect

---

## 📱 Responsiveness

- Desktop layout optimized
- Centered form preserved across breakpoints
- No explicit mobile behaviors defined

---

## 🔘 Interactions

- **Submit**: Validates and submits form
- **Forgot Password?**: Navigates to password recovery page
- **Remember Me**: Persists session (likely via cookies or browser storage)

---

## 🔒 Validation & Security

- Fields must not be empty
- Use HTTPS for secure transmission
- Session handling for "Remember me" must be secure
- Error messages shown on login failure

---

## 💡 Suggestions for Improvement

- Add inline form validation
- Include ARIA roles for accessibility
- Disable submit until fields are filled
- Use proper error feedback (e.g., "Invalid credentials")
