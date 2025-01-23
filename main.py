import argparse
from functools import reduce
from dataclasses import dataclass
from jira import JIRA

# Generate API token
# https://id.atlassian.com/manage-profile/security/api-tokens

# URL to your JIRA
JIRA_URL = "https://domain.atlassian.net"
# Custom field holding story points
STORY_POINTS_FIELD = "customfield_10014"
JIRA_PROJECT = "YOUR_PROJECT_NAME"


@dataclass
class MyTicket:
    name: str 
    storypoints: int

    def __init__(self, name: str, storypoints: int):
        self.name = name
        self.storypoints = storypoints

def get_tickets(jira_url, username, api_token, status):
    try:
        jira = JIRA(server=jira_url, basic_auth=(username, api_token))

        # JQL query to fetch issues for a specific project and sprint
        jql_query = (
            f'project = "{JIRA_PROJECT}" AND sprint in openSprints() AND status = "{status}" AND component = "iOS" AND issuetype NOT IN ("Epic", "Sub-task")'
        )
        
        # Fetch issues
        issues = jira.search_issues(jql_query, maxResults=10000)

        # Extract and return issue summaries
        tickets = []

        for issue in issues:
            story_points = getattr(issue.fields, STORY_POINTS_FIELD, 0)  # Get story points or None if not set
            ticket = MyTicket(name=issue.fields.summary, storypoints=story_points)
    
            if ticket.storypoints == None:
                ticket.storypoints = 0

            tickets.append(ticket)
        
        return tickets

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch 'In Progress' tickets from Jira.")
    parser.add_argument("--api_token", help="Your Jira API token")
    parser.add_argument("--email", help="Your Jira email")

    # Parse the arguments
    args = parser.parse_args()

    total_storypoints = 0

    for status in ["In To Do", "In Progress", "In Code Review", "In Testing", "Ready for Testing", "Done", "Blocked"]:
        tickets = get_tickets(JIRA_URL, args.email, args.api_token, status)

        sum = 0

        if tickets:
            print(f'{status} tickets:')
            for ticket in tickets:
                print(f"• {ticket.name}")
                sum += ticket.storypoints


            print(f'\n Total story points for {status}: {sum}')
        else:
            print(f'No {status} tickets found or an error occurred.')

        total_storypoints += sum

        print("-------------------------------------------------------------------")

    print(f'Total number of planned storypoints: {total_storypoints}')
