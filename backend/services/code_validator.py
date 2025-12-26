"""
Code validator for Manim scripts.
Ensures generated code is safe and valid before execution.
"""
import ast
import re
from typing import Tuple, List

# Allowed imports for Manim scripts
ALLOWED_IMPORTS = {
    "manim",
    "numpy",
    "math",
    "random",
    "itertools",
    "functools",
}

# Dangerous patterns that should be blocked
DANGEROUS_PATTERNS = [
    r"\bos\.",
    r"\bsys\.",
    r"\bsubprocess\.",
    r"\bopen\s*\(",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    r"\b__import__\s*\(",
    r"\bimport\s+os\b",
    r"\bimport\s+sys\b",
    r"\bimport\s+subprocess\b",
    r"\bfrom\s+os\b",
    r"\bfrom\s+sys\b",
    r"\bfrom\s+subprocess\b",
    r"\bshutil\.",
    r"\brequests\.",
    r"\burllib\.",
    r"\bsocket\.",
    r"\bpickle\.",
]


def check_dangerous_patterns(code: str) -> Tuple[bool, List[str]]:
    """Check for dangerous patterns in the code."""
    found_patterns = []
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            found_patterns.append(pattern)
    
    return len(found_patterns) == 0, found_patterns


def check_syntax(code: str) -> Tuple[bool, str]:
    """Check if the code has valid Python syntax."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"


def check_structure(code: str) -> Tuple[bool, str]:
    """Check if the code has the required Manim structure."""
    try:
        tree = ast.parse(code)
        
        # Check for manim import
        has_manim_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "manim":
                    has_manim_import = True
                    break
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "manim":
                        has_manim_import = True
                        break
        
        if not has_manim_import:
            return False, "Code must import from manim (e.g., 'from manim import *')"
        
        # Check for Scene class
        has_scene_class = False
        has_construct_method = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Scene":
                        has_scene_class = True
                        # Check for construct method
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == "construct":
                                has_construct_method = True
                                break
                        break
        
        if not has_scene_class:
            return False, "Code must define a class that inherits from Scene"
        
        if not has_construct_method:
            return False, "Scene class must have a construct method"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error analyzing code structure: {str(e)}"


def validate_manim_code(code: str) -> Tuple[bool, str]:
    """
    Validate Manim code for safety and correctness.
    
    Args:
        code: The Manim Python code to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for empty code
    if not code or not code.strip():
        return False, "Code is empty"
    
    # Check syntax
    is_valid_syntax, syntax_error = check_syntax(code)
    if not is_valid_syntax:
        return False, syntax_error
    
    # Check for dangerous patterns
    is_safe, dangerous_patterns = check_dangerous_patterns(code)
    if not is_safe:
        return False, f"Code contains dangerous patterns: {', '.join(dangerous_patterns)}"
    
    # Check structure
    is_valid_structure, structure_error = check_structure(code)
    if not is_valid_structure:
        return False, structure_error
    
    return True, ""
