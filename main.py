from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv
import json
from pathlib import Path
import re
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socket
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Log to stderr for Claude Desktop
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define allowed base directories
ALLOWED_BASE_DIRS = [
    str(Path.home() / "Documents"),
    str(Path.home() / "Downloads"),
    str(Path.home() / "Desktop"),
    str(Path.home() / "github"),  # Added github directory
]

app = FastAPI(
    title="MCP AI Agent Server",
    description="Multi-Component Processing AI Agent Server with Claude Desktop Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP Protocol endpoints
@app.get("/mcp/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})

@app.get("/mcp/tools")
async def list_tools():
    return JSONResponse(content={
        "tools": [
            {
                "name": "read_file",
                "description": "Read the content of a file. Files must be in Documents, Downloads, Desktop, or github folders.",
                "parameters": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                }
            },
            {
                "name": "count_r",
                "description": "Count the number of 'r' characters in a string",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "Text to count 'r' characters in"
                    }
                }
            }
        ]
    })

@app.post("/mcp/execute")
async def execute_mcp(request: Request):
    try:
        data = await request.json()
        logger.debug(f"Received request: {data}")
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class ToolRequest(BaseModel):
    name: str
    parameters: Dict[str, str]

class AgentRequest(BaseModel):
    prompt: str
    context: Optional[List[str]] = None
    parameters: Optional[dict] = None

class AgentResponse(BaseModel):
    response: str
    metadata: Optional[dict] = None

class FileReadRequest(BaseModel):
    file_path: str

class CountRRequest(BaseModel):
    text: str

class MCPExecuteRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any]

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def normalize_path(file_path: str) -> str:
    """Normalize and validate file path"""
    # Replace environment variables
    file_path = os.path.expandvars(file_path)
    
    # Convert to absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    # Normalize path separators
    file_path = os.path.normpath(file_path)
    
    # Check if path is within allowed directories
    allowed_dirs = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/github")
    ]
    
    if not any(file_path.startswith(d) for d in allowed_dirs):
        raise HTTPException(
            status_code=403,
            detail="File must be in Documents, Downloads, Desktop, or github directory"
        )
    
    return file_path

def read_file(file_path: str) -> str:
    """Read the content of a file with security checks."""
    try:
        # Normalize the path
        file_path = normalize_path(file_path)
        logger.debug(f"Normalized file path: {file_path}")
        
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        logger.debug(f"Absolute file path: {abs_path}")
        
        # Check if path is allowed
        if not is_path_allowed(abs_path):
            allowed_dirs = "\n".join(ALLOWED_BASE_DIRS)
            raise HTTPException(
                status_code=403,
                detail=f"Access to {file_path} is not allowed. File must be in one of these directories:\n{allowed_dirs}"
            )
        
        # Check if file exists
        if not os.path.exists(abs_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_path}\nPlease check:\n1. The file exists\n2. The path is correct\n3. You have permission to access it"
            )
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(abs_path):
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a file: {file_path}"
            )
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(abs_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    logger.debug(f"Successfully read file with {encoding} encoding")
                    return content
            except UnicodeDecodeError:
                continue
                
        raise HTTPException(
            status_code=400,
            detail=f"Could not read file {file_path} with any of the supported encodings"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file {file_path}: {str(e)}"
        )

def count_r(text: str) -> int:
    """Count the number of 'r' characters in a string."""
    return text.lower().count('r')

@app.get("/")
async def root():
    logger.debug("Received request to root endpoint")
    return {"message": "Welcome to MCP AI Agent Server"}

@app.post("/process", response_model=AgentResponse)
async def process_request(request: AgentRequest):
    try:
        logger.debug(f"Received request with prompt: {request.prompt}")
        
        # Parse the prompt to determine which tool to use
        if "read_file" in request.prompt.lower():
            # Extract file path from prompt
            file_path = request.prompt.split("read_file")[1].strip()
            result = read_file(file_path)
            return AgentResponse(
                response=result,
                metadata={"status": "success", "tool": "read_file"}
            )
        elif "count_r" in request.prompt.lower():
            # Extract text from prompt
            text = request.prompt.split("count_r")[1].strip()
            count = count_r(text)
            return AgentResponse(
                response=f"Number of 'r' characters: {count}",
                metadata={"status": "success", "tool": "count_r"}
            )
        else:
            return AgentResponse(
                response="Invalid tool request. Available tools: read_file, count_r",
                metadata={"status": "error", "error": "invalid_tool"}
            )
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/{tool_name}", response_model=AgentResponse)
async def execute_tool(tool_name: str, request: ToolRequest):
    try:
        logger.debug(f"Executing tool: {tool_name} with parameters: {request.parameters}")
        
        if tool_name == "read_file":
            file_path = request.parameters.get("file_path")
            if not file_path:
                raise HTTPException(status_code=400, detail="file_path parameter is required")
            result = read_file(file_path)
            return AgentResponse(
                response=result,
                metadata={"status": "success", "tool": "read_file"}
            )
        elif tool_name == "count_r":
            text = request.parameters.get("text")
            if not text:
                raise HTTPException(status_code=400, detail="text parameter is required")
            count = count_r(text)
            return AgentResponse(
                response=str(count),
                metadata={"status": "success", "tool": "count_r"}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = 8081
    max_attempts = 5
    
    for attempt in range(max_attempts):
        if not is_port_in_use(port):
            break
        logger.warning(f"Port {port} is in use, trying next port...")
        port += 1
    else:
        logger.error(f"Could not find available port after {max_attempts} attempts")
        sys.exit(1)
    
    logger.info(f"Starting server on port {port}")
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=port, log_level="debug") 