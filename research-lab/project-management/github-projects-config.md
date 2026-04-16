# GitHub Projects Configuration

## Project Board Setup

### 1. Research Lab Project Board

#### Board Structure
```
Research Lab Projects
|
|--- Backlog
|    |--- High Priority
|    |--- Medium Priority
|    |--- Low Priority
|    |--- Research Ideas
|
|--- To Do
|    |--- This Week
|    |--- Next Week
|    |--- Future
|
|--- In Progress
|    |--- Development
|    |--- Research
|    |--- Review
|    |--- Testing
|
|--- Review
|    |--- Code Review
|    |--- Research Review
|    |--- Documentation Review
|
|--- Done
|    |--- This Sprint
|    |--- Last Sprint
|    |--- Archive
```

#### Custom Fields
```yaml
Task Fields:
  Priority:
    type: "Single select"
    options: ["P0 - Critical", "P1 - High", "P2 - Medium", "P3 - Low"]
  
  Category:
    type: "Single select"
    options: ["Research", "Development", "Infrastructure", "Community"]
  
  Assignee:
    type: "Text"
    description: "GitHub username of assigned person"
  
  Estimated Hours:
    type: "Number"
    description: "Estimated effort in hours"
  
  Deadline:
    type: "Date"
    description: "Target completion date"
  
  Milestone:
    type: "Single select"
    options: ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", "Ongoing"]
  
  Status:
    type: "Single select"
    options: ["Planning", "Active", "Blocked", "Review", "Completed"]
```

### 2. Automated Workflows

#### Issue to Card Automation
```yaml
name: Auto-create Project Card
on:
  issues:
    types: [opened]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v0.4.0
        with:
          project-url: https://github.com/orgs/research-lab/projects/1
          github-token: ${{ secrets.PROJECTS_TOKEN }}
          labeled: "auto-assign"
```

#### PR Status Updates
```yaml
name: Update PR Status
on:
  pull_request:
    types: [opened, closed, merged]

jobs:
  update-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/update-project@v0.4.0
        with:
          project-url: https://github.com/orgs/research-lab/projects/1
          github-token: ${{ secrets.PROJECTS_TOKEN }}
          status: ${{ github.event.action }}
```

#### Deadline Reminders
```yaml
name: Deadline Reminders
on:
  schedule:
    - cron: '0 9 * * 1-5'  # Daily at 9 AM

jobs:
  send-reminders:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v6
        with:
          script: |
            const { data: items } = await github.rest.projects.listCards({
              project_id: 1,
              column_id: 2
            });
            
            for (const item of items) {
              const deadline = new Date(item.deadline);
              const today = new Date();
              const daysUntil = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
              
              if (daysUntil <= 3 && daysUntil > 0) {
                await github.rest.issues.createComment({
                  owner: 'research-lab',
                  repo: 'main',
                  issue_number: item.content_id,
                  body: `:warning: **Deadline approaching!** This task is due in ${daysUntil} days.`
                });
              }
            }
```

### 3. View Configurations

#### Team Member Views
```yaml
Personal Dashboard:
  name: "My Tasks"
  filters:
    assignee: "@me"
  sort: ["Priority", "Deadline"]
  columns: ["To Do", "In Progress", "Review"]

Research Lead View:
  name: "Research Overview"
  filters:
    category: "Research"
  sort: ["Priority", "Milestone"]
  columns: ["Backlog", "To Do", "In Progress", "Review", "Done"]

Development Lead View:
  name: "Development Overview"
  filters:
    category: "Development"
  sort: ["Priority", "Assignee"]
  columns: ["Backlog", "To Do", "In Progress", "Review", "Done"]

PI Dashboard:
  name: "Lab Overview"
  filters: []
  sort: ["Category", "Priority"]
  columns: ["Backlog", "To Do", "In Progress", "Review", "Done"]
```

#### Milestone Views
```yaml
Q1 2025 Milestone:
  name: "Q1 2025 Goals"
  filters:
    milestone: "Q1 2025"
  sort: ["Priority", "Deadline"]
  columns: ["To Do", "In Progress", "Review", "Done"]

Current Sprint:
  name: "Sprint 23"
  filters:
    deadline: "<= 2025-04-30"
  sort: ["Priority", "Category"]
  columns: ["To Do", "In Progress", "Review", "Done"]
```

### 4. Integration with Other Tools

#### Slack Integration
```python
# Slack bot for project updates
import slack
import github

class ProjectSlackBot:
    def __init__(self, slack_token, github_token):
        self.slack_client = slack.WebClient(token=slack_token)
        self.github_client = github.Github(github_token)
    
    def send_daily_summary(self):
        """Send daily project summary to Slack"""
        project = self.github_client.get_repo("research-lab/main").get_project(1)
        
        summary = {
            "completed": len([c for c in project.get_columns()[-1].get_cards()]),
            "in_progress": len([c for c in project.get_columns()[2].get_cards()]),
            "overdue": self.get_overdue_tasks(project)
        }
        
        message = f"""
        :clipboard: Daily Project Summary
        :white_check_mark: Completed: {summary['completed']}
        :construction: In Progress: {summary['in_progress']}
        :warning: Overdue: {summary['overdue']}
        """
        
        self.slack_client.chat_postMessage(
            channel="#project-updates",
            text=message
        )
    
    def notify_deadline_approaching(self, task, days_until):
        """Notify about approaching deadlines"""
        assignee = task.assignee
        message = f":alarm_clock: Hey @{assignee}, your task '{task.title}' is due in {days_until} days!"
        
        self.slack_client.chat_postMessage(
            channel=f"@{assignee}",
            text=message
        )
```

#### Calendar Integration
```python
# Google Calendar integration for deadlines
import google_calendar
import github

class DeadlineCalendar:
    def __init__(self, calendar_id, github_token):
        self.calendar = google_calendar.Calendar(calendar_id)
        self.github = github.Github(github_token)
    
    def sync_deadlines(self):
        """Sync project deadlines with Google Calendar"""
        project = self.github.get_repo("research-lab/main").get_project(1)
        
        for column in project.get_columns():
            for card in column.get_cards():
                if hasattr(card, 'deadline') and card.deadline:
                    event = {
                        'summary': f"Task: {card.title}",
                        'description': f"Assigned to: {card.assignee}\nPriority: {card.priority}",
                        'start': card.deadline,
                        'end': card.deadline
                    }
                    
                    self.calendar.create_event(event)
```

### 5. Reporting and Analytics

#### Progress Reports
```python
class ProjectAnalytics:
    def __init__(self, project_id):
        self.project = github.get_project(project_id)
    
    def generate_sprint_report(self, sprint_start, sprint_end):
        """Generate sprint progress report"""
        cards = self.get_cards_in_date_range(sprint_start, sprint_end)
        
        report = {
            "sprint_period": f"{sprint_start} to {sprint_end}",
            "total_tasks": len(cards),
            "completed_tasks": len([c for c in cards if c.status == "completed"]),
            "completion_rate": self.calculate_completion_rate(cards),
            "average_cycle_time": self.calculate_average_cycle_time(cards),
            "team_performance": self.get_team_performance(cards),
            "blocked_tasks": len([c for c in cards if c.status == "blocked"])
        }
        
        return report
    
    def get_team_workload(self):
        """Get current workload for each team member"""
        workload = {}
        
        for card in self.project.get_cards():
            assignee = card.assignee
            if assignee not in workload:
                workload[assignee] = {
                    "total_tasks": 0,
                    "in_progress": 0,
                    "estimated_hours": 0
                }
            
            workload[assignee]["total_tasks"] += 1
            if card.status == "in_progress":
                workload[assignee]["in_progress"] += 1
            workload[assignee]["estimated_hours"] += card.estimated_hours
        
        return workload
```

### 6. Best Practices

#### Card Management
- **Clear Titles**: Use action-oriented, specific titles
- **Detailed Descriptions**: Include context, requirements, and acceptance criteria
- **Proper Assignment**: Assign to specific person, not to "Anyone"
- **Realistic Estimates**: Use historical data for better estimates
- **Regular Updates**: Update status daily, not just at sprint boundaries

#### Board Maintenance
- **Weekly Cleanup**: Move completed items to Done column
- **Backlog Grooming**: Review and prioritize backlog items weekly
- **Column Limits**: Set WIP limits to prevent bottlenecks
- **Regular Reviews**: Monthly board structure review and optimization

#### Team Collaboration
- **Daily Standups**: Use board for daily progress updates
- **Sprint Planning**: Use board for sprint planning meetings
- **Retrospectives**: Use board data for sprint retrospectives
- **Stakeholder Updates**: Share board views with stakeholders

---

This GitHub Projects configuration provides a comprehensive project management system that integrates with GitHub issues and pull requests, automates workflows, and provides visibility into project progress across the research team.
