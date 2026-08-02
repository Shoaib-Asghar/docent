import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Widget from './Widget.tsx'
import './index.css'

// CS/SE Concept: Defensive DOM Injection
// When a client embeds our script on their site, we cannot assume they have a <div id="root"> waiting for us.
// Instead, we dynamically create our own container and append it to the body to guarantee it works anywhere.
let container = document.getElementById('docent-widget-root');

if (!container) {
  container = document.createElement('div');
  container.id = 'docent-widget-root';
  document.body.appendChild(container);
}

createRoot(container).render(
  <StrictMode>
    <Widget />
  </StrictMode>,
)
