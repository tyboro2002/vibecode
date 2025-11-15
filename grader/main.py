from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import sys
from io import StringIO
import traceback

app = FastAPI()

class TestCase(BaseModel):
    id: int
    input_data: Any  # Can be list, dict, or single value
    expected_output: str
    is_public: bool = True  # Default to public

class GradeRequest(BaseModel):
    problem_id: int
    code: str
    tests: List[TestCase]

def execute_code(code: str, inputs: Any) -> str:
    """
    Execute user code with given inputs.
    Assumes the code defines a function and we need to call it with inputs.
    """
    try:
        # Create a namespace for execution
        namespace = {}
        
        # Execute the user's code to define functions
        exec(code, namespace)
        
        # Find the first function defined (excluding builtins) # TODO maybe search for the function with the given name
        user_function = None
        for name, obj in namespace.items():
            if callable(obj) and not name.startswith('__'):
                user_function = obj
                break
        
        if user_function is None:
            return "ERROR: No function found in code"
        
        # Call the function with inputs
        if isinstance(inputs, list):
            result = user_function(*inputs)
        elif isinstance(inputs, dict):
            result = user_function(**inputs)
        else:
            result = user_function(inputs)
        
        return str(result)
    
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)}"

@app.post("/")
async def grade_submission(request: GradeRequest):
    """
    Grade a code submission against test cases.
    """
    try:
        results = []
        all_passed = True
        
        for test in request.tests:
            output = execute_code(request.code, test.input_data)
            passed = output.strip() == test.expected_output.strip()
            
            if not passed:
                all_passed = False
            
            results.append({
                'test_id': test.id,
                'input': test.input_data,
                'expected': test.expected_output,
                'actual': output,
                'passed': passed,
                'is_public': test.is_public
            })
        
        return {
            'correct': all_passed,
            'results': results,
            'total_tests': len(request.tests),
            'passed_tests': sum(1 for r in results if r['passed'])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5556)
