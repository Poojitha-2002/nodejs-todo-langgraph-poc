// Get the root div
const root = document.getElementById('root');

// Create a heading
const heading = document.createElement('h2');
heading.textContent = 'This content was added via JavaScript';

// Create a paragraph
const para = document.createElement('p');
para.textContent = 'Client-side rendering inserts this content after the page loads.';

// Create a list
const list = document.createElement('ul');
const items = ['Apple', 'Banana', 'Cherry'];

items.forEach(item => {
  const li = document.createElement('li');
  li.textContent = item;
  list.appendChild(li);
});

// Append all elements to the root div
root.appendChild(heading);
root.appendChild(para);
root.appendChild(list);
