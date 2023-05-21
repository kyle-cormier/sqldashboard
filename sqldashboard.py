import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import psycopg2
import gunicorn


# Connect to the ElephantSQL database
url = "postgres://msydzjhv:bRRyUHzKCCwgLoP_lhECiyT1AoXwPBJ6@drona.db.elephantsql.com/msydzjhv"

connection = psycopg2.connect(url)

# Execute a query to retrieve data
cursor = connection.cursor()
cursor.execute("""
    SELECT
        name,
        SUM(singles) AS total_singles,
        SUM(doubles) AS total_doubles,
        SUM(triples) AS total_triples,
        SUM(home_runs) AS total_home_runs,
        SUM(walks) AS total_walks,
        SUM(at_bats) AS total_at_bats,
        SUM(runs) AS total_runs,
        SUM(rbis) AS total_rbis
    FROM statistics
    GROUP BY name
""")

aggregated_data = cursor.fetchall()

# Extract the player names
players = [row[0] for row in aggregated_data]

# Extract the aggregated sums
sums = {
    'singles': [row[1] for row in aggregated_data],
    'doubles': [row[2] for row in aggregated_data],
    'triples': [row[3] for row in aggregated_data],
    'home_runs': [row[4] for row in aggregated_data],
    'walks': [row[5] for row in aggregated_data],
    'at_bats': [row[6] for row in aggregated_data],
    'runs': [row[7] for row in aggregated_data],
    'rbis': [row[8] for row in aggregated_data]
}

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(id='player-dropdown',
                 options= [
                     {'label': 'Andrew Belleau', 'value': 'Andrew Belleau'},
                     {'label': 'Brad Lefave', 'value': 'Brad Lefave'},
                     {'label': 'Brant Farrell', 'value': 'Brant Farrell'},
                     {'label': 'Brett Macdonald', 'value': 'Brett Macdonald'},
                     {'label': 'Brit Johnson', 'value': 'Brit Johnson'},
                     {'label': 'Chelsea Frazier', 'value': 'Chelsea Frazier'},
                     {'label': 'Chris Parlow', 'value': 'Chris Parlow'},
                     {'label': 'Colleen Veronica', 'value': 'Colleen Veronica'},
                     {'label': 'Corey Lelievre', 'value': 'Corey Lelievre'},
                     {'label': 'Corinna Briglio', 'value': 'Corinna Briglio'},
                     {'label': 'Dalton Opper', 'value': 'Dalton Opper'},
                     {'label': 'Dustin Corbiere', 'value': 'Dustin Corbiere'},
                     {'label': 'Gabriel Tremblay', 'value': 'Gabriel Tremblay'},
                     {'label': 'Greg Lefave', 'value': 'Greg Lefave'},
                     {'label': 'Jamie Stadnisky', 'value': 'Jamie Stadnisky'},
                     {'label': 'Joe Lemieux', 'value': 'Joe Lemieux'},
                     {'label': 'Ken Griffey Jr.', 'value': 'Ken Griffey Jr.'},
                     {'label': 'Kerry Adams', 'value': 'Kerry Adams'},
                     {'label': 'Kyle Cormier', 'value': 'Kyle Cormier'},
                     {'label': 'Kyle Cormier Baseball', 'value': 'Kyle Cormier Baseball'},
                     {'label': 'Larry Johnson', 'value': 'Larry Johnson'},
                     {'label': 'Laura Perrault', 'value': 'Laura Perrault'},
                     {'label': 'Mark Golden', 'value': 'Mark Golden'},
                     {'label': 'Matthew Corbeil', 'value': 'Matthew Corbeil'},
                     {'label': 'Melissa Fulin', 'value': 'Melissa Fulin'},
                     {'label': 'Merrick Adams', 'value': 'Merrick Adams'},
                     {'label': 'Michelle Dear', 'value': 'Michelle Dear'},
                     {'label': 'Mike Allard', 'value': 'Mike Allard'},
                     {'label': 'Mike Piazza', 'value': 'Mike Piazza'},                    
                     {'label': 'Paul Adams', 'value': 'Paul Adams'},
                     {'label': 'Mikayla Jewel', 'value': 'Mikayla Jewel'},
                     {'label': 'Myles Macdonald', 'value': 'Myles Macdonald'},
                     {'label': 'Rob LaRue', 'value': 'Rob LaRue'},
                     {'label': 'Rob Steeves', 'value': 'Rob Steeves'},
                     {'label': 'Robbie Shuba', 'value': 'Robbie Shuba'},
                     {'label': 'Robbie Warren', 'value': 'Robbie Warren'},
                     {'label': 'Sam Nyman', 'value': 'Sam Nyman'},
                     {'label': 'Stephanie Peletz', 'value': 'Stephanie Peletz'},
                     {'label': 'Sarah Stewart', 'value': 'Sarah Stewart'},
                     {'label': 'Shelby Dayne', 'value': 'Shelby Dayne'},
                     {'label': 'Steve Johnson', 'value': 'Steve Johnson'},
                     {'label': 'Sydney Dawn', 'value': 'Sydney Dawn'},
                     {'label': 'Sylvan Tremblay', 'value': 'Sylvan Tremblay'},
                     {'label': 'Ty Dowding', 'value': 'Ty Dowding'},
                     
                 ],
                 placeholder='Select a Player',
                 searchable=False
    ),
    dcc.Graph(id='bar-graph')
])

@app.callback(
    dash.dependencies.Output('bar-graph', 'figure'),
    [dash.dependencies.Input('player-dropdown', 'value')]
)
def update_bar_graph(player):
    # Get the index of the selected player
    player_index = players.index(player)
    
    # Get the sums for the selected player
    player_sums = {key: sums[key][player_index] for key in sums}
    
    # Calculate batting average and on-base percentage
    at_bats = player_sums['at_bats']
    hits = player_sums['singles'] + player_sums['doubles'] + player_sums['triples'] + player_sums['home_runs']
    batting_average = hits / at_bats if at_bats > 0 else 0
    on_base_percentage = (hits + player_sums['walks']) / (at_bats + player_sums['walks']) if (at_bats + player_sums['walks']) > 0 else 0

    # Create bar chart
    bar_trace = go.Bar(x=list(player_sums.keys()), y=list(player_sums.values()), name='Stats')
    percentage_trace = go.Bar(x=['Batting Average', 'On-Base Percentage'], y=[batting_average * 1, on_base_percentage * 1], name= 'Percentages')
   
    figure = go.Figure(data=[bar_trace, percentage_trace])
          
    return figure

if __name__ == '__main__':
    app.server.run(debug=False, host="0.0.0.0", port=8080)