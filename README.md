# Multi-OS Activity Tracker Daemon

## Description
The **Multi-OS Activity Tracker Daemon** is a personal project designed to monitor and categorize user activities across different operating systems. It tracks active applications, window titles, and idle times, categorizing activities into the following categories:

- **Work**: Productivity-related applications and tasks.
- **Private**: Personal or leisure activities.
- **Idle**: Time when the system is idle, locked, or asleep.
- **Uncategorized**: Activities that do not fit into predefined categories.

This project utilizes an AI-driven rule-based system for categorization and saves the output in structured JSON format for analysis.

## Features
- Cross-platform support for multiple operating systems.
- Real-time activity tracking, including foreground application monitoring.
- Rule-based categorization using AI.
- Idle detection to track inactive states of the system.
- JSON output for easy analysis and integration with other tools.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/multi-os-activity-tracker.git
   cd multi-os-activity-tracker
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the tracker:
   ```bash
   python activity_tracker.py
   ```

## Usage
- Run the script on your system to start tracking activities.
- View the categorized JSON output to analyze usage patterns.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributions
This is a personal project, but feedback, issues, and ideas are welcome. Feel free to open a pull request or raise an issue.

## Disclaimer
This project is intended for personal and educational use. Please respect privacy and data protection regulations when using or modifying it.

