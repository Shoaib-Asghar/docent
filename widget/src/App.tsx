import Widget from './Widget';

function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Client Website Placeholder</h1>
      <p>
        This page represents an arbitrary client website (or your Docusaurus site). 
        The Docent Widget is completely decoupled and simply injected into the DOM as a floating UI element.
      </p>
      
      {/* The isolated widget component */}
      <Widget />
    </div>
  );
}

export default App;
