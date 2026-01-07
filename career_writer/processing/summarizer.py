import math
from typing import List, Dict
from llm.base import LLMProvider
from cli.menu import Menu

class ReferenceProcessor:
    def __init__(self, llm: LLMProvider, chunk_size: int = 4000):
        self.llm = llm
        self.chunk_size = chunk_size

    def split_text(self, text: str) -> List[str]:
        """Simple character-based chunking. Could be improved with token counting."""
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def summarize_references(self, references: Dict[str, str]) -> str:
        """
        Processes a dictionary of filename->content.
        Returns a single summarized string.
        """
        combined_summary = ""
        
        for filename, content in references.items():
            Menu.print_info(f"Processing reference: {filename} ({len(content)} chars)")
            
            if len(content) <= self.chunk_size:
                # Small enough, just append relevant parts
                # Or still summarize to keep it dense? Let's summarize to normalize format.
                summary = self._summarize_chunk(filename, content)
            else:
                # Large file, map-reduce
                chunks = self.split_text(content)
                chunk_summaries = []
                for i, chunk in enumerate(chunks):
                    print(f"  - Chunk {i+1}/{len(chunks)}...")
                    chunk_sum = self._summarize_chunk(filename, chunk, is_part=True)
                    chunk_summaries.append(chunk_sum)
                
                # Reduce
                combined_chunk_text = "\n".join(chunk_summaries)
                summary = self._summarize_chunk(filename, combined_chunk_text, is_reduce=True)

            combined_summary += f"=== Ref: {filename} ===\n{summary}\n\n"
            
        return combined_summary

    def _summarize_chunk(self, source: str, text: str, is_part: bool = False, is_reduce: bool = False) -> str:
        type_desc = "fragment" if is_part else "document"
        if is_reduce: type_desc = "set of summaries"
        
        prompt = f"""
        Analyze the following {type_desc} from '{source}'.
        Extract key FACTUAL information relevant to a resume/career description:
        - Project goals and problems
        - Technical actions and technologies
        - Measurable results
        
        Discard conversational filler, formatting noise, or irrelevant metadata.
        Output a dense bulleted list of facts.

        TEXT:
        {text[:self.chunk_size]} 
        """
        # Note: text slice safety in case prompt gets too large, though text should be chunked already.
        
        return self.llm.generate(prompt)
