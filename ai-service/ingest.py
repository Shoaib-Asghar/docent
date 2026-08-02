import os
from core.vector_store import VectorStoreManager

def parse_markdown_contextually(filepath: str):
    """
    Parses a markdown file and chunks it by Headers (H1 and H2).
    This strictly satisfies the Phase 2 'contextual chunking' requirement,
    avoiding blind fixed-size token splitting.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    chunks = []
    current_h1 = ""
    current_h2 = ""
    current_chunk = []
    
    filename = os.path.basename(filepath)
    
    for line in lines:
        if line.startswith('# '):
            if current_chunk:
                chunks.append({"text": "\n".join(current_chunk), "h1": current_h1, "h2": current_h2, "file": filename})
                current_chunk = []
            current_h1 = line[2:].strip()
            current_h2 = "" # Reset h2 on new h1
        elif line.startswith('## '):
            if current_chunk:
                chunks.append({"text": "\n".join(current_chunk), "h1": current_h1, "h2": current_h2, "file": filename})
                current_chunk = []
            current_h2 = line[3:].strip()
        elif line.startswith('---') or line.startswith('sidebar_position:'):
            # Skip Docusaurus frontmatter
            pass
        else:
            if line.strip():
                current_chunk.append(line)
                
    if current_chunk:
        chunks.append({"text": "\n".join(current_chunk), "h1": current_h1, "h2": current_h2, "file": filename})
        
    return chunks

def main():
    docs_dir = os.path.join("..", "docs-site", "docs")
    all_chunks = []
    
    print(f"Scanning directory: {docs_dir}")
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md") or file.endswith(".mdx"):
                filepath = os.path.join(root, file)
                parsed_chunks = parse_markdown_contextually(filepath)
                
                for p in parsed_chunks:
                    if not p["text"].strip():
                        continue
                        
                    # Prepend the hierarchy into the chunk so the LLM has perfect context
                    hierarchy = f"{p['file']}"
                    if p['h1']: hierarchy += f" > {p['h1']}"
                    if p['h2']: hierarchy += f" > {p['h2']}"
                    
                    contextual_text = f"DOCUMENT HIERARCHY: {hierarchy}\n\n{p['text'].strip()}"
                    
                    metadata = {
                        "source_file": p['file'],
                        "h1": p['h1'],
                        "h2": p['h2']
                    }
                    all_chunks.append({"text": contextual_text, "metadata": metadata})

    if not all_chunks:
        print("No documents found to ingest.")
        return

    print(f"Parsed {len(all_chunks)} contextual chunks. Initializing Qdrant Vector Store...")
    
    vsm = VectorStoreManager()
    vsm.setup_collection()
    
    documents = [c["text"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]
    
    print("Embedding and ingesting (FastEmbed will automatically download local models on first run)...")
    vsm.ingest_documents(documents, metadatas)
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
