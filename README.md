## Setup

### Virtual Environment

This project uses a Python virtual environment to manage dependencies. Follow these steps to set up:

1. Create a virtual environment:
   In terminal do:
   python -m venv venv

2. Activate the virtual environment:
   **Windows:**
   venv\Scripts\activate
   **macOS/Linux:**
   source venv/bin/activate
   You should see `(venv)` appear at the beginning of your terminal prompt, indicating the virtual environment is active.

3. Installing Dependencies
   With the virtual environment activated, install the required packages:
   pip install -r requirements.txt

### Running code

Navigate to the root directory of the repo in the terminal of your choice, and run:

python src/main.py --schedule=schedule.json \  
 --overrides=overrides.json \
 --from='2023-11-17T17:00:00Z' \
 --until='2023-12-01T17:00:00Z'
--output="output.json" (optional, output.json is default value)

### Deactivating Virtual Env

When you're done working on the project, you can deactivate the virtual environment:
In terminal run:
deactivate

## Code Structure

### Data Models with Pydantic

The application uses Pydantic models to handle data validation and serialization. This provides several key benefits:

- **Automatic JSON validation**: Input data is automatically validated against the defined models
- **Type safety**: Accessing model fields is type-safe and caught at compile time
- **IDE support**: Get autocomplete and type hints for all model fields
- **Error handling**: Clear error messages when JSON doesn't match expected schema

For example, instead of error-prone dictionary access like `data["start_at"]`, we can safely use `entry.start_at`. start = data["start_at"] leads to a KeyError if misspelled. start = schedule_entry.start_at # Caught at compile time if invalid

### Extensible Parser Architecture

The parser system uses the Factory pattern to create appropriate parsers for different input types. Its ultimate role is to handle the

- Base `FileParser` abstract class defines the interface
- Concrete implementations (e.g., `JSONParser`) handle specific formats
- Factory class instantiates the correct parser based on file type
- Easy to add new parsers (XML, CSV, etc.) by implementing the base interface

This design allows for:

- Dynamic routing of input files to appropriate parsers
- Simple addition of new file format support
- Consistent parsing interface across the application

#### Natural Language Parser (Experimental)

The project also includes an experimental TXT parser that supports natural language queries. This parser demonstrates the extensibility of the parser architecture, though it's currently a proof-of-concept implementation only works on macs and has been tested very little on my laptop

- Supports reading schedule information from plain text files
- Uses LLM-powered natural language processing

**Note:** To use the natural language parser functionality:

1. Install the AI-specific dependencies instead of the standard requirements:
   ```bash
   pip install -r ai_requirements.txt
   ```
2. The AI-related imports are implemented lazily to ensure standard functionality works without these additional dependencies.
3. Be aware that we are currently using a nearly 3gb model, so please don't use txt input files unless you want the model to start downloading automatically

Our design and use of a factory parser means that all you have to do to change parsers is change the schedule argument from schedule.json to schedule.txt:

python src/main.py --schedule=schedule.txt \  
 --overrides=overrides.json \
 --from='2023-11-17T17:00:00Z' \
 --until='2023-12-01T17:00:00Z'
--output="output.json" (optional, output.json is default value)

### Scheduling

The scheduler implementation uses the Strategy pattern:

- `ScheduleCreator` abstract base class defines the scheduling interface
- `BasicScheduleCreator` provides the default implementation
- Additional scheduling strategies can be easily added (eg the priority based one I mention next)

This architecture allows for:

- Easy addition of new scheduling algorithms
- Simple testing of different scheduling approaches
- Clean separation of scheduling logic
- Runtime configuration of scheduling behavior

# Future Ideas

- Priority based scheduler, so instead of naively considering who is due to be in a certain period and checking if there are no overrides. Instead you can store a priority queue of user alongside the time they have currently spent on call (using a min heap). So next user in schedule is determined by popping top item off the min heap
- Users can request for someone to cover for their shift. Other users can accept / reject these requests
- Integration with users google / apple calenders with notifications and alerts to remind them when their shift is
- A clean web interface for nice visualisation of the schedule, and easy interface to upload schedule / override files
