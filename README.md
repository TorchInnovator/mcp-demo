# MCP AI Agent Server

A FastAPI-based server that implements the Model Context Protocol (MCP) for Claude Desktop integration. This server provides tools for file reading and character counting.

## Features

- File reading with security checks
- Character counting functionality
- MCP protocol compliance
- Automatic port selection
- Error handling and logging

## Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- python-dotenv

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TorchInnovator/mcp-test.git
cd mcp-test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
./start_server.bat  # Windows
# or
python main.py      # Direct execution
```

2. The server will start on port 8081 (or the next available port if 8081 is in use)

## Available Tools

### read_file
Reads the content of a file from allowed directories (Documents, Downloads, Desktop, or github).

Parameters:
- `file_path`: Path to the file to read

### count_r
Counts the number of 'r' characters in a string.

Parameters:
- `text`: Text to count 'r' characters in

## Security

The server implements several security measures:
- Path normalization and validation
- Directory access restrictions
- File existence checks
- Multiple encoding support

## License

MIT License 