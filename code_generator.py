"""Code generation using LangChain agents."""
import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class CodeGenerator:
    """Code generator using LangChain agents."""
    
    def __init__(self):
        """Initialize the code generator with OpenAI LLM."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key
        )
    
    def generate_code(self, ticket_info: Dict, repo_structure: List[str] = None) -> Dict[str, str]:
        """
        Generate code based on ticket acceptance criteria.
        
        Args:
            ticket_info: Dictionary containing ticket information
            repo_structure: List of existing files in the repository
            
        Returns:
            Dictionary mapping file paths to file contents
        """
        print(f"\n🤖 Generating code for ticket: {ticket_info['key']}")
        
        # Create a comprehensive prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software developer. Your task is to generate code that fulfills Jira ticket requirements."),
            ("user", """Generate code for the following Jira ticket:

Ticket Summary: {summary}

Description:
{description}

Acceptance Criteria:
{acceptance_criteria}

Existing Repository Structure:
{repo_structure}

Please generate the necessary code files to fulfill all acceptance criteria. 
Return your response as a structured format where each file is clearly marked with:
FILE: <file_path>
CONTENT:
<file_content>
END_FILE

Generate all necessary files including:
- Source code files
- Test files
- Configuration files if needed
- Documentation if required

Ensure the code is:
- Well-structured and follows best practices
- Includes proper error handling
- Has appropriate comments
- Is production-ready
- Follows the existing code style if applicable""")
        ])
        
        repo_structure_str = "\n".join(repo_structure) if repo_structure else "New repository"
        
        # Format the prompt with ticket information
        formatted_prompt = prompt_template.format_messages(
            summary=ticket_info['summary'],
            description=ticket_info['description'],
            acceptance_criteria=ticket_info['acceptance_criteria'],
            repo_structure=repo_structure_str
        )
        
        # Invoke the LLM
        try:
            # Try new LCEL syntax first
            chain = prompt_template | self.llm
            response = chain.invoke({
                "summary": ticket_info['summary'],
                "description": ticket_info['description'],
                "acceptance_criteria": ticket_info['acceptance_criteria'],
                "repo_structure": repo_structure_str
            })
        except (TypeError, AttributeError):
            # Fallback: direct invocation
            response = self.llm.invoke(formatted_prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            response = response.content
        elif isinstance(response, str):
            response = response
        else:
            response = str(response)
        
        # Parse the response to extract files
        files = self._parse_generated_files(response)
        
        print(f"✓ Generated {len(files)} file(s)")
        return files
    
    def _parse_generated_files(self, response: str) -> Dict[str, str]:
        """
        Parse the LLM response to extract file paths and contents.
        
        Args:
            response: LLM response containing file definitions
            
        Returns:
            Dictionary mapping file paths to contents
        """
        files = {}
        current_file = None
        current_content = []
        
        lines = response.split('\n')
        
        for line in lines:
            if line.startswith('FILE:'):
                # Save previous file if exists
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                
                # Start new file
                current_file = line.replace('FILE:', '').strip()
                current_content = []
            elif line.strip() == 'END_FILE':
                # Save current file
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                    current_file = None
                    current_content = []
            elif current_file:
                current_content.append(line)
        
        # Save last file if exists
        if current_file:
            files[current_file] = '\n'.join(current_content).strip()
        
        # If no structured format found, try to infer files from code blocks
        if not files:
            files = self._parse_code_blocks(response)
        
        return files
    
    def _parse_code_blocks(self, response: str) -> Dict[str, str]:
        """Fallback: Parse code blocks from markdown-style response."""
        files = {}
        import re
        
        # Look for code blocks with file paths
        pattern = r'```(\w+)?:?([^\n]+)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches:
            lang, path, content = match
            if path:
                file_path = path.strip()
            else:
                # Generate a default path based on language
                ext_map = {
                    'python': '.py',
                    'javascript': '.js',
                    'typescript': '.ts',
                    'java': '.java',
                    'go': '.go'
                }
                ext = ext_map.get(lang.lower(), '.txt')
                file_path = f"generated_file{ext}"
            
            files[file_path] = content.strip()
        
        # If still no files, create a default implementation file
        if not files:
            files['implementation.py'] = response
        
        return files

