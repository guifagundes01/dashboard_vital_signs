import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import scipy.io
import dash_bootstrap_components as dbc
import random

mat = scipy.io.loadmat('data_matlab.mat')

first_names = [
    "Gabriel", "Miguel", "Arthur", "Heitor", "Bernardo", "Davi", "Lorenzo", "Théo", "Pedro", "Matheus",
    "Enzo", "Lucas", "Benjamin", "Nicolas", "Guilherme", "Rafael", "Joaquim", "Samuel", "Enzo Gabriel", "Henrique",
    "Lívia", "Alice", "Sophia", "Laura", "Isabella", "Manuela", "Luiza", "Helena", "Valentina", "Giovanna",
    "Maria Eduarda", "Beatriz", "Mariana", "Larissa", "Eloá", "Cecília", "Isadora", "Heloísa", "Yasmin", "Rafaela",
]

surnames = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida", "Nascimento", "Lima", "Araújo",
    "Pereira", "Carvalho", "Melo", "Ribeiro", "Costa", "Alves", "Barbosa", "Cavalcanti", "Campos", "Cardoso",
    "Rocha", "Dias", "Martins", "Gomes", "Monteiro", "Moura", "Nogueira", "Batista", "Teixeira", "Vieira"
]

# Gerar 1000 nomes completos
names = [f"{random.choice(first_names)} {random.choice(surnames)}" for _ in range(1000)]

start_time = pd.to_datetime('2023-07-10 00:00:00')
datetime_vector = pd.date_range(start=start_time, periods=1000, freq='20S')
time_vector = datetime_vector.to_list()

users = list(range(0, 1000))
data_dict = {user: {
    'time': time_vector,
    'heart_rate': mat['sens_freq'][:1000][user],
    'oxygen_level': 100 * mat['sens_oxi'][:1000][user],
    'body_temp': mat['sens_temp'][:1000][user],
    'acceleration': mat['sens_acce'][:1000][user],
    'age': mat['age'][0][user],
    'name': names[user],
    'history': mat['hist_cardVasc'][0][user]
} for user in users}

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Painel de Monitoramento de Sinais Vitais", style={'textAlign': 'center', 'marginBottom': '20px', 'color': 'white'}),

    html.Div(id='user-info-card', style={"width": "18rem", "marginBottom": "20px"}),

    dcc.Dropdown(
        id='user-dropdown',
        options=[{'label': f'{name}', 'value': user} for user, name in enumerate(names)],
        value=users[0],
        style={'marginBottom': '20px'}
    ),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='heart-rate-graph', animate=True, style={'height': '400px'}), width=12),
    ], style={'marginBottom': '20px'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='oxygen-level-graph', animate=True, style={'height': '400px'}), width=12),
    ], style={'marginBottom': '20px'}),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='body-temp-graph', animate=True, style={'height': '400px'}), width=12),
    ], style={'marginBottom': '20px'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='acceleration-graph', animate=True, style={'height': '400px'}), width=12),
    ], style={'marginBottom': '20px'}),
        
    # dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
], style={'padding': '20px', 'backgroundColor': '#1e2130', 'height': '100vh', 'overflowY': 'scroll'})

@app.callback(
    Output('user-info-card', 'children'),
    [Input('user-dropdown', 'value')]
)
def update_user_info(selected_user):
    user_data = data_dict[selected_user]
    history = 'Sim' if user_data['history'] == 1 else 'Não'
    user_info_card = dbc.Card(
        dbc.CardBody([
            html.H4("Informações do Usuário", className="card-title"),
            html.P(f"ID: {selected_user}", className="card-text"),
            html.P(f"Nome: {user_data['name']}", className="card-text"),
            html.P(f"Idade: {int(user_data['age'])}", className="card-text"),
            html.P(f"Histórico Cardiovascular: {history}", className="card-text"),
        ]),
        style={"width": "18rem", "marginBottom": "20px", 'backgroundColor': '#2e2e2e', 'color': 'white'}
    )
    return user_info_card

@app.callback([Output('heart-rate-graph', 'figure'),
               Output('oxygen-level-graph', 'figure'),
               Output('body-temp-graph', 'figure'),
               Output('acceleration-graph', 'figure'),],
            #   [Input('interval-component', 'n_intervals'),
            #    Input('user-dropdown', 'value')])
                [
               Input('user-dropdown', 'value')])
def update_graph_live(selected_user):
    user_data = data_dict[selected_user]

    data = pd.DataFrame({
        'time': user_data['time'],
        'heart_rate': user_data['heart_rate'],
        'oxygen_level': user_data['oxygen_level'],
        'body_temp': user_data['body_temp'],
        'acceleration': user_data['acceleration']
    })

    # Definir limites fixos de tempo e valores esperados
    x_range = [data['time'].min(), data['time'].max()]
    y_range_heart_rate = [45, 110]
    y_range_oxygen_level = [65, 100]
    y_range_body_temp = [34, 40]
    y_range_acceleration = [0, 1]

    # Função para identificar anomalias
    anomalies = {
        'heart_rate': (data['heart_rate'] > 100) | (data['heart_rate'] < 50),
        'oxygen_level': data['oxygen_level'] < 71,
        'body_temp': (data['body_temp'] > 39.3) | (data['body_temp'] < 34.5),
        'acceleration': data['acceleration'] == 1
    }


    # Gráfico de Frequência Cardíaca
    heart_rate_fig = go.Figure()
    heart_rate_fig.add_trace(go.Scatter(
        x=data['time'], y=data['heart_rate'], mode='lines+markers', name='Frequência Cardíaca',
        line=dict(color='blue'),
        marker=dict(color=np.where(anomalies['heart_rate'], 'red', 'blue'))
    ))
    heart_rate_fig.update_layout(title='Frequência Cardíaca', xaxis_title='Tempo', yaxis_title='BPM', xaxis=dict(range=x_range), yaxis=dict(range=y_range_heart_rate), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    # Gráfico de Nível de Oxigênio
    oxygen_level_fig = go.Figure()
    oxygen_level_fig.add_trace(go.Scatter(
        x=data['time'], y=data['oxygen_level'], mode='lines+markers', name='Nível de Oxigênio',
        line=dict(color='green'),
        marker=dict(color=np.where(anomalies['oxygen_level'], 'red', 'green'))
    ))
    oxygen_level_fig.update_layout(title='Nível de Oxigênio', xaxis_title='Tempo', yaxis_title='Porcentagem', xaxis=dict(range=x_range), yaxis=dict(range=y_range_oxygen_level), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    # Gráfico de Temperatura Corporal
    body_temp_fig = go.Figure()
    body_temp_fig.add_trace(go.Scatter(
        x=data['time'], y=data['body_temp'], mode='lines+markers', name='Temperatura Corporal',
        line=dict(color='yellow'),
        marker=dict(color=np.where(anomalies['body_temp'], 'red', 'yellow'))
    ))
    body_temp_fig.update_layout(title='Temperatura Corporal', xaxis_title='Tempo', yaxis_title='Celsius', xaxis=dict(range=x_range), yaxis=dict(range=y_range_body_temp), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    # Gráfico de Aceleração
    acceleration_fig = go.Figure()
    acceleration_fig.add_trace(go.Scatter(
        x=data['time'], y=data['acceleration'], mode='lines+markers', name='Aceleração',
        line=dict(color='orange'),
        marker=dict(color=np.where(anomalies['acceleration'], 'red', 'orange'))
    ))
    acceleration_fig.update_layout(title='Aceleração', xaxis_title='Tempo', yaxis_title='m/s^2', xaxis=dict(range=x_range), yaxis=dict(range=y_range_acceleration), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    return heart_rate_fig, oxygen_level_fig, body_temp_fig, acceleration_fig

if __name__ == '__main__':
    app.run_server(debug=True)